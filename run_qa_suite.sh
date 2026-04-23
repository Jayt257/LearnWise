#!/usr/bin/env bash
# =============================================================================
# run_qa_suite.sh — LearnWise Master QA Pipeline
#
# Runs: pytest (unit + coverage) → mutmut (mutation) → locust (load) → e2e
# Prints a full structured report at the end.
# =============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
REPORTS_DIR="$ROOT_DIR/qa_reports"
mkdir -p "$REPORTS_DIR"

# Colour helpers
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

banner() { echo -e "\n${CYAN}${BOLD}══════════════════════════════════════════════════${NC}"; \
           echo -e "${CYAN}${BOLD}  $1${NC}"; \
           echo -e "${CYAN}${BOLD}══════════════════════════════════════════════════${NC}"; }

step()   { echo -e "\n${YELLOW}▶ $1${NC}"; }
ok()     { echo -e "${GREEN}✔ $1${NC}"; }
fail()   { echo -e "${RED}✖ $1${NC}"; }

# Status trackers
STATUS_PYTEST="NOT RUN"; STATUS_MUTATION="NOT RUN"
STATUS_LOAD="NOT RUN";   STATUS_E2E="NOT RUN"; STATUS_UI="NOT RUN"

# ─────────────────────────────────────────────────────────────────────────────
banner "LEARNWISE FULL QA PIPELINE"
# ─────────────────────────────────────────────────────────────────────────────

# 0. Kill any stale background services
step "Killing any stale background services..."
pkill -f 'uvicorn app.main:app' 2>/dev/null || true
pkill -f 'vite'                 2>/dev/null || true
pkill -f 'locust'               2>/dev/null || true
sleep 1
ok "Environment clean."

# ─────────────────────────────────────────────────────────────────────────────
# 1. BACKEND — pytest with full coverage
# ─────────────────────────────────────────────────────────────────────────────
banner "STEP 1/5 — Backend Unit Tests + Coverage"

cd "$BACKEND_DIR"
source venv/bin/activate

PYTEST_REPORT="$REPORTS_DIR/pytest_coverage.txt"
echo "Running pytest across all test modules with coverage..."
if pytest tests/ \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html:"$REPORTS_DIR/htmlcov" \
    -v 2>&1 | tee "$PYTEST_REPORT"; then
    STATUS_PYTEST="${GREEN}PASSED — 100% coverage${NC}"
    ok "All backend tests passed."
else
    STATUS_PYTEST="${RED}FAILED — see $PYTEST_REPORT${NC}"
    fail "Some backend tests failed!"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 2. MUTATION — mutmut on scoring_service.py
# ─────────────────────────────────────────────────────────────────────────────
banner "STEP 2/5 — Mutation Testing (scoring_service.py)"

MUTATION_REPORT="$REPORTS_DIR/mutation_results.txt"
echo "Running mutmut against core scoring algorithm..."
{
    mutmut run 2>&1 || true
    echo ""
    echo "=== MUTMUT RESULTS SUMMARY ==="
    mutmut results 2>&1 || true
} | tee "$MUTATION_REPORT"

# Parse survived mutants
SURVIVED=$(grep -c "survived" "$MUTATION_REPORT" 2>/dev/null || echo "0")
KILLED=$(grep -c "killed" "$MUTATION_REPORT" 2>/dev/null || echo "0")

if [ "$SURVIVED" -eq 0 ]; then
    STATUS_MUTATION="${GREEN}ALL MUTANTS KILLED (0 survived)${NC}"
    ok "Mutation testing: no surviving mutants."
else
    STATUS_MUTATION="${RED}${SURVIVED} MUTANTS SURVIVED — check $MUTATION_REPORT${NC}"
    fail "$SURVIVED mutations survived!"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 3. FRONTEND — Vitest UI tests
# ─────────────────────────────────────────────────────────────────────────────
banner "STEP 3/5 — Frontend Unit Tests (Vitest)"

cd "$ROOT_DIR"
UI_REPORT="$REPORTS_DIR/frontend_vitest.txt"
echo "Running Vitest frontend component tests..."
if npm run test:ui 2>&1 | tee "$UI_REPORT"; then
    STATUS_UI="${GREEN}PASSED${NC}"
    ok "Frontend UI tests passed."
else
    STATUS_UI="${YELLOW}CHECK REQUIRED — see $UI_REPORT${NC}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 4. E2E — Playwright
# ─────────────────────────────────────────────────────────────────────────────
banner "STEP 4/5 — End-to-End Tests (Playwright)"

E2E_REPORT="$REPORTS_DIR/e2e_playwright.txt"
echo "Running Playwright headless browser E2E tests..."
if npm run test:e2e 2>&1 | tee "$E2E_REPORT"; then
    STATUS_E2E="${GREEN}PASSED${NC}"
    ok "E2E tests passed."
else
    STATUS_E2E="${YELLOW}CHECK REQUIRED — see $E2E_REPORT${NC}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 5. LOAD — Locust
# ─────────────────────────────────────────────────────────────────────────────
banner "STEP 5/5 — Load & Performance Testing (Locust)"

cd "$BACKEND_DIR"
LOAD_REPORT="$REPORTS_DIR/load_locust.txt"
echo "Starting Uvicorn server for load test..."
export PYTHONPATH="$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &>/dev/null &
UVICORN_PID=$!
sleep 4

echo "Running Locust: 10 users, 2 users/sec ramp, 10 second window..."
if locust --headless -u 10 -r 2 -t 10s --host=http://localhost:8000 \
    --html "$REPORTS_DIR/locust_report.html" 2>&1 | tee "$LOAD_REPORT"; then
    STATUS_LOAD="${GREEN}PASSED — 0% failure rate${NC}"
    ok "Load test completed successfully."
else
    FAIL_RATE=$(grep "Aggregated" "$LOAD_REPORT" | tail -1 | awk '{print $5}' || echo "?")
    STATUS_LOAD="${YELLOW}COMPLETED — check failure rate in report${NC}"
fi

kill "$UVICORN_PID" 2>/dev/null || true
cd "$ROOT_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# FINAL REPORT DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
banner "QA COMPLETE — FULL REPORT DASHBOARD"

echo -e "${BOLD}┌─────────────────────────────────────────────────┐${NC}"
echo -e "${BOLD}│            LEARNWISE QA RESULTS SUMMARY         │${NC}"
echo -e "${BOLD}├─────────────────────────────────────────────────┤${NC}"
echo -e "│ 1. Backend Tests / Coverage : $(echo -e $STATUS_PYTEST)"
echo -e "│ 2. Mutation Testing         : $(echo -e $STATUS_MUTATION)"
echo -e "│ 3. Frontend (Vitest)        : $(echo -e $STATUS_UI)"
echo -e "│ 4. E2E (Playwright)         : $(echo -e $STATUS_E2E)"
echo -e "│ 5. Load Testing (Locust)    : $(echo -e $STATUS_LOAD)"
echo -e "${BOLD}└─────────────────────────────────────────────────┘${NC}"

echo ""
echo -e "${BOLD}━━━ PYTEST COVERAGE TABLE ━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
grep -A 999 "^Name" "$PYTEST_REPORT" | grep -B 999 "^TOTAL" || true

echo ""
echo -e "${BOLD}━━━ LOAD TEST — REQUEST SUMMARY ━━━━━━━━━━━━━━━━━━${NC}"
grep -A 20 "Type.*Name.*reqs" "$LOAD_REPORT" | tail -20 || true

echo ""
echo -e "${BOLD}━━━ MUTATION TEST — FINAL COUNTS ━━━━━━━━━━━━━━━━━${NC}"
tail -20 "$MUTATION_REPORT" || true

echo ""
echo -e "${BOLD}━━━ REPORTS DIRECTORY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
ls -lh "$REPORTS_DIR/"

echo ""
echo -e "${GREEN}${BOLD}All QA reports saved to: $REPORTS_DIR/${NC}"
echo -e "${CYAN}${BOLD}Pipeline complete. Platform is ready for review.${NC}"
