import os
import sys
import subprocess
import shutil

TARGET_FILE = "app/services/scoring_service.py"
TEST_RUNNER = ["pytest", "mutation_tests/test_scoring_service.py", "-q", "--tb=no"]

MUTATIONS = [
    ("total += clamped", "total -= clamped"),
    ("percentage >= (PASS_THRESHOLD * 100)", "percentage > (PASS_THRESHOLD * 100)"),
    ("clamped = max(0, min(int(raw_score), per_q_max))", "clamped = min(0, max(int(raw_score), per_q_max))"),
    ("total = min(total, max_xp)", "total = max(total, max_xp)"),
    ("if max_xp == 0:", "if max_xp != 0:"),
    ("per_question_xp if correct else 0", "per_question_xp if not correct else 0"),
    ("percentage = round((total / max_xp) * 100, 1)", "percentage = round((total * max_xp) / 100, 1)"),
    ("per_q_max = round(max_xp / num_q)", "per_q_max = round(max_xp * num_q)")
]

def run_mutation_tests():
    print(f"--- Native Mutation Engine ---")
    print(f"Target: {TARGET_FILE}")
    print(f"Test suite bounds: {len(MUTATIONS)} logical vectors.\n")
    
    with open(TARGET_FILE, "r") as f:
        original_code = f.read()

    killed = 0
    survived = 0

    try:
        for i, (orig, mut) in enumerate(MUTATIONS):
            if orig not in original_code:
                print(f"  [ERROR] Cannot find target code for Mutation #{i+1}")
                continue
                
            mutated_code = original_code.replace(orig, mut)
            with open(TARGET_FILE, "w") as f:
                f.write(mutated_code)
                
            sys.stdout.write(f"Evaluating Mutant #{i+1} : {mut[:40]}... ")
            sys.stdout.flush()
            
            # Run test
            res = subprocess.run(TEST_RUNNER, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if res.returncode != 0:
                print("KILLED (Caught by Tests)")
                killed += 1
            else:
                print("SURVIVED (Warning!)")
                survived += 1
                
    finally:
        # ALWAYS restore the original code
        with open(TARGET_FILE, "w") as f:
            f.write(original_code)

    print("\n=== MUTATION RESULTS SUMMARY ===")
    print(f"Total Evaluated : {killed + survived}")
    print(f"Mutants Killed  : {killed}")
    print(f"Mutants Survived: {survived}")
    print(f"Efficacy Rate   : {round((killed / (killed+survived))*100, 1)}%")

if __name__ == "__main__":
    run_mutation_tests()
