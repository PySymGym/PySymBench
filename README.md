# PySymBench

Infrastructure for **AI model comparison and evaluation in symbolic execution workflows**.

PySymBench is a **local web application** for evaluating ONNX models against a non-AI baseline symbolic execution strategy. Experiments run inside Docker using [PySymGym](https://github.com/PySymGym/PySymGym) tools on a fixed dataset; results are emailed back to the user and (when published) saved to a leaderboard.

Three target languages are supported for the dataset: **C#**, **Java**, and **C++**.

## Features

- **Run Experiment** — upload an ONNX model, choose a target language, select methods from the dataset, and compare the model against the baseline strategy. Coverage, errors and timing are emailed to you. Each running task can be cancelled via a one-click link in the confirmation email.
- **Model Ranking** — a leaderboard of all completed experiments per language (with an aggregated view across languages), sorted by mean coverage. Per-experiment metrics include mean/median coverage, total tests, errors, runtime, and coverage percentage.
- **Pairwise Comparison** — pick any two experiments from the ranking and produce side-by-side comparison artifacts (PDFs) downloadable individually or as a single zip.
- **Model Interface docs** — page that describes the ONNX input/output specification required to plug a model into PySymGym.

### Routes

The frontend is a multi-page React SPA using `react-router-dom`:

| Route | Page |
|---|---|
| `/` | Home — navigation hub |
| `/experiment` | Run Experiment form |
| `/ranking` | Model Ranking leaderboard + pairwise comparison |
| `/interface` | Model Interface specification |

### Backend API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/upload` | Submit a new experiment (multipart: ONNX file, `email`, `language`, `experiment`) |
| `GET` | `/api/status/{task_uid}` | Celery task state |
| `POST` | `/api/cancel/{task_uid}` | Cancel a running experiment |
| `GET` | `/api/cancel/{task_uid}?token=...` | One-click cancellation link sent by email |
| `GET` | `/api/ranking?language=csharp\|java\|cpp\|all` | Leaderboard entries |
| `POST` | `/api/compare` | Start a pairwise comparison between two experiment IDs |
| `GET` | `/api/compare/{uid}/status` | Comparison task state and result file list |
| `GET` | `/api/compare/{uid}/file/{name}` | Stream a single comparison artifact |
| `GET` | `/api/compare/{uid}/files.zip` | Download all comparison PDFs as a zip |

# Installation

The repository contains **both frontend and backend components**, and **both must be launched** for the application to work.

---

## Email Communication (Gmail)

To enable email delivery of results, add Gmail credentials to your `.env` file:

```
EMAIL=your_email@gmail.com
APP_PASSWORD=your_app_password
```

`EMAIL` — your Gmail address
`APP_PASSWORD` — your Gmail **App Password** (not your regular account password)

---

## Database (PostgreSQL)

The ranking leaderboard stores experiment results in a PostgreSQL database. Add the connection URL to your `.env` file:

```
DB_URL=postgresql://user:password@localhost:5432/pysymbench
```

The required tables are created automatically on server startup. You can run a local PostgreSQL instance via Docker:

```
docker run --name postgres-pysymbench -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=pysymbench -p 5432:5432 -d postgres
```

---

## Object Storage (MinIO)

Experiments store their ONNX model and result artifacts in MinIO; the pairwise comparison feature also reads artifacts from there. MinIO must be reachable — if it is not configured or unavailable, the task fails and the user is notified by email. Add the following to your `.env` file:

```
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_SECURE=false
MINIO_BUCKET=pysymbench
```

You can run a local MinIO instance via Docker:

```
docker run --name minio -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=your_access_key -e MINIO_ROOT_PASSWORD=your_secret_key \
  -d minio/minio server /data --console-address ":9001"
```

---

## Redis (Celery Broker)

By default, the Celery broker is expected at `redis://localhost:6379`. To use a remote Redis instance (e.g., for running Celery workers on separate machines), set `REDIS_URL` in your `.env` file:

```
REDIS_URL=redis://<host>:6379
```

All services that connect to Redis — the FastAPI app and every Celery worker — must have the same `REDIS_URL`. Workers on remote machines need only the `backend/` code, Docker, and access to the shared Redis instance.

---

## URLs for email links

Cancellation links sent by email are absolute, so the backend needs to know its own public URL and the URL of the frontend. Defaults match a local setup; override them in `.env` if the app is reachable elsewhere:

```
BASE_URL=http://localhost:8000      # base URL of the FastAPI app
FRONTEND_URL=http://localhost:5173  # base URL of the React frontend
```

---

## Backend Setup

1. Install **Python 3.14** and **Docker**, then install the project dependencies:

```
pip install -r requirements.txt
```

2. Run the application setup script (this builds a Docker container with the **PySymGym repository** and downloads the required dataset):

```
python -m backend.launch_service.app_setup
```

3. Start the **Celery broker (Redis)**:

```
docker run --name redis-for-celery -p 6379:6379 -d redis
```

4. Start the **Celery worker** and the **application server** (in separate terminals):

```
celery -A backend.utils.task worker --loglevel=info
uvicorn backend.main:app
```

---

## Frontend Setup

1. Install **Node.js** with **npm**.

2. Install frontend dependencies:

```
cd frontend
npm install
```

3. Start the frontend development server:

```
npm run dev
```

Or build for production:

```
npm run build
```

### Frontend technology stack

| Package | Purpose |
|---|---|
| `react-router-dom` | Client-side routing between pages |
| `antd` | UI component library (forms, tables, buttons, modals) |
| `tailwindcss` | Utility-first CSS framework |
| `vite` | Build tool and dev server |

---

## Development

### Python

```
ruff check .          # Lint
ruff check . --fix    # Auto-fix
ruff format .         # Format
pytest -v             # Run tests
```

### Frontend

```
cd frontend
npm run lint:fix      # ESLint auto-fix
npm run format        # Prettier format
npm run format:check  # Check formatting without writing
```

## CI/CD

GitHub Actions runs on push/PR:
- **`linting.yml`** — ruff check + format, ESLint + Prettier
- **`build_and_test.yml`** — builds Docker image, runs `pytest -v`
