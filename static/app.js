/**
 * app.js — TODO App frontend logic
 * Communicates with the FastAPI backend via fetch. No page reloads.
 */

const list = document.getElementById('todo-list');
const form = document.getElementById('add-form');
const input = document.getElementById('new-title');

// ── API helpers ────────────────────────────────────────────────────────────

async function fetchTodos() {
  try {
    const res = await fetch('/api/todos');
    if (!res.ok) throw new Error(`GET /api/todos returned ${res.status}`);
    const todos = await res.json();
    renderList(todos);
  } catch (err) {
    console.error('Failed to load todos:', err);
  }
}

async function addTodo(title) {
  try {
    const res = await fetch('/api/todos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error(`POST /api/todos returned ${res.status}`);
    await fetchTodos();
  } catch (err) {
    console.error('Failed to add todo:', err);
  }
}

async function toggleTodo(id, completed) {
  try {
    const res = await fetch(`/api/todos/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed }),
    });
    if (!res.ok) throw new Error(`PATCH /api/todos/${id} returned ${res.status}`);
    const updated = await res.json();
    // Update only the affected item in the DOM without a full re-render
    const item = list.querySelector(`[data-id="${id}"]`);
    if (item) applyCompletedState(item, updated.completed);
  } catch (err) {
    console.error(`Failed to toggle todo ${id}:`, err);
  }
}

async function deleteTodo(id) {
  try {
    const res = await fetch(`/api/todos/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(`DELETE /api/todos/${id} returned ${res.status}`);
    const item = list.querySelector(`[data-id="${id}"]`);
    if (item) item.remove();
  } catch (err) {
    console.error(`Failed to delete todo ${id}:`, err);
  }
}

// ── Rendering ──────────────────────────────────────────────────────────────

function renderList(todos) {
  list.innerHTML = '';
  todos.forEach((todo) => list.appendChild(createItem(todo)));
}

function createItem({ id, title, completed }) {
  const li = document.createElement('li');
  li.className = 'todo-item';
  li.dataset.id = id;

  const checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.checked = completed;
  checkbox.setAttribute('aria-label', `Mark "${title}" as ${completed ? 'incomplete' : 'complete'}`);

  const span = document.createElement('span');
  span.className = 'todo-title';
  span.textContent = title;

  const deleteBtn = document.createElement('button');
  deleteBtn.className = 'delete-btn';
  deleteBtn.textContent = '✕';
  deleteBtn.setAttribute('aria-label', `Delete "${title}"`);

  li.appendChild(checkbox);
  li.appendChild(span);
  li.appendChild(deleteBtn);

  applyCompletedState(li, completed);
  return li;
}

function applyCompletedState(item, completed) {
  const checkbox = item.querySelector('input[type="checkbox"]');
  if (checkbox) checkbox.checked = completed;
  item.classList.toggle('completed', completed);
}

// ── Event listeners ────────────────────────────────────────────────────────

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = input.value.trim();
  if (!title) return;
  input.value = '';
  await addTodo(title);
});

// Event delegation — handles clicks on any checkbox or delete button in the list
list.addEventListener('change', async (e) => {
  if (e.target.type !== 'checkbox') return;
  const item = e.target.closest('[data-id]');
  if (!item) return;
  await toggleTodo(Number(item.dataset.id), e.target.checked);
});

list.addEventListener('click', async (e) => {
  if (!e.target.classList.contains('delete-btn')) return;
  const item = e.target.closest('[data-id]');
  if (!item) return;
  await deleteTodo(Number(item.dataset.id));
});

// ── Bootstrap ──────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', fetchTodos);
