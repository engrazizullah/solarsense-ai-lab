"""Run the weather pipeline every morning (in-app scheduler)."""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.db.session import get_engine
from app.services.pipeline import run_pipeline

logger = logging.getLogger(__name__)
JOB_ID = "weather_pipeline"


def run_pipeline_job() -> None:
    """One scheduled run: fetch recent weather for every city."""
    with Session(get_engine()) as session:
        results = run_pipeline(session)
    logger.info("Weather pipeline finished: %s", results)


def start_scheduler() -> BackgroundScheduler:
    """Start a background scheduler that runs the pipeline daily at 06:30 PKT."""
    scheduler = BackgroundScheduler(timezone="Asia/Karachi")
    scheduler.add_job(
        run_pipeline_job,
        CronTrigger(hour=6, minute=30),
        id=JOB_ID,
        replace_existing=True,
        max_instances=1,  # never two runs at the same time
        coalesce=True,  # if runs were missed (Mac asleep), do just one catch-up
    )
    scheduler.start()
    logger.info(
        "Scheduler started; next run at %s", scheduler.get_job(JOB_ID).next_run_time
    )
    return scheduler
