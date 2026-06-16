"""
Load a pilot profile from a JSON file into the database.

Usage:
    python scripts/load_pilot_profile.py config/pilot_profiles/novabank_demo.json

Idempotent: entities are matched by name + profile_name in metadata.
"""

import json
import os
import sys

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.shared.db.repository import db_session, json_dumps
from src.shared.db.session import init_db
from src.modules.brand_profiles.models import BrandProfile
from src.modules.audience_profiles.models import AudienceProfile
from src.modules.creative_assets.models import CreativeAsset
from src.modules.test_rubrics.models import TestRubric
from src.modules.clients.models import Client
from src.modules.projects.models import Project


def _load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def _entity_exists(db, model, name_field: str, name_value: str, profile_name: str) -> bool:
    entities = db.query(model).all()
    for e in entities:
        meta = json.loads(e.metadata_json) if e.metadata_json else {}
        if meta.get("profile_name") == profile_name:
            existing_name = getattr(e, name_field, None)
            if existing_name == name_value:
                return True
    return False


def load_profile(json_path: str, profile_name: str | None = None) -> int:
    profile = _load_json(json_path)
    effective_profile_name = profile_name or profile.get("profile_name") or "custom"
    metadata_base = {"profile_name": effective_profile_name}
    created = 0

    init_db()

    # ── Brand Profile ──────────────────────────────────────────────
    brand = profile.get("brand")
    if brand and brand.get("name"):
        with db_session() as db:
            if not _entity_exists(db, BrandProfile, "name", brand["name"], effective_profile_name):
                db.add(BrandProfile(
                    name=brand["name"],
                    tone_of_voice=brand.get("tone_of_voice"),
                    target_audience=brand.get("target_audience"),
                    restrictions=brand.get("restrictions"),
                    claims_policy=brand.get("claims_policy"),
                    metadata_json=json_dumps({**metadata_base, "demo": profile.get("demo", False)}),
                ))
                print(f"  ✓ Brand profile '{brand['name']}' created.")
                created += 1
            else:
                print(f"  ✓ Brand profile '{brand['name']}' already exists, skipping.")

    # ── Audience Profiles ───────────────────────────────────────────
    for adef in profile.get("audiences", []):
        with db_session() as db:
            if not _entity_exists(db, AudienceProfile, "name", adef["name"], effective_profile_name):
                db.add(AudienceProfile(
                    name=adef["name"],
                    segment_description=adef.get("segment_description"),
                    pains=adef.get("pains"),
                    motivations=adef.get("motivations"),
                    objections=adef.get("objections"),
                    metadata_json=json_dumps({**metadata_base, "demo": profile.get("demo", False)}),
                ))
                print(f"  ✓ Audience profile '{adef['name']}' created.")
                created += 1
            else:
                print(f"  ✓ Audience profile '{adef['name']}' already exists, skipping.")

    # ── Rubric ──────────────────────────────────────────────────────
    rubric = profile.get("rubric")
    if rubric and rubric.get("name"):
        with db_session() as db:
            if not _entity_exists(db, TestRubric, "name", rubric["name"], effective_profile_name):
                criteria_list = rubric.get("criteria", [])
                db.add(TestRubric(
                    name=rubric["name"],
                    criteria_json=json_dumps(criteria_list),
                    scale_min=rubric.get("scale_min", 1),
                    scale_max=rubric.get("scale_max", 10),
                    metadata_json=json_dumps({**metadata_base, "demo": profile.get("demo", False)}),
                ))
                print(f"  ✓ Rubric '{rubric['name']}' created with {len(criteria_list)} criteria.")
                created += 1
            else:
                print(f"  ✓ Rubric '{rubric['name']}' already exists, skipping.")

    # ── Client ─────────────────────────────────────────────────────
    client_obj = profile.get("client")
    client_id = None
    if client_obj and client_obj.get("name"):
        with db_session() as db:
            if not _entity_exists(db, Client, "name", client_obj["name"], effective_profile_name):
                db_client = Client(
                    name=client_obj["name"],
                    industry=client_obj.get("industry"),
                    description=client_obj.get("description"),
                    metadata_json=json_dumps({**metadata_base, "demo": profile.get("demo", False)}),
                )
                db.add(db_client)
                db.flush()
                db.refresh(db_client)
                client_id = db_client.id
                print(f"  ✓ Client '{client_obj['name']}' created (id={client_id[:12]}...).")
                created += 1
            else:
                existing = db.query(Client).all()
                for e in existing:
                    meta = json.loads(e.metadata_json) if e.metadata_json else {}
                    if meta.get("profile_name") == effective_profile_name and e.name == client_obj["name"]:
                        client_id = e.id
                        break
                print(f"  ✓ Client '{client_obj['name']}' already exists, skipping.")

    # ── Project ─────────────────────────────────────────────────────
    project_def = profile.get("project")
    if project_def and project_def.get("name") and client_id:
        with db_session() as db:
            if not _entity_exists(db, Project, "name", project_def["name"], effective_profile_name):
                db.add(Project(
                    client_id=client_id,
                    name=project_def["name"],
                    description=project_def.get("description"),
                    metadata_json=json_dumps({**metadata_base, "demo": profile.get("demo", False)}),
                ))
                print(f"  ✓ Project '{project_def['name']}' created.")
                created += 1
            else:
                print(f"  ✓ Project '{project_def['name']}' already exists, skipping.")

    # ── Creative Assets ─────────────────────────────────────────────
    for adef in profile.get("creative_assets", []):
        with db_session() as db:
            if not _entity_exists(db, CreativeAsset, "title", adef["title"], effective_profile_name):
                asset_meta = {**metadata_base, "demo": profile.get("demo", False)}
                if adef.get("variant"):
                    asset_meta["variant"] = adef["variant"]
                if adef.get("variant_description"):
                    asset_meta["variant_description"] = adef["variant_description"]
                db.add(CreativeAsset(
                    title=adef["title"],
                    asset_type=adef.get("asset_type", "text"),
                    text_content=adef.get("text_content"),
                    metadata_json=json_dumps(asset_meta),
                ))
                print(f"  ✓ Creative asset '{adef['title']}' created.")
                created += 1
            else:
                print(f"  ✓ Creative asset '{adef['title']}' already exists, skipping.")

    return created


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/load_pilot_profile.py <path_to_json> [profile_name]")
        sys.exit(1)

    json_path = sys.argv[1]
    if not os.path.isfile(json_path):
        print(f"File not found: {json_path}")
        sys.exit(1)

    profile_name = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Loading pilot profile from: {json_path}")
    created = load_profile(json_path, profile_name)
    if created:
        print(f"\nCreated {created} new entit(ies).")
    else:
        print("\nAll entities already exist — nothing new to create.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
