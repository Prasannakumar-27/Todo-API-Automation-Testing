from typing import Any, Dict, Optional
import httpx
from app.core.config import settings
from app.utils.logger import logger


class APIClientError(Exception):
    pass


class NotesAPIClient:
    def __init__(self) -> None:
        base_url = str(settings.target_api_base_url)
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def request(self, method: str, path: str, headers: Optional[Dict[str, str]] = None, data: Optional[Dict[str, Any]] = None) -> httpx.Response:
        try:
            request_method = getattr(self.client, method.lower())
            response = await request_method(path, headers=headers or {}, data=data or {})
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            logger.error("API request failed: %s %s -> %s", method, path, exc.response.text)
            raise APIClientError(f"{method.upper()} {path} failed with status {exc.response.status_code}: {exc.response.text}")
        except httpx.RequestError as exc:
            logger.error("Request error for %s %s: %s", method, path, exc)
            raise APIClientError(f"Request error: {str(exc)}")

    async def register_user(self, name: str, email: str, password: str) -> httpx.Response:
        return await self.request("post", "/users/register", data={"name": name, "email": email, "password": password})

    async def login_user(self, email: str, password: str) -> httpx.Response:
        return await self.request("post", "/users/login", data={"email": email, "password": password})

    async def logout_user(self, token: str) -> httpx.Response:
        return await self.request("delete", "/users/logout", headers={"x-auth-token": token})

    async def delete_account(self, token: str) -> httpx.Response:
        return await self.request("delete", "/users/delete-account", headers={"x-auth-token": token})

    async def create_note(self, token: str, title: str, description: str, category: str) -> httpx.Response:
        return await self.request("post", "/notes", headers={"x-auth-token": token}, data={"title": title, "description": description, "category": category})

    async def get_all_notes(self, token: str) -> httpx.Response:
        return await self.request("get", "/notes", headers={"x-auth-token": token})

    async def get_note(self, token: str, note_id: str) -> httpx.Response:
        return await self.request("get", f"/notes/{note_id}", headers={"x-auth-token": token})

    async def update_note(self, token: str, note_id: str, title: str, description: str, category: str, completed: bool) -> httpx.Response:
        return await self.request(
            "put",
            f"/notes/{note_id}",
            headers={"x-auth-token": token},
            data={"title": title, "description": description, "category": category, "completed": completed},
        )

    async def delete_note(self, token: str, note_id: str) -> httpx.Response:
        return await self.request("delete", f"/notes/{note_id}", headers={"x-auth-token": token})
