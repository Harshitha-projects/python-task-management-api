# Task Management REST API

A Python backend portfolio project implementing CRUD endpoints with persistent SQLite storage, validation, filtering, pagination, and automated tests.

## Stack
Python 3.10+, FastAPI, SQLAlchemy 2, SQLite, Pydantic, pytest.

## Setup
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs. A local `tasks.db` is created automatically.

## API endpoints
| Method | Path | Description |
|---|---|---|
| GET | /health | Health check |
| POST | /tasks | Create task |
| GET | /tasks | List tasks, filter by `status`, paginate via `limit` and `offset` |
| GET | /tasks/{task_id} | Retrieve task |
| PATCH | /tasks/{task_id} | Partially update task |
| DELETE | /tasks/{task_id} | Delete task |

## Example
In Swagger `/docs`, execute `POST /tasks` with:
```json
{"title":"Review pull request","description":"Check tests and API validation","status":"todo"}
```
Then call `GET /tasks` to list the saved task.

## Tests
```bash
pytest -q
```
Tests use an isolated in-memory SQLite database.

## Design notes
SQLite makes local setup easy; `DATABASE_URL` can be configured for other SQLAlchemy-supported databases with the appropriate driver. Production improvements include authentication, authorization, migrations (Alembic), logging, observability, and deployment automation.
