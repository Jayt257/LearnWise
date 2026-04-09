"""
backend/app/services/whisper_service.py
OpenAI Whisper integration for speech-to-text transcription.
Loads the model once on first use and reuses it for subsequent calls.
Falls back to a mock response if Whisper is not installed or ffmpeg is missing.

Key fixes to resolve "no speech detected" on real recordings:
  1. Explicit ffmpeg pre-conversion: webm/opus → 16kHz mono PCM WAV before
     feeding to Whisper. Whisper's internal ffmpeg decode of webm can silently
     produce silence on some OS/ffmpeg version combinations.
  2. no_speech_threshold raised 0.6 → 0.8: Whisper's default VAD is very
     aggressive — typical browser microphone recordings (which have background
     noise) were being filtered out entirely.
  3. logprob_threshold=None: Removes the minimum log-probability filter which
     also suppressed valid but uncertain transcriptions.
  4. condition_on_previous_text=False: Prevents hallucination loops on short
     audio clips.
  5. If ffmpeg is not available or conversion fails, falls back to raw Whisper
     decode (original behaviour).
"""

import logging
import os
import subprocess
import tempfile

logger = logging.getLogger(__name__)

_whisper_model = None
_whisper_available = None
_ffmpeg_available = None


def _check_ffmpeg() -> bool:
    global _ffmpeg_available
    if _ffmpeg_available is not None:
        return _ffmpeg_available
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, timeout=5
        )
        _ffmpeg_available = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        _ffmpeg_available = False
    logger.info(f"ffmpeg available: {_ffmpeg_available}")
    return _ffmpeg_available


def _load_model():
    global _whisper_model, _whisper_available
    if _whisper_available is not None:
        return _whisper_available

    try:
        import whisper
        from app.core.config import settings
        model_name = settings.WHISPER_MODEL  # "base"
        logger.info(f"Loading Whisper model: {model_name}")
        _whisper_model = whisper.load_model(model_name)
        _whisper_available = True
        logger.info("Whisper model loaded successfully")
    except Exception as e:
        logger.warning(f"Whisper not available: {e}. Using mock transcription.")
        _whisper_available = False

    return _whisper_available


def _convert_to_wav(audio_bytes: bytes, suffix: str) -> str | None:
    """
    Use ffmpeg to convert any audio format (webm, opus, mp3, m4a …) to
    16kHz mono PCM WAV that Whisper can reliably decode.

    Returns the path to the converted WAV, or None if ffmpeg is unavailable
    or conversion fails.
    """
    if not _check_ffmpeg():
        return None

    try:
        # Write input to temp file
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as inp:
            inp.write(audio_bytes)
            inp_path = inp.name

        # Output WAV path
        out_fd, out_path = tempfile.mkstemp(suffix=".wav")
        os.close(out_fd)

        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", inp_path,
                "-ar", "16000",   # 16kHz — Whisper's native sample rate
                "-ac", "1",       # mono
                "-acodec", "pcm_s16le",
                out_path,
            ],
            capture_output=True,
            timeout=30,
        )

        os.unlink(inp_path)

        if result.returncode != 0:
            err = result.stderr.decode(errors="replace")[-300:]
            logger.warning(f"ffmpeg conversion failed (exit {result.returncode}): {err}")
            try:
                os.unlink(out_path)
            except OSError:
                pass
            return None

        # Sanity-check: converted file should be > 1KB
        size = os.path.getsize(out_path)
        if size < 1000:
            logger.warning(f"ffmpeg produced tiny file ({size}B) — audio may be silent")
            os.unlink(out_path)
            return None

        logger.debug(f"ffmpeg converted → {out_path} ({size}B)")
        return out_path

    except Exception as e:
        logger.error(f"ffmpeg conversion error: {e}")
        return None


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> dict:
    """
    Transcribe audio bytes to text using Whisper.

    Args:
        audio_bytes: Raw audio file bytes (webm, wav, mp3, m4a)
        filename: Original filename to determine format

    Returns:
        {
            text: str,
            language: str,
            confidence: float | None,
            is_mock: bool   ← True when Whisper is unavailable
        }
    """
    available = _load_model()

    if not available:
        logger.warning("Whisper unavailable — returning mock transcription with is_mock=True")
        return {
            "text": "",
            "language": "unknown",
            "confidence": None,
            "is_mock": True,
        }

    try:
        import whisper  # noqa: already conditionally imported above

        suffix = os.path.splitext(filename)[-1] or ".webm"
        logger.info(f"Transcribing audio: {len(audio_bytes)}B, format: {suffix}")

        # Step 1: Try ffmpeg pre-conversion to 16kHz mono WAV
        wav_path = _convert_to_wav(audio_bytes, suffix)

        if wav_path:
            # Use the clean WAV
            input_path = wav_path
            logger.info(f"Using ffmpeg-converted WAV: {wav_path}")
        else:
            # Fallback: write raw bytes and let Whisper's internal ffmpeg handle it
            logger.warning("ffmpeg conversion skipped — using raw file for Whisper")
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_bytes)
                input_path = tmp.name

        try:
            result = _whisper_model.transcribe(
                input_path,
                fp16=False,
                # FIX: Raise VAD threshold — browser mic recordings have background
                # noise that pushes no_speech_prob above the default 0.6 threshold,
                # causing Whisper to silently drop the segment. 0.8 is more tolerant.
                no_speech_threshold=0.8,
                # FIX: Remove logprob filter — short recordings often score below
                # the default -1.0 threshold, suppressing valid transcriptions.
                logprob_threshold=None,
                # FIX: Prevent previous-context hallucination on short clips
                condition_on_previous_text=False,
            )

            text = result.get("text", "").strip()
            language = result.get("language", "unknown")
            segments = result.get("segments", [])

            # Log per-segment VAD info for debugging
            for seg in segments:
                nsp = seg.get("no_speech_prob", "?")
                logger.info(
                    f"Segment: {repr(seg['text'][:60])} | no_speech_prob: {nsp:.3f}"
                    if isinstance(nsp, float) else
                    f"Segment: {repr(seg['text'][:60])}"
                )

            if not text:
                logger.warning(
                    f"Whisper returned empty text. Segments: {len(segments)}. "
                    f"Audio: {len(audio_bytes)}B."
                )

            # Confidence: 1 - avg(no_speech_prob)
            avg_confidence = None
            if segments:
                avg_nsp = sum(s.get("no_speech_prob", 0.5) for s in segments) / len(segments)
                avg_confidence = round(1.0 - avg_nsp, 2)

            logger.info(f"Whisper result: {repr(text)} | lang={language} | conf={avg_confidence}")

            return {
                "text": text,
                "language": language,
                "confidence": avg_confidence,
                "is_mock": False,
            }

        finally:
            try:
                os.unlink(input_path)
            except OSError:
                pass

    except Exception as e:
        logger.error(f"Whisper transcription error: {e}", exc_info=True)
        return {
            "text": "",
            "language": "unknown",
            "confidence": 0.0,
            "is_mock": False,
        }


def save_audio_file(audio_bytes: bytes, filename: str, pair_id: str) -> str:
    """
    Save uploaded audio to backend/uploads/{pair_id}/ directory.
    Returns relative URL path.
    """
    from app.core.config import settings
    import uuid as _uuid
    from pathlib import Path

    upload_dir = Path(settings.data_path).parent / "uploads" / pair_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(filename)[-1] or ".webm"
    unique_name = f"{_uuid.uuid4().hex}{ext}"
    file_path = upload_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(audio_bytes)

    return f"/uploads/{pair_id}/{unique_name}"
