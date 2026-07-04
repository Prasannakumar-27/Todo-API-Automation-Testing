from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models_todo import TodoItem
from app.schemas.todo import TodoCreate, TodoUpdate


class TodoService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_todo(self, payload: TodoCreate) -> TodoItem:
        todo = TodoItem(
            title=payload.title,
            description=payload.description,
            completed=payload.completed,
        )
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def get_todo(self, todo_id: int) -> Optional[TodoItem]:
        return self.session.get(TodoItem, todo_id)

    def list_todos(self) -> List[TodoItem]:
        return self.session.query(TodoItem).order_by(TodoItem.id).all()

    def update_todo(self, todo_id: int, payload: TodoUpdate) -> Optional[TodoItem]:
        todo = self.get_todo(todo_id)
        if todo is None:
            return None
        if payload.title is not None:
            todo.title = payload.title
        if payload.description is not None:
            todo.description = payload.description
        if payload.completed is not None:
            todo.completed = payload.completed
        todo.updated_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def delete_todo(self, todo_id: int) -> bool:
        todo = self.get_todo(todo_id)
        if todo is None:
            return False
        self.session.delete(todo)
        self.session.commit()
        return True
