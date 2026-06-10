from fastapi import APIRouter, HTTPException

from src.modules.test_rubrics.schemas import (
    CreateTestRubricRequest,
    TestRubricResponse,
)
from src.modules.test_rubrics.service import create_rubric, get_rubric, list_rubrics

router = APIRouter(prefix="/test-rubrics", tags=["test-rubrics"])


@router.post("", response_model=TestRubricResponse, status_code=201)
def post_create_rubric(body: CreateTestRubricRequest):
    return create_rubric(body)


@router.get("", response_model=list[TestRubricResponse])
def get_rubrics():
    return list_rubrics()


@router.get("/{rubric_id}", response_model=TestRubricResponse)
def get_rubric_by_id(rubric_id: str):
    rubric = get_rubric(rubric_id)
    if rubric is None:
        raise HTTPException(status_code=404, detail="Rubric not found")
    return rubric
