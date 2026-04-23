"""
backend/scripts/mutation_checker.py
Native AST Mutation Engine for LearnWise backend.

Covers all logic-critical modules:
  1. app/services/scoring_service.py   — XP math & pass thresholds
  2. app/services/groq_service.py      — Feedback tier boundary logic
  3. app/core/security.py              — JWT decode & password verification flow

For each mutation:
  - Temporarily replaces a known logic expression with a logically-broken variant
  - Runs the isolated test suite via pytest
  - If tests FAIL  → mutant KILLED (tests caught the bug) ✅
  - If tests PASS  → mutant SURVIVED (gap in test logic) ❌
  - Original code is ALWAYS restored in a finally block (safe)
"""

import sys
import subprocess

# ──────────────────────────────────────────────────────────────────────────────
# MUTATION DEFINITIONS
# Format: (file_path, original_expression, mutated_expression, description)
# ──────────────────────────────────────────────────────────────────────────────

MUTATION_TARGETS = [
    # ─── scoring_service.py — XP math ────────────────────────────────────────
    (
        "app/services/scoring_service.py",
        "total += clamped",
        "total -= clamped",
        "score accumulation: += flipped to -=",
    ),
    (
        "app/services/scoring_service.py",
        "percentage >= (PASS_THRESHOLD * 100)",
        "percentage > (PASS_THRESHOLD * 100)",
        "pass threshold: >= flipped to > (breaks 0% pass rule)",
    ),
    (
        "app/services/scoring_service.py",
        "clamped = max(0, min(int(raw_score), per_q_max))",
        "clamped = min(0, max(int(raw_score), per_q_max))",
        "score clamping: min/max swapped (always returns 0)",
    ),
    (
        "app/services/scoring_service.py",
        "total = min(total, max_xp)",
        "total = max(total, max_xp)",
        "final cap: min flipped to max (no upper bound on total)",
    ),
    (
        "app/services/scoring_service.py",
        "if max_xp == 0:",
        "if max_xp != 0:",
        "zero-XP guard: == flipped to != (inverts branch logic)",
    ),
    (
        "app/services/scoring_service.py",
        "per_question_xp if correct else 0",
        "per_question_xp if not correct else 0",
        "MCQ scoring: correct/wrong answer XP inverted",
    ),
    (
        "app/services/scoring_service.py",
        "percentage = round((total / max_xp) * 100, 1)",
        "percentage = round((total * max_xp) / 100, 1)",
        "percentage formula: division flipped to multiplication",
    ),
    (
        "app/services/scoring_service.py",
        "per_q_max = round(max_xp / num_q)",
        "per_q_max = round(max_xp * num_q)",
        "per-question cap: division flipped to multiplication (removes clamping)",
    ),

    # ─── groq_service.py — Feedback tier boundaries ──────────────────────────
    (
        "app/services/groq_service.py",
        "if percentage >= 80.0:",
        "if percentage >= 90.0:",
        "feedback tier: praise threshold raised from 80 to 90",
    ),
    (
        "app/services/groq_service.py",
        "elif percentage >= 50.0:",
        "elif percentage >= 60.0:",
        "feedback tier: lesson threshold raised from 50 to 60",
    ),
    (
        "app/services/groq_service.py",
        "return \"hint\" if attempt_count >= 2 else \"lesson\"",
        "return \"hint\" if attempt_count >= 1 else \"lesson\"",
        "hint threshold: >= 2 attempts flipped to >= 1 (hints too early)",
    ),

    # ─── security.py — Auth logic ─────────────────────────────────────────────
    (
        "app/core/security.py",
        "return None",
        "return {}",
        "JWT error handler: None replaced with empty dict (truthy — bypasses auth check)",
    ),
]

# ──────────────────────────────────────────────────────────────────────────────
# TEST RUNNERS per target file
# ──────────────────────────────────────────────────────────────────────────────
TEST_COMMANDS = {
    "app/services/scoring_service.py": [
        "pytest", "mutation_tests/test_scoring_service.py", "-q", "--tb=no", "-p", "no:cov"
    ],
    "app/services/groq_service.py": [
        "pytest", "tests/unit/services/test_groq_service.py", "-q", "--tb=no", "-p", "no:cov"
    ],
    "app/core/security.py": [
        "pytest", "tests/unit/core/test_core.py", "-q", "--tb=no", "-p", "no:cov"
    ],
}


def run_mutation_tests():
    print("╔══════════════════════════════════════════════════════╗")
    print("║        LearnWise Native Mutation Engine              ║")
    print("╚══════════════════════════════════════════════════════╝")

    total_killed = 0
    total_survived = 0
    by_file: dict[str, dict] = {}

    for (target_file, original, mutant, description) in MUTATION_TARGETS:
        # Track per-file stats
        if target_file not in by_file:
            by_file[target_file] = {"killed": 0, "survived": 0}

        test_cmd = TEST_COMMANDS.get(target_file, [
            "pytest", "mutation_tests/", "-q", "--tb=no", "-p", "no:cov"
        ])

        # Read original
        with open(target_file, "r") as f:
            original_code = f.read()

        if original not in original_code:
            print(f"  [SKIP] Pattern not found in {target_file}: {original[:50]}")
            continue

        # Apply mutation
        mutated_code = original_code.replace(original, mutant)
        with open(target_file, "w") as f:
            f.write(mutated_code)

        label = description[:55].ljust(55)
        sys.stdout.write(f"  [{target_file.split('/')[-1]:25s}] {label}  ")
        sys.stdout.flush()

        try:
            res = subprocess.run(test_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode != 0:
                print("✅ KILLED")
                total_killed += 1
                by_file[target_file]["killed"] += 1
            else:
                print("❌ SURVIVED")
                total_survived += 1
                by_file[target_file]["survived"] += 1
        finally:
            # ALWAYS restore original
            with open(target_file, "w") as f:
                f.write(original_code)

    total = total_killed + total_survived
    efficacy = round((total_killed / total) * 100, 1) if total > 0 else 0.0

    print("\n──────────────────────────────────────────────────────")
    print("   PER-FILE BREAKDOWN")
    print("──────────────────────────────────────────────────────")
    for filename, stats in by_file.items():
        k = stats["killed"]
        s = stats["survived"]
        t = k + s
        pct = round((k / t) * 100, 1) if t > 0 else 0
        status = "✅" if s == 0 else "❌"
        print(f"  {status}  {filename:45s}  {k}/{t} killed ({pct}%)")

    print("\n──────────────────────────────────────────────────────")
    print("   OVERALL MUTATION RESULTS SUMMARY")
    print("──────────────────────────────────────────────────────")
    print(f"  Total Evaluated : {total}")
    print(f"  Mutants Killed  : {total_killed}")
    print(f"  Mutants Survived: {total_survived}")
    print(f"  Efficacy Rate   : {efficacy}%")
    print("──────────────────────────────────────────────────────")


if __name__ == "__main__":
    run_mutation_tests()
