# TODO App

A minimal single-page TODO application built with **FastAPI** (Python) on the backend and plain HTML/CSS/JavaScript on the frontend. No frameworks, no build step — just a clean REST API and a lightweight browser UI.

---

## Overview

- **Backend**: FastAPI + SQLAlchemy ORM with a local SQLite database
- **Frontend**: Vanilla HTML5, CSS3, and ES2017+ JavaScript served directly from FastAPI
- **Data model**: `Todo` — `id`, `title`, `completed`, `created_at`
- **Scope**: Single shared list, no user accounts, full CRUD
- **Security**: Server binds to `127.0.0.1` only (never `0.0.0.0`)

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11 or newer |
| pip | bundled with Python |

No other system dependencies are required. SQLite is included in the Python standard library.

---

## Installation

1. **Clone or download** the project, then change into its directory:

   ```bash
   cd todo-app
   ```

2. **(Recommended)** Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate      # Windows PowerShell
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

---

## Running

Start the development server:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

The server will bind to `127.0.0.1:8000`. The SQLite database (`todos.db`) is created automatically on first run.

---

## Usage

1. Open your browser at **http://127.0.0.1:8000**
2. Type a task in the input field and click **Add** (or press Enter) to create a todo
3. Click the **checkbox** next to a todo to toggle it between incomplete and complete — completed items are shown with a strikethrough
4. Click the **✕ button** on any todo to delete it permanently

All changes are reflected immediately without a page reload.

---

## API Reference

The REST API is available under `/api/todos`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/todos` | List all todos (ordered by creation time) |
| `POST` | `/api/todos` | Create a new todo — body: `{ "title": "..." }` |
| `PATCH` | `/api/todos/{id}` | Update a todo — body: `{ "title": "...", "completed": true }` |
| `DELETE` | `/api/todos/{id}` | Delete a todo (returns 204 No Content) |

Interactive API docs (Swagger UI) are available at **http://127.0.0.1:8000/docs**.

---

## Project Structure

```
.
├── main.py            # FastAPI app, ORM model, Pydantic schemas, API routes
├── requirements.txt   # Pinned Python dependencies
├── static/
│   ├── index.html     # Single-page UI shell
│   ├── style.css      # All styles
│   └── app.js         # Fetch-based API calls and DOM rendering
├── todos.db           # SQLite database (auto-created, git-ignored)
└── README.md
```

---

## Running Tests

```bash
pip install pytest httpx
pytest test_api.py -v
```
