# items_api — Agent Task Specifications

This document is the contract between the architect and the agents.
Every bead created for this project must reference the corresponding
task section verbatim. Do not summarize or rephrase.

---

## TASK-01: Scaffold + GET /health

### Context Packet
- **State**: empty repo with only README.md on main
- **Objective**: create a working FastAPI project with a health check endpoint
- **Constraints**: Python only, FastAPI + uvicorn[standard], no database layer
- **Prior outputs available**: none

### Specification
- Create `main.py` with a FastAPI application instance
- Implement `GET /health` returning `{"status": "ok"}` with HTTP 200
- Create `requirements.txt` containing: fastapi, uvicorn[standard], pytest, httpx, ruff
- Create `.gitignore` for Python (`__pycache__`, `.pytest_cache`, `.ruff_cache`, `venv`)

### Acceptance Criteria
- **Command**: `uvicorn main:app --port 8000 &`
- **Validation**: `curl -s http://localhost:8000/health`
- **Expected output**: `{"status":"ok"}`
- **Exit condition**: HTTP 200 + exact JSON match

### Output Artifacts
- `main.py`
- `requirements.txt`
- `.gitignore`

### Failure Modes
- uvicorn fails to start: missing dependency in requirements.txt
- Wrong JSON format: fix return value in endpoint
- Import error: fix main.py module structure

### Handoff to TASK-02
- TASK-02 receives: working main.py confirmed by validation command
- TASK-02 does NOT receive: internal implementation decisions

---

## TASK-02: POST /items + pytest suite

### Context Packet
- **State**: main.py with GET /health confirmed working and merged to main
- **Objective**: add POST /items endpoint and a complete test suite
- **Constraints**: use pytest + httpx, store items in memory with uuid-generated ids
- **Prior outputs available**: main.py, requirements.txt (already on main)

### Specification
- Add `POST /items` accepting `{"name": str, "price": float}`
- Validate that `price > 0`; return 422 on invalid input
- Return created item with generated UUID: `{"id": str, "name": str, "price": float}`
- Add `GET /items/{id}` returning the item or 404 if not found
- Write `test_items.py` in the repo root with exactly 6 tests:
    - `test_create_item_success`
    - `test_get_item_after_create`
    - `test_create_item_missing_name`
    - `test_create_item_missing_price`
    - `test_create_item_negative_price`
    - `test_get_item_not_found`

### Acceptance Criteria
- **Command**: `pytest test_items.py -v`
- **Expected output**: 6 passed
- **Exit condition**: exit code 0, zero failures, zero errors

### Output Artifacts
- `main.py` (modified)
- `test_items.py`

### Failure Modes
- Test count != 6: add or remove tests to match spec exactly
- Any test fails: fix the corresponding endpoint logic
- Import error in tests: verify httpx is in requirements.txt

### Handoff to TASK-03
- TASK-03 receives: main.py with both endpoints confirmed, test_items.py passing
- TASK-03 does NOT receive: test implementation details

---

## TASK-03: Lint + README + release notes

### Context Packet
- **State**: main.py with two endpoints, test_items.py with 6 passing tests, on main
- **Objective**: enforce code quality, document the project, produce release notes
- **Constraints**: ruff for linting, README must document the API not the workflow
- **Prior outputs available**: entire repo contents on main

### Specification
- Run `ruff check .` and fix all violations
- Run `ruff format .` for consistent formatting
- Write `README.md` documenting:
    - Installation (`pip install -r requirements.txt`)
    - Running the server (uvicorn command)
    - Each endpoint with curl examples and expected responses
    - Running tests (pytest command)
- Write `CHANGELOG.md` with v0.1.0 release notes listing all endpoints added

### Acceptance Criteria
- **Command**: `ruff check .`
- **Expected output**: `All checks passed!`
- **Exit condition**: exit code 0

### Output Artifacts
- `main.py` (reformatted if needed)
- `README.md`
- `CHANGELOG.md`

### Failure Modes
- ruff violations: run `ruff check --fix .` first, then verify manually
- README missing section: add the missing section per spec above
- Formatting not applied: run `ruff format .` explicitly

### Handoff
None — this is the final task.
