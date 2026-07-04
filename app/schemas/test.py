from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class StepResult(BaseModel):
    step_name: str
    expected: str
    actual: str
    passed: bool
    status_code: Optional[int]
    response_time_ms: float
    details: Optional[str] = None


class ExecutionSummary(BaseModel):
    total_steps: int
    passed_steps: int
    failed_steps: int
    duration_ms: float


class ExecutionCreateResponse(BaseModel):
    execution_id: int
    status: str
    summary: ExecutionSummary
    report_path: str


class ExecutionResultResponse(BaseModel):
    execution_id: int
    run_name: str
    status: str
    summary: ExecutionSummary
    steps: List[StepResult]
    report_path: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]
