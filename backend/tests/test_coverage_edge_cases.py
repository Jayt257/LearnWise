import pytest
import os
from unittest.mock import patch, mock_open
from app.services import content_service
from app.services import whisper_service
from app.services import scoring_service
from app.services import groq_service

# --- CONTENT SERVICE ---

def test_content_service_invalid_pair_id():
    with pytest.raises(ValueError, match="Invalid pair_id"):
        content_service._base_path("invalidpair")

@patch("app.services.content_service.Path.exists", return_value=False)
def test_get_meta_file_not_found(mock_exists):
    with pytest.raises(FileNotFoundError):
        content_service.get_meta("en-es")

@patch("app.services.content_service.Path.exists", return_value=False)
def test_get_all_pairs_not_found(mock_exists):
    assert content_service.get_all_pairs() == []

@patch("app.services.content_service.Path.exists", return_value=False)
def test_list_pair_files_not_found(mock_exists):
    assert content_service.list_pair_files("en-es") == []

def test_extract_part_exception():
    # Force an exception by passing an object that lacks .split()
    assert content_service._extract_part(12345, "month") is None

@patch("app.services.content_service.get_meta")
def test_add_block_month_not_found(mock_get_meta):
    mock_get_meta.return_value = {"months": [{"month": 1}]}
    with pytest.raises(ValueError, match="Month 2 not found"):
        content_service.add_block("en-es", 2)

# --- WHISPER SERVICE ---

@patch.dict("sys.modules", {"whisper": None})
@patch("app.services.whisper_service._whisper_model", new=None)
@patch("app.services.whisper_service._whisper_available", new=None)
def test_whisper_service_load_failure():
    # This hits lines 30-35 exception handling safely without breaking __import__
    available = whisper_service._load_model()
    assert available is False

@patch("app.services.whisper_service._whisper_model")
@patch("app.services.whisper_service._whisper_available", new=True)
@patch("app.services.whisper_service.subprocess.run")
@patch("app.services.whisper_service.tempfile.NamedTemporaryFile")
@patch("app.services.whisper_service.os.unlink")
def test_whisper_service_transcribe_success(mock_unlink, mock_temp, mock_run, mock_model):
    # Hit lines 73-127
    mock_temp.return_value.__enter__.return_value.name = "dummy.wav"
    mock_model.transcribe.return_value = {
        "text": "test output",
        "language": "en",
        "segments": [{"no_speech_prob": 0.1}]
    }
    
    with patch("builtins.__import__"):
        res = whisper_service.transcribe_audio(b"some audio", "test.webm")
        assert res["text"] == "test output"
        assert res["confidence"] == 0.9

@patch("pathlib.Path.mkdir")
@patch("app.services.whisper_service.subprocess.run")
@patch("app.services.whisper_service.tempfile.NamedTemporaryFile")
@patch("app.services.whisper_service.os.unlink")
def test_whisper_service_save_audio_file(mock_unlink, mock_temp, mock_run, mock_mkdir):
    # Hit lines 140-175
    mock_temp.return_value.__enter__.return_value.name = "dummy.webm"
    res = whisper_service.save_audio_file(b"audio", "test.webm", "en-es")
    assert res.startswith("/uploads/en-es/")

import subprocess

@patch("pathlib.Path.mkdir")
@patch("app.services.whisper_service.subprocess.run", side_effect=subprocess.CalledProcessError(1, ["ffmpeg"]))
@patch("app.services.whisper_service.tempfile.NamedTemporaryFile")
@patch("builtins.open", new_callable=mock_open)
def test_whisper_service_save_audio_ffmpeg_fallback(mock_file, mock_temp, mock_run, mock_mkdir):
    # Hit fallback if ffmpeg fails
    res = whisper_service.save_audio_file(b"audio", "test.webm", "en-es")
    assert res.startswith("/uploads/en-es/")

# --- SCORING SERVICE ---

def test_scoring_service_calculate_score_zero_max_xp():
    from app.services.scoring_service import calculate_score
    res = calculate_score([], 0, [{"question_id": "1", "score": 10}])
    assert res["passed"] is True
    assert res["percentage"] == 100.0
    assert len(res["question_results"]) == 1

def test_scoring_service_raw_score_not_number():
    from app.services.scoring_service import calculate_score
    from app.schemas.activity import QuestionSubmission
    qs = [QuestionSubmission(question_id="1", block_type="lesson", user_answer="a", correct_answer="b")]
    res = calculate_score(qs, 100, [{"question_id": "1", "score": "ABC"}]) 
    assert res["total_score"] == 0

def test_scoring_service_score_mcq_locally_no_questions():
    from app.services.scoring_service import score_mcq_locally
    res = score_mcq_locally([], 100)
    assert res["total_score"] == 0

# --- GROQ SERVICE ---

@patch("app.services.groq_service.get_client")
def test_groq_service_generate_tier_feedback_api_error(mock_get_client):
    from groq import GroqError
    mock_client = mock_get_client.return_value
    mock_client.chat.completions.create.side_effect = GroqError("API offline")
    
    res = groq_service.generate_tier_feedback("lesson", "hint", "old_feedback", "old_suggestion", "hi", "en")
    assert res["overall_feedback"] == "old_feedback"
