"""
Dagster schedules for Telegram Medical Data Pipeline
"""
from dagster import ScheduleDefinition, DefaultScheduleStatus

# Daily schedule - runs the full pipeline every day at 6 AM
daily_schedule = ScheduleDefinition(
    job_name="full_pipeline_job",
    cron_schedule="0 6 * * *",  # Every day at 6:00 AM
    name="daily_pipeline_schedule",
    description="Run the complete pipeline daily at 6 AM",
    default_status=DefaultScheduleStatus.RUNNING
)

# Telegram data schedule - scrapes data every 4 hours
telegram_schedule = ScheduleDefinition(
    job_name="telegram_pipeline_job",
    cron_schedule="0 */4 * * *",  # Every 4 hours
    name="telegram_data_schedule",
    description="Scrape Telegram data every 4 hours",
    default_status=DefaultScheduleStatus.RUNNING
)

# dbt schedule - runs transformations every 6 hours
dbt_schedule = ScheduleDefinition(
    job_name="dbt_job",
    cron_schedule="0 */6 * * *",  # Every 6 hours
    name="dbt_transformation_schedule",
    description="Run dbt transformations every 6 hours",
    default_status=DefaultScheduleStatus.RUNNING
)

# YOLO schedule - runs detection every 12 hours
yolo_schedule = ScheduleDefinition(
    job_name="yolo_job",
    cron_schedule="0 */12 * * *",  # Every 12 hours
    name="yolo_detection_schedule",
    description="Run YOLO detection every 12 hours",
    default_status=DefaultScheduleStatus.RUNNING
)

# Weekly full refresh schedule
weekly_refresh_schedule = ScheduleDefinition(
    job_name="full_pipeline_job",
    cron_schedule="0 2 * * 0",  # Every Sunday at 2 AM
    name="weekly_refresh_schedule",
    description="Full pipeline refresh every Sunday at 2 AM",
    default_status=DefaultScheduleStatus.RUNNING
) 