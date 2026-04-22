#!/bin/bash
# run_all_tests.sh
echo "=== KILLING BACKGROUND SERVICES ==="
pkill -f 'uvicorn app.main:app' || true
pkill -f 'vite' || true
pkill -f 'locust' || true
sleep 1

echo "=== 1. BACKEND TESTS ==="
cd backend
source venv/bin/activate
pytest --cov=app > ../backend_test_results.txt
cd ..

echo "=== 2. FRONTEND UI TESTS ==="
npm run test:ui > frontend_test_results.txt

echo "=== 3. END-TO-END TESTS (PLAYWRIGHT) ==="
npm run test:e2e > e2e_results.txt

echo "=== 4. MUTATION TESTING ==="
cd backend
source venv/bin/activate
mutmut run > ../mutmut_results.txt || true
mutmut results >> ../mutmut_results.txt || true
cd ..

echo "=== 5. NON-FUNCTIONAL LOAD TESTING ==="
cd backend
source venv/bin/activate
export PYTHONPATH=$(pwd)
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
PID=$!
sleep 5
locust --headless -u 10 -r 2 -t 10s --host=http://localhost:8000 > ../locust_results.txt || true
kill $PID || true
cd ..

echo "=== DONE ==="
