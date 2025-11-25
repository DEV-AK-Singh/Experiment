from turtle import mode
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

# Create all database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="Simple Todo API", version="1.0.0") 

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Todo API"}

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Get all todos
@app.get("/todos", response_model=List[schemas.TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()
    return todos

# Create a new todo
@app.post("/todos", response_model=schemas.TodoResponse)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    db_todo = models.Todo(
        title=todo.title,
        description=todo.description,
        completed=False
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Get a specific todo
@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

# Update a todo
@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo_update: schemas.TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first() 
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found") 
    if todo_update.title is not None:
        db_todo.title = models.Todo(title=todo_update.title).title
    if todo_update.description is not None:
        db_todo.description = models.Todo(description=todo_update.description).description
    if todo_update.completed is not None:
        db_todo.completed = models.Todo(completed=todo_update.completed).completed
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Delete a todo
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found") 
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}