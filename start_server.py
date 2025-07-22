#!/usr/bin/env python3
"""
Server startup script for DSPy Prompt Correction Microservice.
"""

import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv


def check_environment():
    """Check if environment is properly configured."""
    load_dotenv()

    # Check for required environment variables
    required_vars = ["ANTHROPIC_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("See env.example for reference.")
        return False

    return True


def main():
    """Main server startup function."""
    print("🚀 DSPy Prompt Correction Microservice - Server Startup")
    print("="*60)

    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Error: requirements.txt not found. Please run from project root.")
        sys.exit(1)

    # Check environment configuration
    if not check_environment():
        sys.exit(1)

    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    print(f"📍 Server will start on: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🧠 Model: {os.getenv('CLAUDE_MODEL', 'claude-3-opus-20240229')}")

    if debug:
        print("⚠️  Warning: Debug mode is enabled. Do not use in production!")

    print("\n🚀 Starting server...")
    print("="*60)

    try:
        uvicorn.run(
            "dspy_prompt_fixer.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if not debug else "debug",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
