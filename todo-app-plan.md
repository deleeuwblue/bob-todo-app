# TODO App — Implementation Plan

## Overview

Build a minimal, single-page TODO application with:
- **Backend**: FastAPI (Python) with SQLite via SQLAlchemy, serving a REST API and static files
- **Frontend**: Vanilla HTML/CSS/JS (no framework, no build step) served directly from FastAPI
- **Data model**: `Todo` — `id`, `title`, `completed`, `created_at`
- **Scope**: Single shared list, no user accounts, CRUD only
- **Security**: Server binds to `127.0.0.1` only (not `0.0.0.0`)

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffolding

**Status**: `[ ] pending`

**Intent**  
Establish the project file layout and package dependencies so every subsequent sub-task has a stable, runnable base to build on.

**Expected Outcomes**
- `requirements.txt` listing pinned, up-to-date dependencies
- `.gitignore` excluding `.env`, `*.db`, `__pycache__`, `.venv/`
- `static/` directory created (initially empty)
- `main.py` exists as an empty module placeholder
- Running `pip install -r requirements.txt` succeeds

**Todo List**
1. Create `requirements.txt` with latest stable versions of: `fastapi`, `uvicorn[standard]`, `sqlalchemy`
2. Create `.gitignore` covering Python artifacts, SQLite files, and virtual environments
3. Create the `static/` directory
4. Create an empty `main.py`

**Relevant Context**
- No existing files in the workspace (greenfield)
- Security policy requires actively maintained packages at latest stable versions

---

### Sub-Task 2 — Database Setup and Data Model

**Status**: `[ ] pending`

**Intent**  
Define the SQLite database connection, the `todos` table via SQLAlchemy ORM, and the Pydantic schemas used by the API. This is the data layer that all routes depend on.

**Expected Outcomes**
- `main.py` contains a working SQLAlchemy engine pointed at `todos.db`
- A `Todo` ORM model with columns: `id` (int PK), `title` (str), `completed` (bool, default False), `created_at` (datetime, default now)
- Pydantic schemas: `TodoCreate` (title only), `TodoUpdate` (title and/or completed), `TodoResponse` (all fields)
- `create_all()` is called on startup so the table is created automatically on first run
- Importing `main.py` raises no errors

**Todo List**
1. Add SQLAlchemy engine, `SessionLocal`, and `Base` to `main.py`
2. Define the `Todo` ORM model class
3. Define `TodoCreate`, `TodoUpdate`, and `TodoResponse` Pydantic schemas
4. Add a `get_db()` dependency function that yields and closes a session
5. Call `Base.metadata.create_all()` at module level so the schema is applied on startup

**Relevant Context**
- SQLite file will be named `todos.db` in the project root
- Keep all code in `main.py` (flat module, no package layout)

---

### Sub-Task 3 — REST API Routes

**Status**: `[ ] pending`

**Intent**  
Implement the five CRUD endpoints that the frontend will call. Each route delegates directly to SQLAlchemy queries — no separate service layer given the app's small size.

**Expected Outcomes**
- `GET /api/todos` — returns list of all todos ordered by `created_at` ascending
- `POST /api/todos` — creates and returns a new todo
- `PATCH /api/todos/{id}` — updates `title` and/or `completed`, returns updated todo
- `DELETE /api/todos/{id}` — deletes todo, returns `204 No Content`
- `GET /` — serves `static/index.html` (added in sub-task 4, but route scaffolded here)
- FastAPI app is mounted to serve `static/` at `/static`
- All routes return appropriate HTTP status codes and generic error messages (no stack traces exposed)
- The server binds to `127.0.0.1:8000` in the startup instructions

**Todo List**
1. Create the `FastAPI()` app instance in `main.py`
2. Mount `StaticFiles` at `/static` pointing to the `static/` directory
3. Implement `GET /api/todos`
4. Implement `POST /api/todos`
5. Implement `PATCH /api/todos/{id}` (404 if not found, generic error message)
6. Implement `DELETE /api/todos/{id}` (404 if not found, generic error message)
7. Add a catch-all `GET /` route that returns `static/index.html`
8. Verify all routes return correct status codes

**Relevant Context**
- Use `JSONResponse` with a generic message for 404 errors — do not expose ORM exceptions to callers
- `PATCH` is preferred over `PUT` because only changed fields need to be sent

---

### Sub-Task 4 — Frontend: HTML and CSS

**Status**: `[ ] pending`

**Intent**  
Create the single-page UI shell — the HTML structure and CSS styling — without any JavaScript logic. This separates markup/style concerns from behaviour and makes the UI reviewable on its own.

**Expected Outcomes**
- `static/index.html` exists and renders correctly when opened via the FastAPI server
- Page shows: a heading, an input field + "Add" button for creating todos, and an empty list container
- Basic styling: readable font, clear todo items with a checkbox and delete button per item
- No JavaScript wired yet — the list area is an empty `<ul>` placeholder

**Todo List**
1. Create `static/index.html` with semantic HTML5 structure
2. Create `static/style.css` and link it from `index.html`
3. Style the input/add form, the todo list items, the checkbox, and the delete button
4. Add a `<ul id="todo-list">` placeholder and a `<script src="app.js">` tag

**Relevant Context**
- `index.html` is served by the `GET /` route defined in Sub-Task 3
- CSS lives in `static/style.css`; JS will live in `static/app.js` (wired in Sub-Task 5)

---

### Sub-Task 5 — Frontend: JavaScript Logic

**Status**: `[ ] pending`

**Intent**  
Wire the UI to the API. All interaction — loading todos on page load, adding, toggling completion, and deleting — is handled via `fetch` calls to the FastAPI routes.

**Expected Outcomes**
- `static/app.js` fetches and renders all todos on page load
- Submitting the add form calls `POST /api/todos` and re-renders the list
- Clicking a todo's checkbox calls `PATCH /api/todos/{id}` with `{ "completed": true/false }`
- Clicking a delete button calls `DELETE /api/todos/{id}` and removes the item from the DOM
- Errors from the API are caught and logged to the console (not exposed in the UI as raw stack traces)
- No page reloads — all updates are reflected without a full refresh

**Todo List**
1. Create `static/app.js`
2. Implement `fetchTodos()` — `GET /api/todos`, render results into `#todo-list`
3. Implement `addTodo(title)` — `POST /api/todos`, then call `fetchTodos()`
4. Implement `toggleTodo(id, completed)` — `PATCH /api/todos/{id}`
5. Implement `deleteTodo(id)` — `DELETE /api/todos/{id}`, then remove the DOM element
6. Attach event listeners to the form submit and delegate checkbox/delete events on the list
7. Call `fetchTodos()` on `DOMContentLoaded`

**Relevant Context**
- All API paths are relative (`/api/todos`) so no base URL configuration is needed
- Completed todos should be visually distinguished (e.g. strikethrough via a CSS class)

---

### Sub-Task 6 — README

**Status**: `[ ] pending`

**Intent**  
Document how to install, run, and use the application so the project is self-contained and hand-off-ready.

**Expected Outcomes**
- `README.md` exists at the project root
- Covers: prerequisites, installation steps, how to start the server, and how to open the app in a browser

**Todo List**
1. Create `README.md` with sections: Overview, Prerequisites, Installation, Running, Usage
2. Include the exact `uvicorn main:app --host 127.0.0.1 --port 8000` start command

**Relevant Context**
- Server must be documented as binding to `127.0.0.1`, not `0.0.0.0`
