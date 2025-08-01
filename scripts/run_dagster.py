#!/usr/bin/env python3
"""
Script to run Dagster UI and manage the Telegram Medical Data Pipeline
"""
import sys
import argparse
import subprocess
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

def run_dagster_dev():
    """Run Dagster development server"""
    print("🚀 Starting Dagster development server...")
    print("📊 UI will be available at: http://localhost:3000")
    print("🔧 Workspace: dagster_workspace/")
    print("📁 Project: Telegram Medical Data Pipeline")
    print()
    print("Available features:")
    print("  • Asset Graph: View and monitor data pipeline")
    print("  • Jobs: Run individual pipeline components")
    print("  • Schedules: Configure automated execution")
    print("  • Sensors: Event-driven triggers")
    print("  • Runs: Monitor execution history")
    print("  • Assets: Track data lineage")
    print()
    
    try:
        # Change to workspace directory
        workspace_dir = Path("dagster_workspace")
        if not workspace_dir.exists():
            print("❌ Dagster workspace not found. Please ensure dagster_workspace/ exists.")
            return False
        
        # Run dagster dev
        subprocess.run([
            "dagster", "dev",
            "--workspace-file", str(workspace_dir / "workspace.yaml"),
            "--host", "0.0.0.0",
            "--port", "3000"
        ], cwd=workspace_dir)
        
    except KeyboardInterrupt:
        print("\n🛑 Dagster server stopped by user")
    except Exception as e:
        print(f"❌ Error starting Dagster: {e}")
        return False
    
    return True

def run_job(job_name: str):
    """Run a specific Dagster job"""
    print(f"🎯 Running Dagster job: {job_name}")
    
    try:
        # Run the job using dagster job execute
        result = subprocess.run([
            "dagster", "job", "execute",
            "--workspace-file", "dagster_workspace/workspace.yaml",
            "--job", job_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Job {job_name} completed successfully")
            print(result.stdout)
        else:
            print(f"❌ Job {job_name} failed")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running job {job_name}: {e}")

def list_jobs():
    """List available Dagster jobs"""
    print("📋 Available Dagster Jobs:")
    print()
    print("1. telegram_pipeline_job")
    print("   Description: Scrape Telegram data and load into PostgreSQL")
    print("   Assets: scraped_telegram_data, loaded_raw_data, loaded_detection_data, telegram_data_quality_check")
    print()
    print("2. dbt_job")
    print("   Description: Run dbt models and tests")
    print("   Assets: dbt_models, dbt_tests, dbt_documentation, analytics_data_quality_check")
    print()
    print("3. yolo_job")
    print("   Description: Run YOLO image detection and analysis")
    print("   Assets: yolo_detections, yolo_quality_check, yolo_analysis")
    print()
    print("4. full_pipeline_job")
    print("   Description: Complete end-to-end pipeline")
    print("   Assets: All assets from all groups")
    print()

def list_schedules():
    """List available Dagster schedules"""
    print("⏰ Available Dagster Schedules:")
    print()
    print("1. daily_pipeline_schedule")
    print("   Job: full_pipeline_job")
    print("   Schedule: Every day at 6:00 AM")
    print("   Status: Running")
    print()
    print("2. telegram_data_schedule")
    print("   Job: telegram_pipeline_job")
    print("   Schedule: Every 4 hours")
    print("   Status: Running")
    print()
    print("3. dbt_transformation_schedule")
    print("   Job: dbt_job")
    print("   Schedule: Every 6 hours")
    print("   Status: Running")
    print()
    print("4. yolo_detection_schedule")
    print("   Job: yolo_job")
    print("   Schedule: Every 12 hours")
    print("   Status: Running")
    print()
    print("5. weekly_refresh_schedule")
    print("   Job: full_pipeline_job")
    print("   Schedule: Every Sunday at 2:00 AM")
    print("   Status: Running")
    print()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Dagster Pipeline Management")
    parser.add_argument(
        "command",
        choices=["dev", "run", "list-jobs", "list-schedules"],
        help="Command to execute"
    )
    parser.add_argument(
        "--job",
        help="Job name to run (use with 'run' command)"
    )
    
    args = parser.parse_args()
    
    if args.command == "dev":
        run_dagster_dev()
    elif args.command == "run":
        if not args.job:
            print("❌ Please specify a job name with --job")
            print("Available jobs:")
            list_jobs()
            return
        run_job(args.job)
    elif args.command == "list-jobs":
        list_jobs()
    elif args.command == "list-schedules":
        list_schedules()

if __name__ == "__main__":
    main() 