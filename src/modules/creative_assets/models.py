from datetime import datetime, timezone


class CreativeAsset:
    def __init__(
        self,
        asset_id: str,
        title: str,
        asset_type: str,
        text_content: str | None = None,
        file_path: str | None = None,
        metadata: dict | None = None,
    ):
        self.id = asset_id
        self.title = title
        self.asset_type = asset_type
        self.text_content = text_content
        self.file_path = file_path
        self.metadata = metadata or {}
        self.created_at = datetime.now(timezone.utc)
