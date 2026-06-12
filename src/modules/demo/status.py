"""Demo status detector — inspects DB for demo readiness."""

from src.modules.audience_profiles.service import list_profiles as list_audience
from src.modules.brand_profiles.service import list_profiles as list_brand
from src.modules.brandbooks.service import list_brandbooks
from src.modules.batches.service import list_batches
from src.modules.clients.service import list_clients
from src.modules.creative_assets.service import list_assets
from src.modules.knowledge_base.service import list_knowledge_items
from src.modules.projects.service import list_projects
from src.modules.report_generator.models import Report
from src.modules.reviews.service import list_reviews
from src.shared.db.repository import db_session


def get_demo_status() -> dict:
    clients = list_clients()
    projects = list_projects()
    assets = list_assets()
    brandbooks = list_brandbooks()
    brand_profiles = list_brand()
    audience_profiles = list_audience()
    batches = list_batches()
    reviews = list_reviews()
    knowledge = list_knowledge_items()

    client_exists = len(clients) > 0
    project_exists = len(projects) > 0
    creatives_count = len(assets)
    brandbooks_count = len(brandbooks)
    brand_profiles_count = len(brand_profiles)
    audience_profiles_count = len(audience_profiles)
    batch_exists = len(batches) > 0
    batch_completed = any(getattr(b, "status", "") == "completed" for b in batches)

    with db_session() as db:
        reports_count = db.query(Report).count()

    reviews_count = len(reviews)
    knowledge_count = len(knowledge)

    next_action = "Create a client"
    if not client_exists:
        next_action = "Load demo profile or create a client"
    elif not project_exists:
        next_action = "Create a project"
    elif creatives_count == 0:
        next_action = "Upload creative assets"
    elif brandbooks_count == 0:
        next_action = "Upload a brandbook"
    elif not batch_exists:
        next_action = "Create a batch test"
    elif not batch_completed:
        next_action = "Run the batch test"
    elif reviews_count == 0:
        next_action = "Create a review"
    else:
        next_action = "Export a report or build client pack"

    return {
        "profile_loaded": client_exists or project_exists or creatives_count > 0,
        "client_exists": client_exists,
        "project_exists": project_exists,
        "creatives_count": creatives_count,
        "brandbooks_count": brandbooks_count,
        "brand_profiles_count": brand_profiles_count,
        "audience_profiles_count": audience_profiles_count,
        "batch_exists": batch_exists,
        "batch_completed": batch_completed,
        "reports_count": reports_count,
        "exports_count": 0,
        "reviews_count": reviews_count,
        "knowledge_items_count": knowledge_count,
        "next_recommended_action": next_action,
    }
