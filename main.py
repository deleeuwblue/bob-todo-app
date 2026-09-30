from datetime import date, datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# ORM model
# ---------------------------------------------------------------------------

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class TodoCreate(BaseModel):
    title: str
    due_date: Optional[date] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    due_date: Optional[date] = None
    completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------

def get_db():
    """Provide a transactional database session scope.

    Yields:
        db: SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# App and routes
# ---------------------------------------------------------------------------

app = FastAPI(title="TODO App")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/api/todos", response_model=list[TodoResponse])
def list_todos(db: Session = Depends(get_db)):
    """Retrieve all todo items ordered by creation date ascending.

    Args:
        db: Database session injected by FastAPI dependency.

    Returns:
        List of TodoResponse objects representing all todos.
    """
    return db.query(Todo).order_by(Todo.created_at.asc()).all()


@app.post("/api/todos", response_model=TodoResponse, status_code=201)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo item with an optional due date.

    Args:
        payload: TodoCreate payload containing title and optional due_date.
        db: Database session injected by FastAPI dependency.

    Returns:
        Created TodoResponse object.
    """
    todo = Todo(title=payload.title, due_date=payload.due_date)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@app.patch("/api/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, payload: TodoUpdate, db: Session = Depends(get_db)):
    """Update fields on an existing todo item.

    Args:
        todo_id: Integer primary key ID of the todo to update.
        payload: TodoUpdate payload containing fields to update.
        db: Database session injected by FastAPI dependency.

    Returns:
        Updated TodoResponse object.

    Raises:
        HTTPException: 404 if the todo item is not found.
    """
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    if payload.title is not None:
        todo.title = payload.title
    if payload.due_date is not None:
        todo.due_date = payload.due_date
    if payload.completed is not None:
        todo.completed = payload.completed
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/api/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo item by ID.

    Args:
        todo_id: Integer primary key ID of the todo to delete.
        db: Database session injected by FastAPI dependency.

    Returns:
        None.

    Raises:
        HTTPException: 404 if the todo item is not found.
    """
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()


@app.get("/")
def serve_index():
    """Serve the single page application HTML file.

    Returns:
        FileResponse serving the static index.html file.
    """
    return FileResponse("static/index.html")
