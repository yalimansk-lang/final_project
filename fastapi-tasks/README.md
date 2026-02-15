# FastAPI Tasks

Simple task management API built with FastAPI that stores data in a plain text file.

## Project structure

```text
fastapi-tasks/
├── main.py      # FastAPI application (single-file)
├── tasks.txt    # JSON array of tasks (plain text)
└── README.md
```

## Requirements

Install dependencies (from the project root that contains `requirements.txt`):

```bash
pip install -r requirements.txt
```

## Running the app

From inside the `fastapi-tasks/` directory:

```bash
uvicorn main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000/` – health check
- `http://127.0.0.1:8000/docs` – interactive Swagger UI

## API overview

- `GET /tasks` – list all tasks
- `GET /tasks/{task_id}` – get a single task by ID
- `POST /tasks` – create a new task
- `PUT /tasks/{task_id}` – fully replace an existing task
- `PATCH /tasks/{task_id}` – partially update a task
- `DELETE /tasks/{task_id}` – delete a task

Tasks are persisted as a JSON array in the `tasks.txt` file.

