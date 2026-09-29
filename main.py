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
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    due_date = Column(Date, nullable=True)


Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class TodoCreate(BaseModel):
    """Schema for creating a new todo item.

    Attributes:
        title: The text description of the task.
        due_date: Optional target completion date for the task.
    """

    title: str
    due_date: Optional[date] = None


class TodoUpdate(BaseModel):
    """Schema for partially updating an existing todo item.

    Attributes:
        title: New title text, if changing.
        completed: New completion state, if changing.
        due_date: New due date, if changing.
    """

    title: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[date] = None


class TodoResponse(BaseModel):
    """Schema returned by the API for a todo item.

    Attributes:
        id: Primary key.
        title: Task description.
        completed: Whether the task is done.
        created_at: UTC timestamp of creation.
        due_date: Optional target completion date.
    """

    id: int
    title: str
    completed: bool
    created_at: datetime
    due_date: Optional[date] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------

def get_db():
    """Provide a SQLAlchemy database session as a FastAPI dependency.

    Yields:
        Session: An active database session that is closed after the request.
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
    """Return all todo items ordered by creation date ascending.

    Args:
        db: Database session injected by FastAPI's dependency system.

    Returns:
        List of TodoResponse objects.
    """
    return db.query(Todo).order_by(Todo.created_at.asc()).all()


@app.post("/api/todos", response_model=TodoResponse, status_code=201)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo item.

    Args:
        payload: Request body containing title and optional due_date.
        db: Database session injected by FastAPI's dependency system.

    Returns:
        TodoResponse for the newly created item.
    """
    todo = Todo(title=payload.title, due_date=payload.due_date)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@app.patch("/api/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, payload: TodoUpdate, db: Session = Depends(get_db)):
    """Partially update an existing todo item.

    Args:
        todo_id: Path parameter identifying the todo.
        payload: Fields to update (title, completed, due_date).
        db: Database session injected by FastAPI's dependency system.

    Returns:
        Updated TodoResponse.

    Raises:
        HTTPException: 404 if no todo with the given id exists.
    """
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    if payload.title is not None:
        todo.title = payload.title
    if payload.completed is not None:
        todo.completed = payload.completed
    if payload.due_date is not None:
        todo.due_date = payload.due_date
    db.commit()
    db.refresh(todo)
    return todo


@app.delete("/api/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo item by id.

    Args:
        todo_id: Path parameter identifying the todo to delete.
        db: Database session injected by FastAPI's dependency system.

    Raises:
        HTTPException: 404 if no todo with the given id exists.
    """
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()


@app.get("/")
def serve_index():
    """Serve the frontend SPA index page.

    Returns:
        FileResponse for static/index.html.
    """
    return FileResponse("static/index.html")
