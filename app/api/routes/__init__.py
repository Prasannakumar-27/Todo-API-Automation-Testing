from fastapi import APIRouter

router = APIRouter()

from app.api.routes import health, todos  # noqa: F401

router.include_router(health.router, prefix="", tags=["Health"])
router.include_router(todos.router, prefix="", tags=["Todos"])
