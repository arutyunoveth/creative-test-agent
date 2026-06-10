from datetime import datetime, timezone


class BrandProfile:
    def __init__(
        self,
        profile_id: str,
        name: str,
        tone_of_voice: str | None = None,
        target_audience: str | None = None,
        restrictions: str | None = None,
        claims_policy: str | None = None,
    ):
        self.id = profile_id
        self.name = name
        self.tone_of_voice = tone_of_voice
        self.target_audience = target_audience
        self.restrictions = restrictions
        self.claims_policy = claims_policy
        self.created_at = datetime.now(timezone.utc)
