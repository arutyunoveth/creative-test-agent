from datetime import datetime, timezone


class AudienceProfile:
    def __init__(
        self,
        profile_id: str,
        name: str,
        segment_description: str,
        pains: str | None = None,
        motivations: str | None = None,
        objections: str | None = None,
    ):
        self.id = profile_id
        self.name = name
        self.segment_description = segment_description
        self.pains = pains
        self.motivations = motivations
        self.objections = objections
        self.created_at = datetime.now(timezone.utc)
