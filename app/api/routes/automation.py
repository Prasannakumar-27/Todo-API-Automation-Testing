from fastapi import APIRouter, HTTPException, status
from app.services.test_runner import TestExecutionRunner
from app.schemas.test import ExecutionCreateResponse, ExecutionResultResponse

router = APIRouter()

runner = TestExecutionRunner()

@router.post("/run-tests", response_model=ExecutionCreateResponse)
async def run_tests():
    result = await runner.run_full_sequence()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute automation sequence",
        )
    return result

@router.get("/report/{execution_id}", response_model=ExecutionResultResponse)
async def get_report(execution_id: int):
    report = await runner.load_execution_report(execution_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")
    return report
