import pytest
from app.services.scoring_service import calculate_score, score_mcq_locally
from app.schemas.activity import QuestionSubmission

def test_calculate_score_zero_max_xp():
    res = calculate_score([], 0, [{"question_id": "1", "score": 10}])
    assert res["passed"] is True
    assert res["percentage"] == 100.0

def test_calculate_score_raw_score_not_number():
    qs = [QuestionSubmission(question_id="1", block_type="lesson", user_answer="a", correct_answer="b")]
    res = calculate_score(qs, 100, [{"question_id": "1", "score": "ABC"}]) 
    assert res["total_score"] == 0
    assert res["passed"] is True

def test_calculate_score_normal():
    qs = [QuestionSubmission(question_id="1", block_type="lesson", user_answer="a", correct_answer="b")]
    res = calculate_score(qs, 100, [{"question_id": "1", "score": 100, "correct": True}])
    assert res["total_score"] == 100
    assert res["passed"] is True
    assert res["percentage"] == 100.0

def test_score_mcq_locally_no_questions():
    res = score_mcq_locally([], 100)
    assert res["total_score"] == 0

def test_score_mcq_locally_correct():
    qs = [QuestionSubmission(question_id="1", block_type="lesson", user_answer="A", correct_answer="A")]
    res = score_mcq_locally(qs, 100)
    assert res["total_score"] == 100
    assert res["passed"] is True

def test_score_mcq_locally_incorrect():
    qs = [QuestionSubmission(question_id="1", block_type="lesson", user_answer="B", correct_answer="A")]
    res = score_mcq_locally(qs, 100)
    assert res["total_score"] == 0
    assert res["passed"] is True
