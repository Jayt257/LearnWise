"""
backend/app/services/whisper_service.py
OpenAI Whisper integration for speech-to-text transcription.
Loads the model once on first use and reuses it for subsequent calls.
Falls back to a mock response if Whisper is not installed or ffmpeg is missing.

Bug Fix #9: Mock now returns is_mock=True so the frontend can detect and
display a "Whisper unavailable — demo mode" warning instead of submitting
a garbage placeholder string as the user's spoken answer.
"""

import logging
import os
import tempfile
import subprocess

logger = logging.getLogger(__name__)

_whisper_model = None
_whisper_available = None


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
        logger.info(f"Whisper not available: {e}. Using mock transcription.")
        _whisper_available = False

    return _whisper_available


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
            is_mock: bool   ← True when Whisper is unavailable (Bug #9 fix)
        }
    """
    available = _load_model()

    if not available:
        # Bug Fix #9: Return is_mock=True so the frontend knows transcription
        # did not actually happen. The text is intentionally empty — the frontend
        # should block submission when is_mock is True.
        logger.info("Whisper unavailable — returning mock transcription with is_mock=True")
        return {
            "text": "",
            "language": "unknown",
            "confidence": None,
            "is_mock": True,
        }

    try:
        import whisper

        # Write incoming bytes to temp file
        suffix = os.path.splitext(filename)[-1] or ".webm"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_in:
            tmp_in.write(audio_bytes)
            in_path = tmp_in.name

        # Create output temp file for transcoded WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_out:
            out_path = tmp_out.name

        try:
            # Transcode explicitly to 16kHz 1-channel WAV via ffmpeg
            # This strips browser container corruption/chunk errors that cause Whisper to fail
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", in_path, 
                "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", 
                out_path
            ]
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            result = _whisper_model.transcribe(out_path, fp16=False)
            text = result.get("text", "").strip()
            language = result.get("language", "unknown")

            # Estimate confidence from segments if available
            segments = result.get("segments", [])
            avg_confidence = None
            if segments:
                avg_confidence = sum(
                    s.get("no_speech_prob", 0.5) for s in segments
                ) / len(segments)
                avg_confidence = round(1.0 - avg_confidence, 2)

            return {
                "text": text,
                "language": language,
                "confidence": avg_confidence,
                "is_mock": False,
            }
        finally:
            try:
                os.unlink(in_path)
            except OSError:
                pass
            try:
                os.unlink(out_path)
            except OSError:
                pass

    except Exception as e:
        logger.error(f"Whisper transcription error: {e}")
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

    # Force saving as WAV as requested by user
    unique_name = f"{_uuid.uuid4().hex}.wav"
    file_path = upload_dir / unique_name

    # We transcode it so the user receives a clean WAV file format
    suffix = os.path.splitext(filename)[-1] or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_in:
        tmp_in.write(audio_bytes)
        in_path = tmp_in.name
    
    try:
        # Transcode strictly to WAV
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", in_path, 
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", 
            str(file_path)
        ]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        # Fallback if ffmpeg fails: just write raw bytes even if its labeled .wav
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
    finally:
        try:
            os.unlink(in_path)
        except OSError:
            pass

    return f"/uploads/{pair_id}/{unique_name}"
