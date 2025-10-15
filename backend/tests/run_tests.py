#!/usr/bin/env python3
"""
Test runner for BOLT AI Neural Agent System
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")

    start_time = time.time()
    result = subprocess.run(command, capture_output=False)
    end_time = time.time()

    duration = end_time - start_time
    status = "PASSED" if result.returncode == 0 else "FAILED"

    print(f"\n{description}: {status} ({duration:.2f}s)")
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Run BOLT AI Neural Agent System tests"
    )
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "performance", "security", "legal", "all"],
        default="all",
        help="Type of tests to run",
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Run with coverage reporting"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument(
        "--fail-fast", action="store_true", help="Stop on first failure"
    )

    args = parser.parse_args()

    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]

    if args.verbose:
        base_cmd.append("-v")

    if args.fail_fast:
        base_cmd.append("--maxfail=1")

    if args.parallel:
        base_cmd.extend(["-n", "auto"])

    if args.coverage:
        base_cmd.extend(
            [
                "--cov=backend",
                "--cov-report=html",
                "--cov-report=term-missing",
                "--cov-fail-under=90",
            ]
        )

    # Test type specific commands
    test_commands = []

    if args.type == "unit" or args.type == "all":
        test_commands.append(
            (base_cmd + ["backend/tests/test_ml/", "-m", "unit"], "Unit Tests")
        )

    if args.type == "integration" or args.type == "all":
        test_commands.append(
            (
                base_cmd + ["backend/tests/test_integration/", "-m", "integration"],
                "Integration Tests",
            )
        )

    if args.type == "performance" or args.type == "all":
        test_commands.append(
            (
                base_cmd + ["backend/tests/test_performance/", "-m", "performance"],
                "Performance Tests",
            )
        )

    if args.type == "security" or args.type == "all":
        test_commands.append(
            (
                base_cmd + ["backend/tests/test_security/", "-m", "security"],
                "Security Tests",
            )
        )

    if args.type == "legal" or args.type == "all":
        test_commands.append(
            (
                base_cmd + ["backend/tests/test_legal/", "-m", "legal"],
                "Legal Compliance Tests",
            )
        )

    # Run tests
    start_time = time.time()
    all_passed = True

    for command, description in test_commands:
        if not run_command(command, description):
            all_passed = False
            if args.fail_fast:
                break

    end_time = time.time()
    total_duration = end_time - start_time

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Duration: {total_duration:.2f}s")
    print(f"Overall Status: {'PASSED' if all_passed else 'FAILED'}")

    if args.coverage:
        print(f"Coverage Report: htmlcov/index.html")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
