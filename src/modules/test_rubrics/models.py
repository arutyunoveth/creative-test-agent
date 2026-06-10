from datetime import datetime, timezone


class Criterion:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description


class TestRubric:
    def __init__(
        self,
        rubric_id: str,
        name: str,
        criteria: list[Criterion] | None = None,
        scale_min: int = 1,
        scale_max: int = 10,
    ):
        self.id = rubric_id
        self.name = name
        self.criteria = criteria or _DEFAULT_CRITERIA
        self.scale_min = scale_min
        self.scale_max = scale_max
        self.created_at = datetime.now(timezone.utc)


_DEFAULT_CRITERIA = [
    Criterion("message_clarity", "How clear is the core message?"),
    Criterion("memorability", "How memorable is the creative?"),
    Criterion("audience_fit", "How well does it fit the target audience?"),
    Criterion("call_to_action", "How effective is the call to action?"),
    Criterion("trust", "How trustworthy does the creative feel?"),
    Criterion("brand_fit", "How well does it align with the brand?"),
    Criterion("negativity_risk", "Risk of negative perception."),
    Criterion("distinctiveness", "How distinct is it from competitors?"),
]
