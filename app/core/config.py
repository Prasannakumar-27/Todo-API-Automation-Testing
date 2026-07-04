from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    target_api_base_url: str = "https://practice.expandtesting.com/notes/api"
    database_url: str = "sqlite:///./notes_history.db"
    reports_dir: str = "./reports"
    log_level: str = "INFO"
    default_test_user_name: str = "Automation User"
    default_test_user_password: str = "TestPass123!"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
