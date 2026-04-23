"""
tests/test_100_coverage.py
Targeted tests to cover every remaining uncovered line and reach 100% backend coverage.
Covers:
  - app/routers/progress.py  lines 56, 97, 138-146, 161-169
  - app/routers/speech.py    lines 39, 80
  - app/routers/users.py     line 91
  - app/routers/validate.py  lines 87-88
  - app/schemas/activity.py  lines 34, 44, 62, 71
  - app/schemas/auth.py      lines 24, 26, 33
  - app/services/groq_service.py  lines 319-320
  - app/services/whisper_service.py  lines 30-35, 118-119, 122-123
"""
import io
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import pydantic

# ─────────────────────────────────────────────────────────────────────────────
# SCHEMAS — validate field validators (no HTTP needed)
# ─────────────────────────────────────────────────────────────────────────────

class TestAuthSchema:
    """app/schemas/auth.py lines 24, 26, 33"""

    def test_username_too_short(self):
        from app.schemas.auth import RegisterRequest
        with pytest.raises(pydantic.ValidationError, match="3-50 characters"):
            RegisterRequest(username="ab", email="x@x.com", password="Secure@123")

    def test_username_too_long(self):
        from app.schemas.auth import RegisterRequest
        with pytest.raises(pydantic.ValidationError, match="3-50 characters"):
            RegisterRequest(username="a" * 51, email="x@x.com", password="Secure@123")

    def test_username_invalid_chars(self):
        from app.schemas.auth import RegisterRequest
        with pytest.raises(pydantic.ValidationError, match="letters, numbers, underscores"):
            RegisterRequest(username="bad name!", email="x@x.com", password="Secure@123")

    def test_password_too_short(self):
        from app.schemas.auth import RegisterRequest
        with pytest.raises(pydantic.ValidationError, match="8 characters"):
            RegisterRequest(username="validuser", email="x@x.com", password="short")


class TestActivitySchema:
    """app/schemas/activity.py lines 34, 44, 62, 71"""

    def test_answer_too_long(self):
        from app.schemas.activity import QuestionSubmission
        with pytest.raises(pydantic.ValidationError, match="too long"):
            QuestionSubmission(
                question_id="q1",
                block_type="writing",
                user_answer="x" * 2001,
            )

    def test_prompt_too_long(self):
        from app.schemas.activity import QuestionSubmission
        with pytest.raises(pydantic.ValidationError):
            QuestionSubmission(
                question_id="q1",
                block_type="writing",
                user_answer="ok",
                prompt="p" * 2001,
            )

    def test_too_many_questions(self):
        from app.schemas.activity import ValidateRequest, QuestionSubmission
        questions = [
            QuestionSubmission(question_id=str(i), block_type="quiz", user_answer="a")
            for i in range(51)
        ]
        with pytest.raises(pydantic.ValidationError, match="Too many questions"):
            ValidateRequest(
                activity_id=1,
                activity_type="test",
                lang_pair_id="hi-en",
                max_xp=100,
                questions=questions,
            )

    def test_negative_max_xp(self):
        from app.schemas.activity import ValidateRequest, QuestionSubmission
        with pytest.raises(pydantic.ValidationError, match="cannot be negative"):
            ValidateRequest(
                activity_id=1,
                activity_type="lesson",
                lang_pair_id="hi-en",
                max_xp=-1,
                questions=[QuestionSubmission(question_id="q1", block_type="quiz", user_answer="a")],
            )


# ─────────────────────────────────────────────────────────────────────────────
# PROGRESS ROUTER – use existing fixtures (client, auth_headers)
# ─────────────────────────────────────────────────────────────────────────────

class TestProgressRouterCoverage:
    """Covers progress.py lines 56, 97, 138-146, 161-163, 169"""

    def test_get_pair_progress_not_found(self, client, auth_headers):
        """Line 56 — 404 when pair not started"""
        resp = client.get("/api/progress/nonexistent-pair", headers=auth_headers)
        assert resp.status_code == 404

    def test_derive_month_block_with_zero(self, client, auth_headers):
        """Line 97 — activity_seq_id < 1 is clamped to 1"""
        resp = client.post(
            "/api/progress/hi-en/complete",
            headers=auth_headers,
            json={
                "activity_seq_id": 0,
                "lang_pair_id": "hi-en",
                "activity_type": "lesson",
                "score_earned": 50,
                "max_score": 100,
                "passed": True,
            },
        )
        assert resp.status_code in (200, 201)

    def test_complete_creates_new_progress_record(self, client, auth_headers):
        """Lines 138-146 — complete without starting first (auto-creates progress)"""
        resp = client.post(
            "/api/progress/brand-new-pair/complete",
            headers=auth_headers,
            json={
                "activity_seq_id": 1,
                "lang_pair_id": "brand-new-pair",
                "activity_type": "vocab",
                "score_earned": 80,
                "max_score": 100,
                "passed": True,
            },
        )
        assert resp.status_code == 200

    def test_complete_existing_with_score_improvement(self, client, auth_headers):
        """Lines 161-163 — second attempt with higher score awards XP delta"""
        pair = "score-improve-pair"
        client.post(
            f"/api/progress/{pair}/complete",
            headers=auth_headers,
            json={
                "activity_seq_id": 5,
                "lang_pair_id": pair,
                "activity_type": "lesson",
                "score_earned": 40,
                "max_score": 100,
                "passed": True,
            },
        )
        resp = client.post(
            f"/api/progress/{pair}/complete",
            headers=auth_headers,
            json={
                "activity_seq_id": 5,
                "lang_pair_id": pair,
                "activity_type": "lesson",
                "score_earned": 90,
                "max_score": 100,
                "passed": True,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["score_earned"] == 90

    def test_complete_with_activity_json_id_update(self, client, auth_headers):
        """Line 169 — activity_json_id updated on second attempt"""
        pair = "json-id-update-pair"
        client.post(
            f"/api/progress/{pair}/complete",
            headers=auth_headers,
            json={
                "activity_seq_id": 10,
                "lang_pair_id": pair,
                "activity_type": "lesson",
                "score_earned": 30,
                "max_score": 100,
                "passed": True,
                "activity_json_id": "act_old",
            },
        )
        resp = client.post(
            f"/api/progress/{pair}/complete",
            headers=auth_headers,
            json={
                "activity_seq_id": 10,
                "lang_pair_id": pair,
                "activity_type": "lesson",
                "score_earned": 50,
                "max_score": 100,
                "passed": True,
                "activity_json_id": "act_new",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["activity_json_id"] == "act_new"


# ─────────────────────────────────────────────────────────────────────────────
# SPEECH ROUTER – covers lines 39, 80
# ─────────────────────────────────────────────────────────────────────────────

class TestSpeechRouterCoverage:
    """app/routers/speech.py lines 39, 80"""

    def test_is_allowed_audio_missing_content_type(self):
        """Line 39 — empty content_type returns True (allow through)"""
        from app.routers.speech import _is_allowed_audio
        assert _is_allowed_audio("") is True
        assert _is_allowed_audio(None) is True

    def test_audio_too_large(self, client, auth_headers):
        """Line 80 — 413 when audio exceeds 25MB"""
        # 26MB of zeros to trigger size check
        large_audio = b"\x00" * (26 * 1024 * 1024)
        resp = client.post(
            "/api/speech/transcribe",
            headers=auth_headers,
            files={"audio": ("big.webm", io.BytesIO(large_audio), "audio/webm")},
        )
        assert resp.status_code == 413


# ─────────────────────────────────────────────────────────────────────────────
# USERS ROUTER – covers line 91
# ─────────────────────────────────────────────────────────────────────────────

class TestUsersRouterCoverage:
    """app/routers/users.py line 91"""

    def test_get_user_progress_not_found(self, client, auth_headers):
        """Line 91 — 404 when user not found in get_user_progress_public"""
        # Random UUID — guaranteed not in DB
        resp = client.get(
            "/api/users/00000000-0000-0000-0000-000000000099/progress",
            headers=auth_headers,
        )
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATE ROUTER – covers lines 87-88 (exception in generate_tier_feedback)
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateRouterCoverage:
    """app/routers/validate.py lines 87-88"""

    def test_validate_tier_feedback_exception_swallowed(self, client, auth_headers):
        """Lines 87-88 — if generate_tier_feedback raises, we silently continue"""
        payload = {
            "activity_id": 1,
            "activity_type": "lesson",
            "lang_pair_id": "hi-en",
            "max_xp": 100,
            "attempt_count": 5,  # forces non-lesson tier
            "questions": [
                {
                    "question_id": "q1",
                    "block_type": "fill_blank",
                    "user_answer": "hello",
                    "correct_answer": "hello",
                }
            ],
        }
        with patch("app.routers.validate.groq_service.generate_tier_feedback",
                   side_effect=Exception("API timeout")):
            resp = client.post("/api/validate", headers=auth_headers, json=payload)
        # Must succeed even when tier feedback fails
        assert resp.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# GROQ SERVICE – covers lines 319-320 (generate_tier_feedback success path)
# ─────────────────────────────────────────────────────────────────────────────

class TestGroqServiceCoverage:
    """app/services/groq_service.py lines 319-320"""

    def test_generate_tier_feedback_success_path(self):
        """Lines 319-320 — ensure response.choices[0].message.content path is hit"""
        from app.services import groq_service

        mock_choice = MagicMock()
        mock_choice.message.content = '{"overall_feedback": "Great!", "suggestion": "Keep going!"}'
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        # Patch get_client (the actual function name in the module)
        with patch("app.services.groq_service.get_client", return_value=mock_client):
            result = groq_service.generate_tier_feedback(
                activity_type="lesson",
                feedback_tier="praise",
                overall_feedback="Nice work!",
                suggestion="Try harder topics.",
                user_lang="hi",
                target_lang="en",
            )
        assert result.get("overall_feedback") == "Great!"


# ─────────────────────────────────────────────────────────────────────────────
# WHISPER SERVICE – covers lines 30-35, 118-119, 122-123
# ─────────────────────────────────────────────────────────────────────────────

class TestWhisperServiceCoverage:
    """app/services/whisper_service.py lines 30-35, 118-119, 122-123"""

    def test_load_model_success_path(self):
        """Lines 30-35 — whisper import succeeds and model is loaded"""
        import app.services.whisper_service as ws
        original_available = ws._whisper_available
        original_model = ws._whisper_model
        ws._whisper_available = None
        ws._whisper_model = None

        mock_whisper = MagicMock()
        mock_whisper.load_model.return_value = MagicMock()

        try:
            # settings is imported inside the try block in _load_model,
            # so we patch it at its source module
            with patch.dict("sys.modules", {"whisper": mock_whisper}), \
                 patch("app.core.config.settings") as mock_settings:
                mock_settings.WHISPER_MODEL = "base"
                result = ws._load_model()
            assert result is True
        finally:
            ws._whisper_available = original_available
            ws._whisper_model = original_model

    def test_unlink_oserror_swallowed(self):
        """Lines 118-119, 122-123 — OSError during temp file cleanup is silently swallowed.

        Root cause why whisper is patched here too:
        transcribe_audio() does `import whisper` at the top of its own try block (line 74).
        Without patching sys.modules, whisper ImportError is caught by the *outer*
        except Exception which returns early — the finally cleanup block is never reached.
        Patching sys.modules ensures `import whisper` succeeds and the code path
        reaches the finally block where os.unlink raises OSError.
        """
        import sys
        import app.services.whisper_service as ws
        original_available = ws._whisper_available
        original_model = ws._whisper_model

        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "hello",
            "language": "en",
            "segments": [],
        }
        ws._whisper_available = True
        ws._whisper_model = mock_model

        try:
            with patch.dict("sys.modules", {"whisper": mock_whisper}), \
                 patch("app.services.whisper_service.subprocess.run"), \
                 patch("app.services.whisper_service.os.unlink",
                       side_effect=OSError("busy")):
                result = ws.transcribe_audio(b"\x00" * 200, "test.webm")
            # Despite OSError on cleanup, function returns result
            assert "text" in result
        finally:
            ws._whisper_available = original_available
            ws._whisper_model = original_model

