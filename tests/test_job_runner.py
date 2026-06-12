from httpx import ASGITransport, AsyncClient
from src.main import app

_UNIQUE_JOB_TYPE = "runner_test_job"


async def test_runner_run_next_no_jobs():
    from src.modules.job_queue.runner import run_next_job
    result = run_next_job(job_type=_UNIQUE_JOB_TYPE)
    assert result["processed"] is False


async def test_runner_run_next_processes_job():
    from src.modules.job_queue.runner import run_next_job
    from src.modules.job_queue.service import enqueue_job

    enqueue_job(_UNIQUE_JOB_TYPE, payload={"test_run_id": "fake"}, max_attempts=1)
    result = run_next_job(job_type=_UNIQUE_JOB_TYPE)
    assert result["processed"] is True
    assert result["job_id"] is not None


async def test_runner_run_pending_jobs():
    from src.modules.job_queue.runner import run_pending_jobs
    from src.modules.job_queue.service import enqueue_job

    enqueue_job(_UNIQUE_JOB_TYPE, payload={"test_run_id": "fake"}, max_attempts=1)
    results = run_pending_jobs(limit=5)
    assert len(results) >= 1
