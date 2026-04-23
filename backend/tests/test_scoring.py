from app.services.scoring_service import calculate_score, score_mcq_locally
from app.schemas.activity import QuestionSubmission

def test_calculate_score():
    assert calculate_score([], 10, [{"score": 10}])["total_score"] == 10
    assert calculate_score([], 10, [{"score": 5}])["total_score"] == 5
    assert calculate_score([], 10, [{"score": 0}])["total_score"] == 0
    assert calculate_score([], 0, [{"score": 10}])["total_score"] == 0

def test_score_mcq_locally():
    q1 = QuestionSubmission(question_id="1", user_answer="A", correct_answer="A", block_type="test")
    q2 = QuestionSubmission(question_id="2", user_answer="C", correct_answer="B", block_type="test")
    
    # 2 questions, 10 XP max. 1 right. Score should be 5.
    res = score_mcq_locally([q1, q2], 10)
    assert res["total_score"] == 5

    # 1 question, right. Score should be 10.
    res_full = score_mcq_locally([q1], 10)
    assert res_full["total_score"] == 10
