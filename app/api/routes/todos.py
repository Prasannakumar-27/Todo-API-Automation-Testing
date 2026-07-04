from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.todo import TodoCreate, TodoUpdate, TodoRead
from app.services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["Todos"])


def get_db():
    with SessionLocal() as session:
        yield session


@router.post("/", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    service = TodoService(db)
    todo = service.create_todo(payload)
    return todo


@router.get("/", response_model=list[TodoRead])
async def list_todos(db: Session = Depends(get_db)):
    service = TodoService(db)
    return service.list_todos()


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(todo_id: int, db: Session = Depends(get_db)):
    service = TodoService(db)
    todo = service.get_todo(todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.put("/{todo_id}", response_model=TodoRead)
async def update_todo(todo_id: int, payload: TodoUpdate, db: Session = Depends(get_db)):
    service = TodoService(db)
    todo = service.update_todo(todo_id, payload)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    service = TodoService(db)
    deleted = service.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return {"detail": "Todo deleted successfully"}
