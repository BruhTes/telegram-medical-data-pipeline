"""
Dagster workspace configuration for Telegram Medical Data Pipeline
"""
from dagster import Definitions, load_assets_from_modules

from .assets import telegram_assets, dbt_assets, yolo_assets
from .jobs import telegram_pipeline_job, dbt_job, yolo_job, full_pipeline_job
from .schedules import telegram_schedule, daily_schedule
from .sensors import telegram_sensor

# Load all assets
all_assets = []
all_assets.extend(telegram_assets)
all_assets.extend(dbt_assets)
all_assets.extend(yolo_assets)

# Create definitions
defs = Definitions(
    assets=all_assets,
    jobs=[
        telegram_pipeline_job,
        dbt_job,
        yolo_job,
        full_pipeline_job
    ],
    schedules=[
        telegram_schedule,
        daily_schedule
    ],
    sensors=[
        telegram_sensor
    ]
) 