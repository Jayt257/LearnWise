"""
backend/scripts/mutation_checker.py
Native AST Mutation Engine for LearnWise backend.

Covers all logic-critical modules:
  1. app/services/scoring_service.py   — XP math & pass thresholds
  2. app/services/groq_service.py      — Feedback tier boundary logic
  3. app/core/security.py              — JWT decode & password verification
  4. app/services/content_service.py   — Path security & file existence guards
  5. app/core/dependencies.py          — Auth enforcement & admin role checks
  6. app/routers/progress.py           — XP accumulation & activity advancement

For each mutation:
  - Temporarily replaces a known logic expression with a logically-broken variant
  - Runs the isolated test suite via pytest
  - KILLED  → tests caught the injected bug  ✅
  - SURVIVED → gap in test logic             ❌
  - Original code is ALWAYS restored in a finally block (safe)
"""

import sys
import subprocess

# ──────────────────────────────────────────────────────────────────────────────
# MUTATION DEFINITIONS
# Format: (file_path, original_expression, mutated_expression, description)
# ──────────────────────────────────────────────────────────────────────────────

MUTATION_TARGETS = [
    # ─── 1. scoring_service.py — XP math ─────────────────────────────────────
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
        "per-question cap: division flipped to multiplication",
    ),

    # ─── 2. groq_service.py — Feedback tier boundaries ───────────────────────
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

    # ─── 3. security.py — Auth logic ─────────────────────────────────────────
    (
        "app/core/security.py",
        "return None",
        "return {}",
        "JWT error handler: None replaced with empty dict (truthy bypass)",
    ),

    # ─── 4. content_service.py — Path security & file guards ─────────────────
    (
        "app/services/content_service.py",
        "if len(parts) != 2:",
        "if len(parts) == 2:",
        "pair_id validation: != 2 flipped to == 2 (rejects all valid pair IDs)",
    ),
    (
        "app/services/content_service.py",
        "if not path.exists():\n        raise FileNotFoundError(f\"Activity file not found: {file_path}\")",
        "if path.exists():\n        raise FileNotFoundError(f\"Activity file not found: {file_path}\")",
        "activity existence check: raises for existing files, allows missing",
    ),
    (
        "app/services/content_service.py",
        "if not path.exists():\n        raise FileNotFoundError(f\"meta.json not found for pair: {pair_id}\")",
        "if path.exists():\n        raise FileNotFoundError(f\"meta.json not found for pair: {pair_id}\")",
        "meta existence check: raises for existing meta, allows missing meta",
    ),

    # ─── 5. dependencies.py — Auth enforcement & admin role ──────────────────
    (
        "app/core/dependencies.py",
        "if not payload:",
        "if payload:",
        "JWT payload check: not payload flipped (accepts bad tokens, rejects good)",
    ),
    (
        "app/core/dependencies.py",
        "if not credentials:",
        "if credentials:",
        "credential check: not credentials flipped (rejects when creds present)",
    ),
    (
        "app/core/dependencies.py",
        "if user.role != UserRole.admin:",
        "if user.role == UserRole.admin:",
        "admin role check: != flipped to == (grants admin to regular users)",
    ),

    # ─── 6. progress.py — Advancement & XP accumulation ─────────────────────
    (
        "app/routers/progress.py",
        "progress.current_activity_id + 1",
        "progress.current_activity_id - 1",
        "activity advancement: +1 flipped to -1 (moves backward not forward)",
    ),
    (
        "app/routers/progress.py",
        "if effective_passed and req.activity_seq_id == progress.current_activity_id:",
        "if effective_passed and req.activity_seq_id != progress.current_activity_id:",
        "advance condition: == flipped to != (advances the wrong activity)",
    ),
    (
        "app/routers/progress.py",
        "progress.total_xp += xp_delta",
        "progress.total_xp -= xp_delta",
        "XP accumulation: += flipped to -= (subtracts XP on completion)",
    ),
    (
        "app/routers/progress.py",
        "if req.score_earned > existing.score_earned:",
        "if req.score_earned < existing.score_earned:",
        "XP improvement check: > flipped to < (awards XP for getting worse)",
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
    "app/services/content_service.py": [
        "pytest", "tests/unit/services/test_content_service.py", "-q", "--tb=no", "-p", "no:cov"
    ],
    "app/core/dependencies.py": [
        "pytest", "tests/integration/api/test_auth.py",
        "tests/gui/test_gui_flows.py::TestAdminPanelGUI",
        "-q", "--tb=no", "-p", "no:cov"
    ],
    "app/routers/progress.py": [
        "pytest", "tests/integration/api/test_progress.py", "-q", "--tb=no", "-p", "no:cov"
    ],
}


def run_mutation_tests():
    print("╔══════════════════════════════════════════════════════╗")
    print("║        LearnWise Native Mutation Engine v2           ║")
    print("║  Coverage: scoring · groq · security · content      ║")
    print("║             dependencies · progress                  ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    total_killed = 0
    total_survived = 0
    by_file: dict[str, dict] = {}

    for (target_file, original, mutant, description) in MUTATION_TARGETS:
        if target_file not in by_file:
            by_file[target_file] = {"killed": 0, "survived": 0}

        test_cmd = TEST_COMMANDS.get(target_file, [
            "pytest", "tests/", "-q", "--tb=no", "-p", "no:cov"
        ])

        with open(target_file, "r") as f:
            original_code = f.read()

        if original not in original_code:
            print(f"  [SKIP] Pattern not found in {target_file}: {original[:60]!r}")
            continue

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

    return total_survived


if __name__ == "__main__":
    survivors = run_mutation_tests()
    sys.exit(1 if survivors > 0 else 0)
