"""
Seed demo data for the Creative Test Agent pilot demo.

Creates demo entities via the running API server.

Usage:
    # First start the server
    uvicorn src.main:app --reload

    # Then run this script
    python scripts/seed_demo_data.py

Safe to run multiple times — uses idempotent checks via metadata.
"""

import sys
import os
import json

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import httpx
except ImportError:
    print("httpx is required. Install with: pip install httpx")
    sys.exit(1)

BASE_URL = os.environ.get("CTA_DEMO_BASE_URL", "http://localhost:8000")
DEMO_METADATA = {"demo": True, "demo_scenario": "novabank_freelancer_card"}


def _is_demo_entity(entity: dict) -> bool:
    meta = entity.get("metadata") or {}
    return meta.get("demo") is True


def _find_by_name(items: list[dict], name: str) -> dict | None:
    for item in items:
        if item.get("name") == name or item.get("title") == name:
            return item
    return None


def seed_demo_data() -> bool:
    seeded = False

    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        # ── Brand Profile ──────────────────────────────────────────
        brands = client.get("/brand-profiles").json()
        if _find_by_name(brands, "NovaBank"):
            print("✓ Brand profile 'NovaBank' already exists, skipping.")
        else:
            resp = client.post(
                "/brand-profiles",
                json={
                    "name": "NovaBank",
                    "tone_of_voice": "Clear, practical, trustworthy, calm, not aggressive.",
                    "target_audience": "Freelancers, self-employed professionals and small business owners who need simple financial tools.",
                    "restrictions": "No exaggerated claims. No 'guaranteed income'. No 'zero risk'. No pressure language. No hidden-fee ambiguity.",
                    "claims_policy": "Every benefit should be framed as a product feature, not as a guaranteed financial outcome.",
                },
            )
            resp.raise_for_status()
            print("✓ Brand profile 'NovaBank' created.")
            seeded = True

        # ── Audience Profiles ──────────────────────────────────────
        audiences = client.get("/audience-profiles").json()

        audience_defs = [
            {
                "name": "Beginner Freelancer",
                "segment_description": "Начинающий фрилансер, недавно ушёл из найма или совмещает работу с подработками.",
                "pains": "Сложно отделять личные и рабочие деньги. Нет уверенности в налогах. Боится банковских комиссий.",
                "motivations": "Простота. Прозрачность. Быстрый старт.",
                "objections": "Не хочет сложных финансовых продуктов. Не доверяет 'банковскому маркетингу'.",
            },
            {
                "name": "Experienced Self-Employed Specialist",
                "segment_description": "Самозанятый специалист с постоянными клиентами.",
                "pains": "Много платежей от разных клиентов. Нужен контроль расходов. Важно быстро видеть финансовую картину.",
                "motivations": "Удобство. Аналитика. Экономия времени.",
                "objections": "Не хочет менять привычный банк без сильной причины.",
            },
            {
                "name": "Skeptical Small Business Owner",
                "segment_description": "Владелец малого бизнеса, осторожно относится к новым финансовым сервисам.",
                "pains": "Боится скрытых условий. Не доверяет слишком громким обещаниям. Хочет понятные тарифы.",
                "motivations": "Надёжность. Контроль. Снижение рисков.",
                "objections": "'Слишком хорошо, чтобы быть правдой'. Опасается мелкого шрифта.",
            },
        ]

        for adef in audience_defs:
            if _find_by_name(audiences, adef["name"]):
                print(f"✓ Audience profile '{adef['name']}' already exists, skipping.")
            else:
                resp = client.post("/audience-profiles", json=adef)
                resp.raise_for_status()
                print(f"✓ Audience profile '{adef['name']}' created.")
                seeded = True

        # ── Rubric ─────────────────────────────────────────────────
        rubrics = client.get("/test-rubrics").json()
        rubric_name = "Default Creative Pre-Test Rubric"
        if _find_by_name(rubrics, rubric_name):
            print(f"✓ Rubric '{rubric_name}' already exists, skipping.")
        else:
            resp = client.post(
                "/test-rubrics",
                json={
                    "name": rubric_name,
                    "criteria": [
                        {"name": "message_clarity", "description": "How clear and understandable is the core message?"},
                        {"name": "memorability", "description": "How likely is the creative to be remembered?"},
                        {"name": "audience_fit", "description": "How well does the creative resonate with the target audience?"},
                        {"name": "call_to_action", "description": "How effective and compelling is the call to action?"},
                        {"name": "trust", "description": "Does the creative build or erode trust?"},
                        {"name": "brand_fit", "description": "How well does the creative align with the brand's tone and guidelines?"},
                        {"name": "negativity_risk", "description": "Risk of negative perception or backlash."},
                        {"name": "distinctiveness", "description": "How distinctive is the creative compared to competitors?"},
                    ],
                    "scale_min": 1,
                    "scale_max": 10,
                },
            )
            resp.raise_for_status()
            print(f"✓ Rubric '{rubric_name}' created.")
            seeded = True

        # ── Creative Assets ────────────────────────────────────────
        assets = client.get("/creative-assets").json()

        asset_defs = [
            {
                "title": "NovaBank Freelancer Card — Practical Variant",
                "asset_type": "text",
                "text_content": "Headline:\nOne card for your freelance income and expenses.\n\nBody:\nReceive client payments, separate work expenses and keep your freelance finances clear in one simple account.\n\nCTA:\nOpen your freelancer account.",
                "metadata": {**DEMO_METADATA, "variant": "A", "variant_description": "clear/practical"},
            },
            {
                "title": "NovaBank Freelancer Card — Freedom Variant",
                "asset_type": "text",
                "text_content": "Headline:\nYour freelance money, finally under control.\n\nBody:\nSpend less time sorting payments and more time doing the work you love. NovaBank helps you keep income, expenses and taxes easier to manage.\n\nCTA:\nStart managing your freelance money.",
                "metadata": {**DEMO_METADATA, "variant": "B", "variant_description": "emotional/freedom"},
            },
            {
                "title": "NovaBank Freelancer Card — Risky Variant",
                "asset_type": "text",
                "text_content": "Headline:\nThe only card freelancers will ever need.\n\nBody:\nForget financial stress forever. NovaBank guarantees full control over your money with zero hassle and no risks.\n\nCTA:\nJoin now.",
                "metadata": {**DEMO_METADATA, "variant": "C", "variant_description": "risky/overclaim"},
            },
        ]

        for adef in asset_defs:
            if _find_by_name(assets, adef["title"]):
                print(f"✓ Creative asset '{adef['title']}' already exists, skipping.")
            else:
                resp = client.post("/creative-assets", json=adef)
                resp.raise_for_status()
                print(f"✓ Creative asset '{adef['title']}' created.")
                seeded = True

    return seeded


if __name__ == "__main__":
    seeded = seed_demo_data()
    if seeded:
        print("\nDemo data seeded successfully.")
    else:
        print("\nAll demo data already exists — nothing new to seed.")
    print("Open UI: http://localhost:8000/")
    print("Recommended next step: create or run test runs for demo creative variants.")
