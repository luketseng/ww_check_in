#!/usr/bin/env python3
"""
Test script for WW Check-in login functionality
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_env_variables():
    """Test if environment variables are properly set"""
    print("Testing environment variables...")

    username = os.getenv("WW_USERNAME")
    password = os.getenv("WW_PASSWORD")

    if not username:
        print("❌ WW_USERNAME not found in .env file")
        return False
    else:
        print(f"✅ WW_USERNAME found: {username[:3]}***")

    if not password:
        print("❌ WW_PASSWORD not found in .env file")
        return False
    else:
        print(f"✅ WW_PASSWORD found: {'*' * len(password)}")

    return True


def test_imports():
    """Test if all required modules can be imported"""
    print("\nTesting module imports...")

    try:
        from ww_check_in import WWCheckIn

        print("✅ WWCheckIn class imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WWCheckIn: {e}")
        return False

    try:
        from utils.selenium_helper import SeleniumHelper

        print("✅ SeleniumHelper class imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SeleniumHelper: {e}")
        return False

    try:
        from config.schedule_config import ScheduleConfig

        print("✅ ScheduleConfig class imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ScheduleConfig: {e}")
        return False

    return True


def main():
    """Main test function"""
    print("=" * 50)
    print("WW Check-in System - Login Test")
    print("=" * 50)

    # Test environment variables
    env_ok = test_env_variables()

    # Test imports
    imports_ok = test_imports()

    print("\n" + "=" * 50)
    if env_ok and imports_ok:
        print("✅ All tests passed! Ready to run login test.")
        print("\nTo test the actual login, run:")
        print("python3 ww_check_in.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)
    print("=" * 50)


if __name__ == "__main__":
    main()
