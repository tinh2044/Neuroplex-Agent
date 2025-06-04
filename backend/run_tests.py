#!/usr/bin/env python3
"""
Script để chạy test suite cho backend API
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner"""
    print("🧪 Backend API Test Suite Runner")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✅ Pytest found: {pytest.__version__}")
    except ImportError:
        print("❌ Pytest not found. Installing...")
        if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"], 
                          "Installing test dependencies"):
            return 1
    
    # Run different test scenarios
    test_scenarios = [
        {
            "name": "Quick Smoke Tests",
            "cmd": [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-x"],
            "description": "Run tests until first failure"
        },
        {
            "name": "All Tests with Coverage",
            "cmd": [sys.executable, "-m", "pytest", "tests/", "-v", 
                   "--cov=backend", "--cov-report=term-missing", "--cov-report=html"],
            "description": "Run all tests with coverage report"
        },
        {
            "name": "Admin Routes Only",
            "cmd": [sys.executable, "-m", "pytest", "tests/test_admin_routes.py", "-v"],
            "description": "Test only admin routes"
        }
    ]
    
    # Ask user which scenario to run
    print("\nAvailable test scenarios:")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"{i}. {scenario['name']}")
    print("0. Run all scenarios")
    
    try:
        choice = input("\nSelect scenario (0-{}): ".format(len(test_scenarios)))
        choice = int(choice)
    except (ValueError, KeyboardInterrupt):
        print("\n👋 Goodbye!")
        return 0
    
    if choice == 0:
        # Run all scenarios
        success_count = 0
        for scenario in test_scenarios:
            if run_command(scenario["cmd"], scenario["description"]):
                success_count += 1
            
        print(f"\n📊 Results: {success_count}/{len(test_scenarios)} scenarios passed")
        return 0 if success_count == len(test_scenarios) else 1
    
    elif 1 <= choice <= len(test_scenarios):
        # Run selected scenario
        scenario = test_scenarios[choice - 1]
        success = run_command(scenario["cmd"], scenario["description"])
        return 0 if success else 1
    
    else:
        print("❌ Invalid choice")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 