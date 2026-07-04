import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from functools import partial
import httpx
from app.core.config import settings
from app.db.database import SessionLocal, init_db
from app.db.models import ExecutionHistory
from app.schemas.test import StepResult, ExecutionSummary
from app.services.api_client import NotesAPIClient
from app.utils.logger import logger


class TestExecutionRunner:
    def __init__(self) -> None:
        init_db()
        os.makedirs(settings.reports_dir, exist_ok=True)
        self.api_client = NotesAPIClient()
        self.test_email: Optional[str] = None
        self.test_password: Optional[str] = None
        self.auth_token: Optional[str] = None
        self.note_id: Optional[str] = None

    async def run_full_sequence(self) -> Optional[Dict[str, Any]]:
        run_name = f"notes_api_automation_{datetime.utcnow().isoformat()}"
        started_at = datetime.utcnow()
        step_results: List[StepResult] = []
        self.test_email = f"automation+{int(datetime.utcnow().timestamp())}@example.com"
        self.test_password = settings.default_test_user_password
        self.auth_token = None
        self.note_id = None

        steps = [
            partial(self.register_user),
            partial(self.login_user),
            partial(self.create_note),
            partial(self.get_note),
            partial(self.update_note),
            partial(self.delete_note),
            partial(self.logout_user),
        ]

        for step in steps:
            step_name = getattr(step.func, "__name__", "step")
            try:
                result = await step()
                step_results.append(result)
                if step_name == "login_user" and result.passed:
                    response_data = json.loads(result.details or "{}")
                    self.auth_token = response_data.get("data", {}).get("token")
                if step_name == "create_note" and result.passed:
                    response_data = json.loads(result.details or "{}")
                    self.note_id = response_data.get("data", {}).get("id")
            except Exception as exc:
                logger.exception("Execution error during step %s", step_name)
                step_results.append(
                    StepResult(
                        step_name=step_name,
                        expected="Step completes successfully",
                        actual=str(exc),
                        passed=False,
                        status_code=None,
                        response_time_ms=0.0,
                        details=None,
                    )
                )
                break

        finished_at = datetime.utcnow()
        summary = self._build_summary(step_results, started_at, finished_at)
        report_path = self._save_report(run_name, started_at, finished_at, step_results, summary)
        execution_id = self._save_history(run_name, started_at, finished_at, summary, step_results, report_path)

        return {
            "execution_id": execution_id,
            "status": "passed" if summary.failed_steps == 0 else "failed",
            "summary": summary,
            "report_path": report_path,
        }

    async def load_execution_report(self, execution_id: int) -> Optional[Dict[str, Any]]:
        with SessionLocal() as session:
            history = session.get(ExecutionHistory, execution_id)
            if history is None:
                return None
            details = json.loads(history.details or "{}")
            return {
                "execution_id": history.id,
                "run_name": history.run_name,
                "status": history.status,
                "summary": details.get("summary", {}),
                "steps": details.get("steps", []),
                "report_path": history.report_path,
                "started_at": history.started_at,
                "finished_at": history.finished_at,
            }

    def _build_summary(self, steps: List[StepResult], started_at: datetime, finished_at: datetime) -> ExecutionSummary:
        passed_steps = sum(1 for step in steps if step.passed)
        total_steps = len(steps)
        duration_ms = (finished_at - started_at).total_seconds() * 1000
        return ExecutionSummary(
            total_steps=total_steps,
            passed_steps=passed_steps,
            failed_steps=total_steps - passed_steps,
            duration_ms=duration_ms,
        )

    def _save_report(self, run_name: str, started_at: datetime, finished_at: datetime, steps: List[StepResult], summary: ExecutionSummary) -> str:
        report_data = {
            "run_name": run_name,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "summary": summary.dict(),
            "steps": [step.dict() for step in steps],
        }
        report_filename_json = os.path.join(settings.reports_dir, f"{run_name}.json")
        report_filename_html = os.path.join(settings.reports_dir, f"{run_name}.html")
        with open(report_filename_json, "w", encoding="utf-8") as json_file:
            json.dump(report_data, json_file, indent=2)
        html_content = self._render_html_report(report_data)
        with open(report_filename_html, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)
        return report_filename_html

    def _render_html_report(self, report_data: Dict[str, Any]) -> str:
        rows = []
        for step in report_data["steps"]:
            status_label = "Passed" if step["passed"] else "Failed"
            rows.append(
                f"<tr><td>{step['step_name']}</td><td>{step['expected']}</td><td>{step['actual']}</td>"
                f"<td>{status_label}</td><td>{step['status_code'] or ''}</td><td>{step['response_time_ms']:.2f}</td></tr>"
            )
        return f"""
<html>
<head>
    <title>{report_data['run_name']} - Execution Report</title>
    <style>body{{font-family:Arial,sans-serif}}table{{width:100%;border-collapse:collapse}}th,td{{border:1px solid #ddd;padding:8px}}th{{background:#f4f4f4}}</style>
</head>
<body>
    <h1>Automation Execution Report</h1>
    <p><strong>Run:</strong> {report_data['run_name']}</p>
    <p><strong>Started:</strong> {report_data['started_at']}</p>
    <p><strong>Finished:</strong> {report_data['finished_at']}</p>
    <p><strong>Status:</strong> {"Passed" if report_data['summary']['failed_steps'] == 0 else "Failed"}</p>
    <p><strong>Steps:</strong> {report_data['summary']['total_steps']} | Passed: {report_data['summary']['passed_steps']} | Failed: {report_data['summary']['failed_steps']} | Duration(ms): {report_data['summary']['duration_ms']:.2f}</p>
    <table>
        <thead><tr><th>Step</th><th>Expected</th><th>Actual</th><th>Result</th><th>HTTP Status</th><th>Latency (ms)</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
    </table>
</body>
</html>
"""

    def _save_history(self, run_name: str, started_at: datetime, finished_at: datetime, summary: ExecutionSummary, steps: List[StepResult], report_path: str) -> int:
        details = json.dumps({"summary": summary.dict(), "steps": [step.dict() for step in steps]})
        with SessionLocal() as session:
            history = ExecutionHistory(
                run_name=run_name,
                started_at=started_at,
                finished_at=finished_at,
                status="passed" if summary.failed_steps == 0 else "failed",
                summary=json.dumps(summary.dict()),
                details=details,
                report_path=report_path,
            )
            session.add(history)
            session.commit()
            session.refresh(history)
            return history.id

    async def _create_step_result(self, step_name: str, expected: str, response: httpx.Response, actual: str) -> StepResult:
        return StepResult(
            step_name=step_name,
            expected=expected,
            actual=actual,
            passed=200 <= response.status_code < 300,
            status_code=response.status_code,
            response_time_ms=response.elapsed.total_seconds() * 1000,
            details=response.text,
        )

    async def register_user(self) -> StepResult:
        response = await self.api_client.register_user(settings.default_test_user_name, self.test_email, self.test_password)
        actual = response.json().get("message", response.text)
        return await self._create_step_result("register_user", "User registration should succeed", response, actual)

    async def login_user(self) -> StepResult:
        response = await self.api_client.login_user(self.test_email, self.test_password)
        actual = response.json().get("message", response.text)
        return await self._create_step_result("login_user", "Login should succeed and return a token", response, actual)

    async def create_note(self) -> StepResult:
        if not self.auth_token:
            raise RuntimeError("Create note requires authentication token")
        response = await self.api_client.create_note(
            self.auth_token,
            title="Automation note title",
            description="This note was created as part of an automated API test sequence.",
            category="Personal",
        )
        actual = response.json().get("message", response.text)
        return await self._create_step_result("create_note", "Note creation should succeed", response, actual)

    async def get_note(self) -> StepResult:
        if not self.auth_token or not self.note_id:
            raise RuntimeError("Get note requires auth token and note id")
        response = await self.api_client.get_note(self.auth_token, self.note_id)
        actual = response.json().get("message", response.text)
        return await self._create_step_result("get_note", "Retrieve the created note successfully", response, actual)

    async def update_note(self) -> StepResult:
        if not self.auth_token or not self.note_id:
            raise RuntimeError("Update note requires auth token and note id")
        response = await self.api_client.update_note(
            self.auth_token,
            self.note_id,
            title="Automation note title - updated",
            description="The note was updated by the automation suite.",
            category="Personal",
            completed=True,
        )
        actual = response.json().get("message", response.text)
        return await self._create_step_result("update_note", "Note update should succeed", response, actual)

    async def delete_note(self) -> StepResult:
        if not self.auth_token or not self.note_id:
            raise RuntimeError("Delete note requires auth token and note id")
        response = await self.api_client.delete_note(self.auth_token, self.note_id)
        actual = response.json().get("message", response.text)
        return await self._create_step_result("delete_note", "Note deletion should succeed", response, actual)

    async def logout_user(self) -> StepResult:
        if not self.auth_token:
            raise RuntimeError("Logout user requires auth token")
        response = await self.api_client.logout_user(self.auth_token)
        actual = response.json().get("message", response.text)
        return await self._create_step_result("logout_user", "Logout should succeed", response, actual)
