"""
backend/tests/test_speech.py
Tests for speech-to-text endpoint:
  POST /api/speech/transcribe
"""
import pytest
from io import BytesIO
from fastapi import UploadFile

def test_transcribe_unauthenticated(client):
    res = client.post("/api/speech/transcribe")
    assert res.status_code == 401

def test_transcribe_no_file(client, auth_headers):
    res = client.post("/api/speech/transcribe", headers=auth_headers)
    assert res.status_code == 422  # validation error for missing field

def test_transcribe_invalid_mime(client, auth_headers):
    # Try uploading a text file
    file_content = b"not an audio file"
    file = ("file", BytesIO(file_content), "text/plain")
    res = client.post("/api/speech/transcribe", files={"audio": file}, headers=auth_headers)
    
    assert res.status_code == 400
    assert "Unsupported audio format" in res.text

def test_transcribe_accepts_webm_opus(client, auth_headers):
    # Regression test for Bug #1: Ensure 'audio/webm;codecs=opus' is accepted
    file_content = b"fake webm data" * 10
    file = ("file", BytesIO(file_content), "audio/webm;codecs=opus")
    
    # We patch the actual whisper service to avoid needing ffmpeg in tests
    from unittest.mock import patch
    with patch("app.routers.speech.whisper_service.transcribe_audio") as mock_whisper:
        mock_whisper.return_value = {"text": "Hello world", "is_mock": True}
        
        res = client.post("/api/speech/transcribe", files={"audio": file}, headers=auth_headers)
        
        assert res.status_code == 200
        data = res.json()
        assert data["text"] == "Hello world"
        assert data["is_mock"] is True
