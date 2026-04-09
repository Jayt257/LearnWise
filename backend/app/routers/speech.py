"""
backend/app/routers/speech.py
Speech-to-text endpoint using Whisper.
  POST /api/speech/transcribe  - Upload audio, get text transcription

Bug Fix #1: MIME type check now uses startswith() — browsers send
'audio/webm;codecs=opus' which previously caused a 400 rejection.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.activity import TranscribeResponse
from app.services import whisper_service

router = APIRouter(prefix="/speech", tags=["Speech"])

MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25 MB
MIN_AUDIO_SIZE = 100                # 100 bytes — anything smaller is not real audio

# Allowed MIME prefixes — use startswith() to handle codec suffixes like
# 'audio/webm;codecs=opus', 'audio/mpeg; charset=utf-8', etc.
ALLOWED_MIME_PREFIXES = (
    "audio/webm",
    "audio/wav",
    "audio/mpeg",
    "audio/mp4",
    "audio/ogg",
    "audio/x-m4a",
    "audio/m4a",
    "audio/flac",
    "application/octet-stream",  # Some recorders send generic binary
)


def _is_allowed_audio(content_type: str) -> bool:
    """Check if the content type is an allowed audio format."""
    if not content_type:
        return True  # Allow missing content-type (treat as webm)
    ct_lower = content_type.lower().strip()
    return any(ct_lower.startswith(prefix) for prefix in ALLOWED_MIME_PREFIXES)


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    audio: UploadFile = File(..., description="Audio file (webm, wav, mp3, m4a)"),
    current_user: User = Depends(get_current_user),
) -> TranscribeResponse:
    """
    Transcribe audio file to text using Whisper.
    Used by speaking, pronunciation, and vocab activities.

    Returns:
      - text: transcribed string
      - confidence: float 0–1 (None if Whisper unavailable)
      - language: detected language code
      - is_mock: True when Whisper is not installed (dev fallback)
    """
    # --- MIME type validation (Bug #1 fix: use startswith) ---
    content_type = audio.content_type or ""
    if content_type and not _is_allowed_audio(content_type):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported audio format: '{content_type}'. "
                "Accepted formats: webm, wav, mp3, mp4, ogg, m4a."
            ),
        )

    # --- Read audio bytes ---
    audio_bytes = await audio.read()

    if len(audio_bytes) < MIN_AUDIO_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Audio file is empty or too small. Please record at least 1 second of audio.",
        )

    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file too large ({len(audio_bytes) // (1024*1024)}MB). Maximum allowed size is 25MB.",
        )

    filename = audio.filename or "audio.webm"

    result = whisper_service.transcribe_audio(audio_bytes, filename)

    return TranscribeResponse(
        text=result["text"],
        confidence=result.get("confidence"),
        language=result.get("language"),
        is_mock=result.get("is_mock", False),
    )
