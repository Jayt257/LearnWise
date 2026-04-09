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
        logger.warning(f"Whisper not available: {e}. Using mock transcription.")
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
        logger.warning("Whisper unavailable — returning mock transcription with is_mock=True")
        return {
            "text": "",
            "language": "unknown",
            "confidence": None,
            "is_mock": True,
        }

    try:
        import whisper

        # Write to temp file (Whisper needs a file path)
        suffix = os.path.splitext(filename)[-1] or ".webm"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            result = _whisper_model.transcribe(tmp_path, fp16=False)
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
                os.unlink(tmp_path)
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

    ext = os.path.splitext(filename)[-1] or ".webm"
    unique_name = f"{_uuid.uuid4().hex}{ext}"
    file_path = upload_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(audio_bytes)

    return f"/uploads/{pair_id}/{unique_name}"
