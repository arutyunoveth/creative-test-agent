from httpx import ASGITransport, AsyncClient
from src.main import app
from src.shared.config.settings import get_settings


async def test_batch_docs_exist():
    import os
    assert os.path.isfile("docs/batch_testing.md")
    assert os.path.isfile("docs/local_job_queue.md")
    assert os.path.isfile("docs/campaign_summary_reports.md")


async def test_batch_docs_have_content():
    with open("docs/batch_testing.md") as f:
        assert len(f.read()) > 100
    with open("docs/local_job_queue.md") as f:
        assert len(f.read()) > 100
    with open("docs/campaign_summary_reports.md") as f:
        assert len(f.read()) > 100


async def test_demo_batch_script_imports():
    import scripts.run_demo_batch
    assert hasattr(scripts.run_demo_batch, "main")
