"""
Dagster sensors for Telegram Medical Data Pipeline
"""
from dagster import sensor, RunRequest, SensorDefinition, DefaultSensorStatus
from datetime import datetime, timedelta

@sensor(
    job_name="telegram_pipeline_job",
    name="telegram_data_sensor",
    description="Trigger Telegram scraping when new data is available",
    default_status=DefaultSensorStatus.RUNNING
)
def telegram_data_sensor(context):
    """Sensor that triggers Telegram scraping based on time intervals"""
    
    # Check if it's time to scrape (every 4 hours)
    now = datetime.now()
    last_run = context.cursor or "2024-01-01T00:00:00"
    last_run_time = datetime.fromisoformat(last_run)
    
    # Trigger if 4 hours have passed since last run
    if now - last_run_time >= timedelta(hours=4):
        context.update_cursor(now.isoformat())
        yield RunRequest(
            run_key=f"telegram_scrape_{now.strftime('%Y%m%d_%H%M')}",
            run_config={
                "execution": {
                    "config": {
                        "multiprocess": {
                            "max_concurrent": 2
                        }
                    }
                }
            }
        )

@sensor(
    job_name="dbt_job",
    name="dbt_trigger_sensor",
    description="Trigger dbt transformations when new raw data is loaded",
    default_status=DefaultSensorStatus.RUNNING
)
def dbt_trigger_sensor(context):
    """Sensor that triggers dbt transformations when new data is available"""
    
    # This sensor would typically check for new files or database changes
    # For now, we'll use a time-based trigger (every 6 hours)
    now = datetime.now()
    last_run = context.cursor or "2024-01-01T00:00:00"
    last_run_time = datetime.fromisoformat(last_run)
    
    # Trigger if 6 hours have passed since last run
    if now - last_run_time >= timedelta(hours=6):
        context.update_cursor(now.isoformat())
        yield RunRequest(
            run_key=f"dbt_transform_{now.strftime('%Y%m%d_%H%M')}",
            run_config={
                "execution": {
                    "config": {
                        "multiprocess": {
                            "max_concurrent": 1
                        }
                    }
                }
            }
        )

@sensor(
    job_name="yolo_job",
    name="yolo_trigger_sensor",
    description="Trigger YOLO detection when new images are available",
    default_status=DefaultSensorStatus.RUNNING
)
def yolo_trigger_sensor(context):
    """Sensor that triggers YOLO detection when new images are available"""
    
    # This sensor would typically check for new image files
    # For now, we'll use a time-based trigger (every 12 hours)
    now = datetime.now()
    last_run = context.cursor or "2024-01-01T00:00:00"
    last_run_time = datetime.fromisoformat(last_run)
    
    # Trigger if 12 hours have passed since last run
    if now - last_run_time >= timedelta(hours=12):
        context.update_cursor(now.isoformat())
        yield RunRequest(
            run_key=f"yolo_detection_{now.strftime('%Y%m%d_%H%M')}",
            run_config={
                "execution": {
                    "config": {
                        "multiprocess": {
                            "max_concurrent": 1
                        }
                    }
                }
            }
        )

@sensor(
    job_name="full_pipeline_job",
    name="full_pipeline_sensor",
    description="Trigger full pipeline on manual request or time intervals",
    default_status=DefaultSensorStatus.RUNNING
)
def full_pipeline_sensor(context):
    """Sensor that triggers the full pipeline"""
    
    # Check for manual trigger or daily schedule
    now = datetime.now()
    last_run = context.cursor or "2024-01-01T00:00:00"
    last_run_time = datetime.fromisoformat(last_run)
    
    # Trigger if 24 hours have passed since last run (daily)
    if now - last_run_time >= timedelta(hours=24):
        context.update_cursor(now.isoformat())
        yield RunRequest(
            run_key=f"full_pipeline_{now.strftime('%Y%m%d_%H%M')}",
            run_config={
                "execution": {
                    "config": {
                        "multiprocess": {
                            "max_concurrent": 2
                        }
                    }
                }
            }
        )

# Export sensors
telegram_sensor = telegram_data_sensor 