"""
Dagster jobs for Telegram Medical Data Pipeline
"""
from dagster import job, define_asset_job, AssetSelection

# Telegram pipeline job - scrapes and loads data
telegram_pipeline_job = define_asset_job(
    name="telegram_pipeline_job",
    description="Scrape Telegram data and load into PostgreSQL",
    selection=AssetSelection.groups("telegram"),
    config={
        "execution": {
            "config": {
                "multiprocess": {
                    "max_concurrent": 2
                }
            }
        }
    }
)

# dbt transformation job
dbt_job = define_asset_job(
    name="dbt_job",
    description="Run dbt models and tests",
    selection=AssetSelection.groups("dbt"),
    config={
        "execution": {
            "config": {
                "multiprocess": {
                    "max_concurrent": 1
                }
            }
        }
    }
)

# YOLO detection job
yolo_job = define_asset_job(
    name="yolo_job",
    description="Run YOLO image detection and analysis",
    selection=AssetSelection.groups("yolo"),
    config={
        "execution": {
            "config": {
                "multiprocess": {
                    "max_concurrent": 1
                }
            }
        }
    }
)

# Full pipeline job - runs everything
full_pipeline_job = define_asset_job(
    name="full_pipeline_job",
    description="Complete end-to-end pipeline: Telegram → dbt → YOLO → Analytics",
    selection=AssetSelection.all(),
    config={
        "execution": {
            "config": {
                "multiprocess": {
                    "max_concurrent": 2
                }
            }
        }
    }
) 