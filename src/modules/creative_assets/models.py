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
        extracted_text: str | None = None,
        original_filename: str | None = None,
        mime_type: str | None = None,
        file_size_bytes: int | None = None,
    ):
        self.id = asset_id
        self.title = title
        self.asset_type = asset_type
        self.text_content = text_content
        self.file_path = file_path
        self.metadata = metadata or {}
        self.extracted_text = extracted_text
        self.original_filename = original_filename
        self.mime_type = mime_type
        self.file_size_bytes = file_size_bytes
        self.created_at = datetime.now(timezone.utc)
