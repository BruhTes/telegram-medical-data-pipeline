#!/usr/bin/env python3
"""
Script to run dbt commands for the Telegram Medical Data Pipeline
"""
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DbtRunner:
    """Run dbt commands for the data transformation pipeline"""
    
    def __init__(self):
        """Initialize the dbt runner"""
        self.dbt_project_dir = Path("dbt/telegram_medical_pipeline")
        self.profiles_dir = Path("dbt")
        
    def run_command(self, command: str, capture_output: bool = True) -> dict:
        """Run a dbt command and return results"""
        try:
            logger.info(f"Running: dbt {command}")
            
            # Set environment variables
            env = {
                'DBT_PROJECT_DIR': str(self.dbt_project_dir),
                'DBT_PROFILES_DIR': str(self.profiles_dir),
                'PATH': '/usr/local/bin:/usr/bin:/bin'
            }
            
            # Run the command
            result = subprocess.run(
                ['dbt'] + command.split(),
                cwd=self.dbt_project_dir,
                env=env,
                capture_output=capture_output,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout if capture_output else None,
                'stderr': result.stderr if capture_output else None
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: dbt {command}")
            return {'success': False, 'error': 'timeout'}
        except FileNotFoundError:
            logger.error("dbt command not found. Please install dbt first.")
            return {'success': False, 'error': 'dbt_not_found'}
        except Exception as e:
            logger.error(f"Error running dbt command: {e}")
            return {'success': False, 'error': str(e)}
    
    def deps(self) -> bool:
        """Install dbt dependencies"""
        logger.info("📦 Installing dbt dependencies...")
        result = self.run_command("deps")
        if result['success']:
            logger.info("✅ Dependencies installed successfully")
        else:
            logger.error(f"❌ Failed to install dependencies: {result.get('stderr', 'Unknown error')}")
        return result['success']
    
    def debug(self) -> bool:
        """Run dbt debug to check configuration"""
        logger.info("🔍 Running dbt debug...")
        result = self.run_command("debug")
        if result['success']:
            logger.info("✅ dbt configuration is valid")
            if result.get('stdout'):
                logger.info(result['stdout'])
        else:
            logger.error(f"❌ dbt configuration issues: {result.get('stderr', 'Unknown error')}")
        return result['success']
    
    def run(self, models: str = None) -> bool:
        """Run dbt models"""
        command = "run"
        if models:
            command += f" --models {models}"
            
        logger.info(f"🚀 Running dbt models: {command}")
        result = self.run_command(command)
        
        if result['success']:
            logger.info("✅ Models built successfully")
            if result.get('stdout'):
                logger.info(result['stdout'])
        else:
            logger.error(f"❌ Model build failed: {result.get('stderr', 'Unknown error')}")
        return result['success']
    
    def test(self, models: str = None) -> bool:
        """Run dbt tests"""
        command = "test"
        if models:
            command += f" --models {models}"
            
        logger.info(f"🧪 Running dbt tests: {command}")
        result = self.run_command(command)
        
        if result['success']:
            logger.info("✅ All tests passed")
            if result.get('stdout'):
                logger.info(result['stdout'])
        else:
            logger.error(f"❌ Tests failed: {result.get('stderr', 'Unknown error')}")
        return result['success']
    
    def docs_generate(self) -> bool:
        """Generate dbt documentation"""
        logger.info("📚 Generating dbt documentation...")
        result = self.run_command("docs generate")
        
        if result['success']:
            logger.info("✅ Documentation generated successfully")
            logger.info("📖 Documentation available at: dbt/telegram_medical_pipeline/target/index.html")
        else:
            logger.error(f"❌ Documentation generation failed: {result.get('stderr', 'Unknown error')}")
        return result['success']
    
    def docs_serve(self) -> bool:
        """Serve dbt documentation"""
        logger.info("🌐 Starting dbt documentation server...")
        logger.info("📖 Documentation will be available at: http://localhost:8080")
        logger.info("Press Ctrl+C to stop the server")
        
        # Run without capturing output so user can see the server
        result = self.run_command("docs serve --port 8080", capture_output=False)
        return result['success']
    
    def full_pipeline(self) -> bool:
        """Run the complete dbt pipeline"""
        logger.info("🔄 Starting complete dbt pipeline...")
        
        steps = [
            ("Debug", self.debug),
            ("Dependencies", self.deps),
            ("Run Models", lambda: self.run()),
            ("Run Tests", lambda: self.test()),
            ("Generate Docs", self.docs_generate)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 Step: {step_name}")
            if not step_func():
                logger.error(f"❌ Pipeline failed at step: {step_name}")
                return False
            logger.info(f"✅ Step completed: {step_name}")
        
        logger.info("🎉 Complete dbt pipeline finished successfully!")
        return True

def main():
    """Main function to run dbt commands"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run dbt commands for Telegram Medical Data Pipeline")
    parser.add_argument(
        "command",
        choices=['deps', 'debug', 'run', 'test', 'docs-generate', 'docs-serve', 'full-pipeline'],
        help="dbt command to run"
    )
    parser.add_argument(
        "--models",
        help="Specific models to run/test (e.g., 'staging', 'marts', 'dim_channels')"
    )
    
    args = parser.parse_args()
    
    runner = DbtRunner()
    
    if args.command == 'deps':
        success = runner.deps()
    elif args.command == 'debug':
        success = runner.debug()
    elif args.command == 'run':
        success = runner.run(args.models)
    elif args.command == 'test':
        success = runner.test(args.models)
    elif args.command == 'docs-generate':
        success = runner.docs_generate()
    elif args.command == 'docs-serve':
        success = runner.docs_serve()
    elif args.command == 'full-pipeline':
        success = runner.full_pipeline()
    else:
        logger.error(f"Unknown command: {args.command}")
        sys.exit(1)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 