#!/usr/bin/env python3
"""
Test runner script for DSPy Prompt Correction Microservice.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*60)

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Exit code: {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


def main():
    """Main test runner function."""
    print("🧪 DSPy Prompt Correction Microservice - Test Runner")
    print("="*60)

    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Error: requirements.txt not found. Please run from project root.")
        sys.exit(1)

    # Install dependencies if needed
    print("\n📦 Checking dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                       "Installing dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)

    # Run linting
    print("\n🔍 Running linting...")
    try:
        import flake8
        if not run_command([sys.executable, "-m", "flake8", "dspy_prompt_fixer", "tests"],
                           "Running flake8 linting"):
            print("⚠️  Linting issues found (continuing with tests)")
    except ImportError:
        print("⚠️  flake8 not installed, skipping linting")

    # Run all tests
    print("\n🧪 Running all tests...")
    if not run_command([sys.executable, "-m", "pytest", "tests/", "-v"],
                       "Running all tests"):
        print("❌ Tests failed")
        sys.exit(1)

    # Run all tests with coverage
    print("\n📊 Running tests with coverage...")
    if not run_command([sys.executable, "-m", "pytest", "tests/", "--cov=dspy_prompt_fixer",
                       "--cov-report=term-missing", "--cov-report=html"],
                       "Running tests with coverage"):
        print("❌ Coverage tests failed")
        sys.exit(1)

    print("\n✅ All tests completed successfully!")
    print("\n📁 Coverage report generated in htmlcov/index.html")
    print("🎉 Ready to deploy!")


if __name__ == "__main__":
    main()
