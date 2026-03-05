# PySymBench
Infrastructure for **model comparison and evaluation in symbolic execution workflows**.

This project is a **local web application** designed to compare symbolic execution results of an uploaded trained model (in `.onnx` format) on a selected dataset with a **baseline symbolic execution approach (non-AI)**.

The system uses **PySymGym tools** to run symbolic execution on the dataset and evaluate the results. After execution completes, the results are sent to the **email address you provide**.

# Installation

The repository contains **both frontend and backend components**, and **both must be launched** for the application to work.

---

## Email Communication (Gmail)

To enable email delivery of results, create a `.env` file containing your Gmail credentials:

```
EMAIL=your_email@gmail.com
APP_PASSWORD=your_app_password
```

`EMAIL` — your Gmail address  
`APP_PASSWORD` — your Gmail **App Password** (not your regular account password)

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
```

3. Start the frontend development server:

```
npm run build
```
