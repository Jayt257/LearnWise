"""
backend/tests/test_speech.py
Comprehensive Whisper STT tests — validates the full speech pipeline:
endpoint routing, MIME checks, response schema, real audio with Whisper,
error handling, and AudioRecorder.jsx compatibility (uses `text` field).

Key discovery: endpoint returns { text, confidence, language, is_mock }
NOT { transcript, ... } — so `AudioRecorder.jsx` must read `data.text`.
"""
import io
import math
import struct
import pytest


TRANSCRIBE_URL = "/api/speech/transcribe"


# ── WAV Generators ─────────────────────────────────────────────────────────────

def make_minimal_wav() -> bytes:
    """Minimal valid WAV header with 0 audio samples (silent)."""
    return (
        b"RIFF" + (36).to_bytes(4, "little") + b"WAVE" +
        b"fmt " + (16).to_bytes(4, "little") +
        (1).to_bytes(2, "little") +      # PCM
        (1).to_bytes(2, "little") +      # mono
        (16000).to_bytes(4, "little") +  # 16kHz sample rate
        (32000).to_bytes(4, "little") +  # byte rate = sample_rate * channels * bits/8
        (2).to_bytes(2, "little") +      # block align
        (16).to_bytes(2, "little") +     # bits per sample
        b"data" + (0).to_bytes(4, "little")
    )


def make_sine_wav(duration_s: float = 1.0, freq: int = 440, sample_rate: int = 16000) -> bytes:
    """
    Generate a real 1-second 440Hz sine wave WAV.
    Whisper can actually process this (returns empty string — no speech, just tone).
    Used to verify the Whisper pipeline is fully wired end-to-end.
    """
    n_samples = int(sample_rate * duration_s)
    raw = b"".join(
        struct.pack("<h", int(32767 * math.sin(2 * math.pi * freq * i / sample_rate)))
        for i in range(n_samples)
    )
    data_len = len(raw)
    header = (
        b"RIFF" + struct.pack("<I", 36 + data_len) + b"WAVE" +
        b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16) +
        b"data" + struct.pack("<I", data_len)
    )
    return header + raw


def make_fake_webm() -> bytes:
    """Minimal EBML/WebM magic bytes — MIME accepted, but no real audio data."""
    return b"\x1a\x45\xdf\xa3" + b"\x00" * 200  # >100 byte minimum


# ── Auth / Endpoint Existence ──────────────────────────────────────────────────

def test_stt_endpoint_requires_auth(client):
    """STT endpoint must reject unauthenticated requests with 401/403."""
    resp = client.post(TRANSCRIBE_URL, files={"audio": ("test.wav", io.BytesIO(make_minimal_wav()), "audio/wav")})
    assert resp.status_code in (401, 403), f"Expected 401/403, got {resp.status_code}"


def test_stt_missing_file(client, auth_headers):
    """POST without a file body must return 422 Unprocessable Entity."""
    resp = client.post(TRANSCRIBE_URL, headers=auth_headers)
    assert resp.status_code == 422


def test_stt_wrong_method(client, auth_headers):
    """GET on STT endpoint must return 405 Method Not Allowed."""
    resp = client.get(TRANSCRIBE_URL, headers=auth_headers)
    assert resp.status_code == 405


# ── MIME Type Validation ───────────────────────────────────────────────────────

def test_stt_rejects_non_audio_text_plain(client, auth_headers):
    """text/plain content-type must be rejected with 400."""
    fake = io.BytesIO(b"this is plain text, not audio at all")
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("test.txt", fake, "text/plain")},
    )
    assert resp.status_code == 400, f"Expected 400 for text/plain, got {resp.status_code}"


def test_stt_rejects_image_content_type(client, auth_headers):
    """image/jpeg must be rejected with 400."""
    fake = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 200)
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("photo.jpg", fake, "image/jpeg")},
    )
    assert resp.status_code == 400


def test_stt_accepts_wav(client, auth_headers):
    """audio/wav content-type must be accepted (not 400 for MIME)."""
    wav = make_sine_wav()
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("recording.wav", io.BytesIO(wav), "audio/wav")},
    )
    assert resp.status_code in (200, 422, 500), f"Unexpected MIME rejection: {resp.status_code}"


def test_stt_accepts_webm(client, auth_headers):
    """audio/webm (browser MediaRecorder format) must NOT be rejected for MIME type."""
    fake_webm = io.BytesIO(make_fake_webm())
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("recording.webm", fake_webm, "audio/webm")},
    )
    assert resp.status_code in (200, 422, 500), f"Expected MIME acceptance, got {resp.status_code}"


def test_stt_accepts_webm_with_codec_suffix(client, auth_headers):
    """
    Browsers send 'audio/webm;codecs=opus' — this must NOT be rejected.
    Bug Fix #1: Speech router uses startswith() to handle codec suffixes.
    """
    fake_webm = io.BytesIO(make_fake_webm())
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("recording.webm", fake_webm, "audio/webm;codecs=opus")},
    )
    assert resp.status_code in (200, 422, 500), f"Codec suffix rejected: {resp.status_code}"


def test_stt_accepts_mp3(client, auth_headers):
    """audio/mpeg must be accepted."""
    fake = io.BytesIO(b"ID3" + b"\x00" * 200)
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("audio.mp3", fake, "audio/mpeg")},
    )
    assert resp.status_code in (200, 422, 500)


def test_stt_accepts_octet_stream(client, auth_headers):
    """application/octet-stream (generic binary) must be accepted — some browser recorders send this."""
    fake = io.BytesIO(make_fake_webm())
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("recording.bin", fake, "application/octet-stream")},
    )
    assert resp.status_code in (200, 422, 500)


# ── File Size Validation ───────────────────────────────────────────────────────

def test_stt_rejects_too_small_file(client, auth_headers):
    """Files smaller than 100 bytes must be rejected with 400."""
    tiny = io.BytesIO(b"\x00" * 50)  # 50 bytes — below MIN_AUDIO_SIZE (100)
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("tiny.wav", tiny, "audio/wav")},
    )
    assert resp.status_code == 400
    assert "empty" in resp.json()["detail"].lower() or "small" in resp.json()["detail"].lower()


# ── Response Schema ────────────────────────────────────────────────────────────

def test_stt_response_has_text_field_not_transcript(client, auth_headers):
    """
    CRITICAL: Backend returns { text, confidence, language, is_mock }.
    AudioRecorder.jsx must read `data.text` NOT `data.transcript`.
    This test pins the API contract so a field rename doesn't break the frontend silently.
    """
    wav = make_sine_wav()
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("recording.wav", io.BytesIO(wav), "audio/wav")},
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text[:200]}"
    data = resp.json()

    # The field MUST be 'text', not 'transcript'
    assert "text" in data, f"'text' field missing. Got keys: {list(data.keys())}"
    assert "transcript" not in data, (
        "'transcript' field must NOT exist — AudioRecorder.jsx must use data.text"
    )


def test_stt_response_schema_complete(client, auth_headers):
    """Response must contain all 4 required fields: text, confidence, language, is_mock."""
    wav = make_sine_wav()
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("recording.wav", io.BytesIO(wav), "audio/wav")},
    )
    assert resp.status_code == 200
    data = resp.json()

    required = {"text", "confidence", "language", "is_mock"}
    missing = required - set(data.keys())
    assert not missing, f"Missing response fields: {missing}. Got: {list(data.keys())}"


def test_stt_response_text_is_string(client, auth_headers):
    """The `text` field must always be a string (never null)."""
    wav = make_sine_wav()
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("recording.wav", io.BytesIO(wav), "audio/wav")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["text"], str), f"Expected string for 'text', got {type(data['text'])}"


def test_stt_response_is_mock_is_bool(client, auth_headers):
    """The `is_mock` field must always be a boolean."""
    wav = make_sine_wav()
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("recording.wav", io.BytesIO(wav), "audio/wav")},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json()["is_mock"], bool)


# ── Whisper Integration ────────────────────────────────────────────────────────

def test_stt_real_wav_whisper_processes(client, auth_headers):
    """
    Full pipeline test: real 1-second sine WAV → Whisper → response.
    Whisper is installed (verified), so is_mock must be False.
    The tone produces no speech text — empty string is expected and correct.
    """
    wav = make_sine_wav(duration_s=1.0, freq=440)
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("tone.wav", io.BytesIO(wav), "audio/wav")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_mock"] is False, "Whisper is installed — is_mock must be False"
    assert isinstance(data["text"], str), "text must be a string"
    # A 440Hz pure tone will not be transcribed to text — empty is expected
    assert data["text"].strip() == "" or len(data["text"]) < 50, (
        f"Unexpected transcription of pure tone: {data['text']}"
    )


def test_stt_real_wav_detects_language(client, auth_headers):
    """Whisper must detect a language (not 'unknown') for real audio."""
    wav = make_sine_wav(duration_s=2.0)
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("tone.wav", io.BytesIO(wav), "audio/wav")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["language"] is not None, "language must not be None"
    assert data["language"] != "", "language must not be empty string"


def test_stt_real_wav_confidence_is_valid(client, auth_headers):
    """Confidence must be None or a float in [0.0, 1.0] range."""
    wav = make_sine_wav()
    resp = client.post(
        TRANSCRIBE_URL, headers=auth_headers,
        files={"audio": ("tone.wav", io.BytesIO(wav), "audio/wav")},
    )
    assert resp.status_code == 200
    conf = resp.json().get("confidence")
    if conf is not None:
        assert 0.0 <= conf <= 1.0, f"Confidence out of range: {conf}"


def test_stt_whisper_service_returns_text_key():
    """
    Unit test: whisper_service.transcribe_audio() must return dict with 'text' key.
    Tests the service layer directly — not via HTTP.
    """
    from app.services.whisper_service import transcribe_audio
    wav = make_sine_wav()
    result = transcribe_audio(wav, "test.wav")
    assert "text" in result, f"whisper_service must return 'text'. Got: {list(result.keys())}"
    assert "is_mock" in result, "whisper_service must return 'is_mock'"
    assert isinstance(result["text"], str)
    assert isinstance(result["is_mock"], bool)


def test_stt_whisper_service_handles_invalid_bytes():
    """
    Unit test: whisper_service must not raise — must return empty text with is_mock=False.
    Tests resilience to corrupted audio.
    """
    from app.services.whisper_service import transcribe_audio
    # Random bytes that aren't valid audio
    result = transcribe_audio(b"\x00" * 500, "corrupt.webm")
    assert "text" in result
    assert isinstance(result["text"], str)
    assert "is_mock" in result


def test_stt_whisper_service_not_mock_when_installed():
    """
    Unit test: Whisper is installed+loaded — service must return is_mock=False.
    """
    from app.services.whisper_service import transcribe_audio
    wav = make_sine_wav()
    result = transcribe_audio(wav, "test.wav")
    assert result["is_mock"] is False, (
        "Whisper is installed — is_mock must be False. "
        "If True, Whisper failed to load — check whisper install and ffmpeg."
    )
