from app.services.scoring_service import calculate_score, score_mcq_locally
from app.schemas.activity import QuestionSubmission

def test_calculate_score():
    res1 = calculate_score([], 10, [{"score": 10}])
    assert res1["total_score"] == 10
    assert res1["percentage"] == 100.0
    assert res1["passed"] is True

    res2 = calculate_score([], 10, [{"score": 5}])
    assert res2["total_score"] == 5
    assert res2["percentage"] == 50.0

    res3 = calculate_score([], 10, [{"score": 0}])
    assert res3["total_score"] == 0
    assert res3["percentage"] == 0.0
    assert res3["passed"] is True  # Fails if >= mutated to > when PASS_THRESHOLD is 0

    res4 = calculate_score([], 0, [{"score": 10}])
    assert res4["total_score"] == 0
    assert res4["percentage"] == 100.0

    # Kill: per_q_max = round(max_xp * num_q)
    # Original max_xp=10, num_q=2 => per_q_max=5. Mutated per_q_max=20.
    res5 = calculate_score([], 10, [{"score": 10}, {"score": 0}])
    assert res5["total_score"] == 5  # Ensure 10 is clamped to 5
    assert res5["percentage"] == 50.0

def test_score_mcq_locally():
    q1 = QuestionSubmission(question_id="1", user_answer="A", correct_answer="A", block_type="test")
    q2 = QuestionSubmission(question_id="2", user_answer="C", correct_answer="B", block_type="test")
    
    # 2 questions, 10 XP max. 1 right. Score should be 5.
    res = score_mcq_locally([q1, q2], 10)
    assert res["total_score"] == 5

    # 1 question, right. Score should be 10.
    res_full = score_mcq_locally([q1], 10)
    assert res_full["total_score"] == 10
