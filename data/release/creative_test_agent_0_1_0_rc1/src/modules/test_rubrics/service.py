from src.modules.test_rubrics.models import TestRubric
from src.modules.test_rubrics.schemas import (
    CreateTestRubricRequest,
    CriterionSchema,
    TestRubricResponse,
)
from src.shared.db.repository import db_session, json_dumps, json_loads


def _criteria_from_json(val: str | None) -> list[CriterionSchema]:
    data = json_loads(val)
    if not data:
        return _default_criteria()
    return [CriterionSchema(**c) if isinstance(c, dict) else CriterionSchema(name=c.get("name", ""), description=c.get("description", "")) for c in data]


def _criteria_to_json(criteria: list[CriterionSchema] | None) -> str | None:
    if criteria is None:
        return None
    return json_dumps([{"name": c.name, "description": c.description} for c in criteria])


def _default_criteria() -> list[CriterionSchema]:
    return [
        CriterionSchema(name="message_clarity", description="How clear is the core message?"),
        CriterionSchema(name="memorability", description="How memorable is the creative?"),
        CriterionSchema(name="audience_fit", description="How well does it fit the target audience?"),
        CriterionSchema(name="call_to_action", description="How effective is the call to action?"),
        CriterionSchema(name="trust", description="How trustworthy does the creative feel?"),
        CriterionSchema(name="brand_fit", description="How well does it align with the brand?"),
        CriterionSchema(name="negativity_risk", description="Risk of negative perception."),
        CriterionSchema(name="distinctiveness", description="How distinct is it from competitors?"),
    ]


def _to_response(r: TestRubric) -> TestRubricResponse:
    return TestRubricResponse(
        id=r.id,
        name=r.name,
        criteria=_criteria_from_json(r.criteria_json),
        scale_min=r.scale_min,
        scale_max=r.scale_max,
        metadata=json_loads(r.metadata_json) or {},
        created_at=r.created_at,
    )


def create_rubric(req: CreateTestRubricRequest) -> TestRubricResponse:
    with db_session() as db:
        rubric = TestRubric(
            name=req.name,
            criteria_json=_criteria_to_json(req.criteria),
            scale_min=req.scale_min or 1,
            scale_max=req.scale_max or 10,
            metadata_json=json_dumps(req.metadata),
        )
        db.add(rubric)
        db.flush()
        db.refresh(rubric)
        return _to_response(rubric)


def list_rubrics() -> list[TestRubricResponse]:
    with db_session() as db:
        rubrics = db.query(TestRubric).order_by(TestRubric.created_at.desc()).all()
        return [_to_response(r) for r in rubrics]


def get_rubric(rubric_id: str) -> TestRubricResponse | None:
    with db_session() as db:
        rubric = db.query(TestRubric).filter(TestRubric.id == rubric_id).first()
        if rubric is None:
            return None
        return _to_response(rubric)
