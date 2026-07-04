from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.db.database import init_db
from app.utils.logger import logger

app = FastAPI(
    title="Notes API Automation Backend",
    description="Backend service to automate Notes API end-to-end tests and generate execution reports.",
    version="0.1.0",
    swagger_ui_init_oauth={"appName": "API Testing Practice"},
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Docs",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        init_oauth=None,
        extra_js=["/static/docs_banner.js"],
    )


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting Notes API Automation Backend")
    init_db()


@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {"message": "Notes API automation backend is running."}
