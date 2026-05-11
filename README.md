# PySymBench
Infrastructure for **model comparison and evaluation in symbolic execution workflows**.

This project is a **local web application** designed to compare symbolic execution results of an uploaded trained model (in `.onnx` format) on a selected dataset with a **baseline symbolic execution approach (non-AI)**.

The system uses **PySymGym tools** to run symbolic execution on the dataset and evaluate the results. After execution completes, the results are sent to the **email address you provide**.

## Features

- **Run Experiment** — upload an ONNX model, select test methods from the dataset, and compare it against the baseline strategy. Results (coverage, errors, timing) are delivered to your inbox.
- **Model Ranking** — a public leaderboard of all published experiments, sorted by mean coverage. Shows per-experiment metrics: mean/median coverage, total tests, errors, and runtime.
- **Publish Experiment** — submit a model to the ranking leaderboard. The experiment runs in Docker, computes metrics, and saves the result to the database. Supports cancellation while in progress.

The frontend is a multi-page React SPA using `react-router-dom`:

| Route | Page |
|---|---|
| `/` | Home — navigation hub |
| `/experiment` | Run Experiment form |
| `/ranking` | Model Ranking leaderboard |
| `/ranking/publish` | Publish Experiment form |

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

The required table is created automatically on server startup. You can run a local PostgreSQL instance via Docker:

```
docker run --name postgres-pysymbench -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=pysymbench -p 5432:5432 -d postgres
```

---

## Object Storage (MinIO) — optional

When publishing experiments to the ranking, the ONNX model and result artifacts can be stored in MinIO. Add the following to your `.env` file:

```
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_SECURE=false
MINIO_BUCKET=pysymbench
```

If not configured, artifact upload is skipped and only metrics are saved to the database. You can run a local MinIO instance via Docker:

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

4. Start the **Celery worker** and the **application server**:

```
celery -A backend.utils.task worker --loglevel=info && uvicorn backend.main:app
```

---

## Frontend Setup

1. Install **Node.js** with **npm**.

2. Install frontend dependencies:

```
cd frontend
npm install
npm install react-router-dom @types/react-router-dom
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
| `@types/react-router-dom` | TypeScript types for react-router-dom |
| `antd` | UI component library (forms, tables, buttons) |
| `tailwindcss` | Utility-first CSS framework |
| `vite` | Build tool and dev server |
