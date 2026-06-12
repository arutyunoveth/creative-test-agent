"""Prompt registry tests."""

import pytest
from pathlib import Path
from src.shared.db.session import init_db


@pytest.fixture(autouse=True)
def _db():
    init_db()
    yield


def test_list_empty():
    from src.modules.prompt_registry.service import list_prompts
    assert list_prompts() == []


def test_register_and_get(tmp_path):
    from src.modules.prompt_registry.service import register_prompt, get_active_prompt
    f = tmp_path / "creative_summary.md"
    f.write_text("Summarize this creative.")
    pv = register_prompt(stage_name="creative_summary", template_path=str(f))
    assert pv.stage_name == "creative_summary"
    assert len(pv.template_hash) == 64


def test_get_active_prompt(tmp_path):
    from src.modules.prompt_registry.service import register_prompt, get_active_prompt
    f = tmp_path / "audience_simulation.md"
    f.write_text("Simulate audience.")
    register_prompt(stage_name="audience_simulation", template_path=str(f))
    active = get_active_prompt("audience_simulation")
    assert active is not None
    assert active.stage_name == "audience_simulation"


def test_get_active_prompt_none():
    from src.modules.prompt_registry.service import get_active_prompt
    active = get_active_prompt("nonexistent_stage")
    assert active is None


def test_get_active_prompt_not_active(tmp_path):
    from src.modules.prompt_registry.service import register_prompt, get_active_prompt
    f = tmp_path / "inactive.md"
    f.write_text("Not active.")
    register_prompt(stage_name="inactive_stage", template_path=str(f))
    active = get_active_prompt("inactive_stage")
    assert active is not None  # first registered is auto-active
    from src.modules.prompt_registry.models import PromptVersion
    from src.shared.db.repository import db_session
    with db_session() as db:
        pv = db.query(PromptVersion).filter(PromptVersion.stage_name == "inactive_stage").first()
        pv.is_active = False
        db.flush()
    active2 = get_active_prompt("inactive_stage")
    assert active2 is None


def test_register_multiple_versions(tmp_path):
    from src.modules.prompt_registry.service import register_prompt, list_prompts
    f1 = tmp_path / "test_stage_v1.md"
    f1.write_text("v1 content")
    v1 = register_prompt(stage_name="test_stage", template_path=str(f1), version="1.0")
    f2 = tmp_path / "test_stage_v2.md"
    f2.write_text("v2 content")
    v2 = register_prompt(stage_name="test_stage", template_path=str(f2), version="2.0")
    prompts = list_prompts()
    ids = {p.id for p in prompts}
    assert v1.id in ids
    assert v2.id in ids


def test_dedup_same_content(tmp_path):
    from src.modules.prompt_registry.service import register_prompt
    f1 = tmp_path / "dedup1.md"
    f1.write_text("same content")
    v1 = register_prompt(stage_name="dedup_test", template_path=str(f1), version="1.0")
    f2 = tmp_path / "dedup2.md"
    f2.write_text("same content")
    v2 = register_prompt(stage_name="dedup_test", template_path=str(f2), version="1.0")
    assert v1.id == v2.id


def test_dedup_different_content(tmp_path):
    from src.modules.prompt_registry.service import register_prompt
    f1 = tmp_path / "dedup_a.md"
    f1.write_text("content a")
    v1 = register_prompt(stage_name="dedup_test2", template_path=str(f1), version="1.0")
    f2 = tmp_path / "dedup_b.md"
    f2.write_text("content b")
    v2 = register_prompt(stage_name="dedup_test2", template_path=str(f2), version="1.0")
    assert v1.id != v2.id


def test_prompt_version_model(tmp_path):
    from src.modules.prompt_registry.service import register_prompt
    from src.modules.prompt_registry.models import PromptVersion
    f = tmp_path / "brand_safety.md"
    f.write_text("Check brand safety.")
    pv = register_prompt(stage_name="brand_safety_review", template_path=str(f), version="1.0")
    assert isinstance(pv.id, str)


def test_get_prompt_hash():
    from src.modules.prompt_registry.service import get_prompt_hash
    h = get_prompt_hash("test_stage", "hello world")
    assert len(h) == 64
    assert isinstance(h, str)
