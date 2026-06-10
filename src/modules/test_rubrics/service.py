from uuid import uuid4

from src.modules.test_rubrics.models import Criterion, TestRubric
from src.modules.test_rubrics.schemas import (
    CreateTestRubricRequest,
    CriterionSchema,
    TestRubricResponse,
)

_store: dict[str, TestRubric] = {}


def _to_response(r: TestRubric) -> TestRubricResponse:
    return TestRubricResponse(
        id=r.id,
        name=r.name,
        criteria=[CriterionSchema(name=c.name, description=c.description) for c in r.criteria],
        scale_min=r.scale_min,
        scale_max=r.scale_max,
        created_at=r.created_at,
    )


def create_rubric(req: CreateTestRubricRequest) -> TestRubricResponse:
    criteria = None
    if req.criteria is not None:
        criteria = [Criterion(name=c.name, description=c.description) for c in req.criteria]
    rubric = TestRubric(
        rubric_id=str(uuid4()),
        name=req.name,
        criteria=criteria,
        scale_min=req.scale_min,
        scale_max=req.scale_max,
    )
    _store[rubric.id] = rubric
    return _to_response(rubric)


def list_rubrics() -> list[TestRubricResponse]:
    return [_to_response(r) for r in _store.values()]


def get_rubric(rubric_id: str) -> TestRubricResponse | None:
    rubric = _store.get(rubric_id)
    if rubric is None:
        return None
    return _to_response(rubric)
