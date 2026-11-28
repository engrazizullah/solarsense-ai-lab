"""The scheduler registers the daily pipeline job correctly."""

from app.core.scheduler import JOB_ID, start_scheduler


def test_daily_job_is_registered_for_0630() -> None:
    scheduler = start_scheduler()
    try:
        job = scheduler.get_job(JOB_ID)
        assert job is not None
        assert job.max_instances == 1
        assert job.next_run_time.hour == 6
        assert job.next_run_time.minute == 30
    finally:
        scheduler.shutdown(wait=False)
