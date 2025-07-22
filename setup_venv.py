#!/usr/bin/env python3
"""
Virtual Environment Setup Script for DSPy Prompt Correction Microservice.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description, check=True):
    print(f"🔄 {description}...")
    print(f"   Command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   Details: {e.stderr.strip()}")
        return False


def check_python_version():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def get_venv_activate_command():
    system = platform.system().lower()
    if system == "windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"


def main():
    print("🐍 DSPy Prompt Correction Microservice - Virtual Environment Setup")
    print("="*70)
    if not Path("requirements.txt").exists():
        print("❌ Error: requirements.txt not found. Please run from project root.")
        sys.exit(1)
    if not check_python_version():
        sys.exit(1)
    venv_path = Path("venv")
    if venv_path.exists():
        print("⚠️  Virtual environment 'venv' already exists.")
        response = input("   Do you want to recreate it? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            print("🗑️  Removing existing virtual environment...")
            import shutil
            shutil.rmtree(venv_path)
        else:
            print("📝 Using existing virtual environment.")
            print(f"   To activate: {get_venv_activate_command()}")
            return
    print("\n🔧 Creating virtual environment...")
    if not run_command([sys.executable, "-m", "venv", "venv"], "Creating virtual environment"):
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    activate_cmd = get_venv_activate_command()
    print("\n📦 Installing dependencies...")
    if platform.system().lower() == "windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    if not run_command([pip_cmd, "install", "--upgrade", "pip"], "Upgrading pip"):
        print("⚠️  Failed to upgrade pip, continuing...")
    if not run_command([pip_cmd, "install", "-r", "requirements.txt"], "Installing requirements"):
        print("❌ Failed to install requirements")
        sys.exit(1)
    env_file = Path(".env")
    if not env_file.exists():
        env_example = Path("env.example")
        if env_example.exists():
            print("\n📝 Creating .env file from template...")
            import shutil
            shutil.copy(env_example, env_file)
            print("   ✅ Created .env file")
            print("   ⚠️  Please edit .env file with your Anthropic API key")
        else:
            print("⚠️  env.example not found, please create .env file manually")
    print("\n🎉 Virtual environment setup completed successfully!")
    print("\n📋 Next steps:")
    print(f"   1. Activate virtual environment:")
    print(f"      {activate_cmd}")
    print("   2. Edit .env file with your Anthropic API key")
    print("   3. Start the server:")
    print("      python start_server.py")
    print("   4. Run tests:")
    print("      python run_tests.py")
    print(f"\n💡 Quick activation command:")
    print(f"   {activate_cmd}")
    print("\n🔗 Useful commands:")
    print("   - Start server: python start_server.py")
    print("   - Run tests: python run_tests.py")
    print("   - View API docs: http://localhost:8000/docs")
    print("   - Deactivate venv: deactivate")


if __name__ == "__main__":
    main()
