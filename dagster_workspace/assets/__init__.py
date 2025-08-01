"""
Dagster assets module
"""
from .telegram_assets import telegram_assets
from .dbt_assets import dbt_assets
from .yolo_assets import yolo_assets

__all__ = ["telegram_assets", "dbt_assets", "yolo_assets"] 