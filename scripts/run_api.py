#!/usr/bin/env python3
"""
Script to run the FastAPI Analytics API server
"""
import sys
import argparse
import uvicorn
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings

def main():
    """Main function to run the FastAPI server"""
    parser = argparse.ArgumentParser(description="Run Telegram Medical Analytics API")
    parser.add_argument(
        "--host",
        default=settings.api_host,
        help=f"Host to bind to (default: {settings.api_host})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.api_port,
        help=f"Port to bind to (default: {settings.api_port})"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Log level (default: info)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Starting Telegram Medical Analytics API...")
    print(f"📍 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"🔄 Reload: {args.reload}")
    print(f"👥 Workers: {args.workers}")
    print(f"📝 Log Level: {args.log_level}")
    print(f"📖 Documentation: http://{args.host}:{args.port}/docs")
    print(f"📚 ReDoc: http://{args.host}:{args.port}/redoc")
    print(f"🔍 API Root: http://{args.host}:{args.port}/")
    print()
    
    try:
        uvicorn.run(
            "app.api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers,
            log_level=args.log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 API server stopped by user")
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 