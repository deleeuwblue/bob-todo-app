/* app.js — Todo frontend logic */

const list         = document.getElementById('todo-list');
const form         = document.getElementById('add-form');
const titleInput   = document.getElementById('new-title');
const dueDateInput = document.getElementById('new-due-date');
const emptyState   = document.getElementById('empty-state');

// -------------------------------------------------------------------------
// API helpers
// -------------------------------------------------------------------------

/**
 * Purpose:
 *   Centralized wrapper around the native `fetch` API for making HTTP requests
 *   to backend endpoints.
 *
 * How API calls work:
 *   - Sends an HTTP request to the specified `path` with default `Content-Type: application/json` headers.
 *   - Merges custom request options (e.g., HTTP method like POST/PATCH/DELETE, payload body).
 *   - Returns parsed JSON for successful responses with content, or `null` for 204 No Content.
 *
 * How error handling is implemented:
 *   - Checks `res.ok` (status code 200–299). If false, attempts to parse the error message
 *     from the response JSON body (`res.json().catch(() => ({}))`), safely falling back to
 *     an empty object if the response cannot be parsed as JSON.
 *   - Throws a descriptive `Error` containing either the backend error message (`err.error`)
 *     or the HTTP status code (e.g., `Request failed (404)`).
 */
async function apiFetch(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (res.status === 204) return null;
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed (${res.status})`);
  }
  return res.json();
}

// -------------------------------------------------------------------------
// Render
// -------------------------------------------------------------------------

/**
 * Purpose:
 *   Constructs and returns the DOM element (`<li>`) representing a single todo item.
 *   Creates the checkbox input, title span, and delete button with proper data attributes and ARIA labels.
 */
function renderTodo(todo) {
  const li = document.createElement('li');
  li.className = `todo-item${todo.completed ? ' completed' : ''}`;
  li.dataset.id = todo.id;

  const checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.checked = todo.completed;
  checkbox.setAttribute('aria-label', 'Mark complete');

  const title = document.createElement('span');
  title.className = 'todo-title';
  title.textContent = todo.title;

  const dueDate = document.createElement('span');
  dueDate.className = 'due-date';
  dueDate.textContent = `Due: ${todo.due_date}`;

  const deleteBtn = document.createElement('button');
  deleteBtn.className = 'delete-btn';
  deleteBtn.setAttribute('aria-label', 'Delete todo');
  deleteBtn.textContent = '✕';

  li.append(checkbox, title, dueDate, deleteBtn);
  return li;
}

/**
 * Purpose:
 *   Toggles visibility of the empty state placeholder based on whether there are
 *   any items currently in the list container.
 */
function syncEmptyState() {
  emptyState.classList.toggle('visible', list.children.length === 0);
}

// -------------------------------------------------------------------------
// Data operations
// -------------------------------------------------------------------------

/**
 * Purpose:
 *   Loads all todo items from the server and renders them in the list.
 *
 * How API calls work:
 *   - Calls `GET /api/todos` via `apiFetch('/api/todos')` to fetch the list of todos.
 *
 * How error handling is implemented:
 *   - Wraps the operation in a `try...catch` block.
 *   - If network or API failure occurs, catches the error and logs it to `console.error` without breaking the UI.
 */
async function fetchTodos() {
  try {
    const todos = await apiFetch('/api/todos');
    list.innerHTML = '';
    todos.forEach(todo => list.appendChild(renderTodo(todo)));
    syncEmptyState();
  } catch (err) {
    console.error('Failed to load todos:', err);
  }
}

/**
 * Purpose:
 *   Creates a new todo item on the server and appends it to the DOM list.
 *
 * How API calls work:
 *   - Calls `POST /api/todos` via `apiFetch` with a JSON payload containing `{ title }`.
 *   - Receives the newly created todo object with its generated `id`.
 *
 * How error handling is implemented:
 *   - Uses a `try...catch` block around the async API call and DOM update.
 *   - If the request fails (e.g. validation error or network issue), logs the error with `console.error`.
 */
async function addTodo(title, dueDate) {
  try {
    const todo = await apiFetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify({ title, due_date: dueDate }),
    });
    list.appendChild(renderTodo(todo));
    syncEmptyState();
  } catch (err) {
    console.error('Failed to add todo:', err);
  }
}

/**
 * Purpose:
 *   Updates the completion status of an existing todo on the server and synchronizes the DOM.
 *
 * How API calls work:
 *   - Calls `PATCH /api/todos/{id}` via `apiFetch` with a JSON payload `{ completed }`.
 *   - Receives the updated todo object back from the server.
 *
 * How error handling is implemented:
 *   - Uses a `try...catch` block to handle network/server errors and logs them to `console.error`.
 *   - Checks that the list element exists in the DOM before attempting to update classes or checkbox state.
 */
async function toggleTodo(id, completed) {
  try {
    const updated = await apiFetch(`/api/todos/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ completed }),
    });
    const li = list.querySelector(`[data-id="${id}"]`);
    if (!li) return;
    li.classList.toggle('completed', updated.completed);
    li.querySelector('input[type="checkbox"]').checked = updated.completed;
  } catch (err) {
    console.error('Failed to update todo:', err);
  }
}

/**
 * Purpose:
 *   Deletes a todo item on the server by ID and removes its corresponding DOM node.
 *
 * How API calls work:
 *   - Calls `DELETE /api/todos/{id}` via `apiFetch` with `method: 'DELETE'`.
 *   - Server returns 204 No Content on success.
 *
 * How error handling is implemented:
 *   - Wrapped in a `try...catch` block.
 *   - If deletion fails on the server, the error is logged and the item remains in the UI.
 *   - Safely removes the element from the DOM only after a successful response.
 */
async function deleteTodo(id) {
  try {
    await apiFetch(`/api/todos/${id}`, { method: 'DELETE' });
    const li = list.querySelector(`[data-id="${id}"]`);
    if (li) li.remove();
    syncEmptyState();
  } catch (err) {
    console.error('Failed to delete todo:', err);
  }
}

// -------------------------------------------------------------------------
// Event listeners
// -------------------------------------------------------------------------
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = titleInput.value.trim();
  const dueDate = dueDateInput.value;
  if (!title || !dueDate) return;
  titleInput.value = '';
  dueDateInput.value = '';
  await addTodo(title, dueDate);
});

list.addEventListener('change', (e) => {
  if (e.target.type !== 'checkbox') return;
  const li = e.target.closest('.todo-item');
  toggleTodo(Number(li.dataset.id), e.target.checked);
});

list.addEventListener('click', (e) => {
  if (!e.target.classList.contains('delete-btn')) return;
  const li = e.target.closest('.todo-item');
  deleteTodo(Number(li.dataset.id));
});

// -------------------------------------------------------------------------
// Init
// -------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', fetchTodos);
