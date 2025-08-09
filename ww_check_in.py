#!/usr/bin/env python3
"""
WW Check-in System
Automated check-in system for WW HR portal
"""
import logging
import os
import sys
from datetime import datetime
from selenium.webdriver.common.by import By
from dotenv import load_dotenv


# Import local modules
from utils.selenium_helper import SeleniumHelper
from config.schedule_config import ScheduleConfig

# Load environment variables
load_dotenv()


# Configure logging
def setup_logging():
    """Setup logging configuration"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "logs/ww_check_in.log")

    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )


class WWCheckIn:
    """Main class for WW check-in system"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.selenium_helper = None
        self.schedule_config = ScheduleConfig()
        self.login_url = "https://hr.wiwynn.com/psc/hcmprd/?cmd=login&languageCd=ZHT"

    def initialize(self):
        """Initialize the check-in system"""
        try:
            self.logger.info("Initializing WW Check-in System")
            self.selenium_helper = SeleniumHelper()
            self.logger.info("System initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {str(e)}")
            raise

    def login(self):
        """Login to WW HR portal"""
        try:
            self.logger.info("Starting login process")

            # Navigate to login page
            self.selenium_helper.navigate_to(self.login_url)
            self.logger.info("Navigated to login page")

            # Get credentials from environment variables
            username = os.getenv("WW_USERNAME")
            password = os.getenv("WW_PASSWORD")

            if not username or not password:
                raise ValueError("Username or password not found in environment variables")

            self.logger.info("Credentials loaded from environment variables")

            # Wait for login page to load completely
            self.logger.info("Login page loaded successfully")
            self.logger.info(f"Current page title: {self.selenium_helper.get_page_title()}")
            self.logger.info(f"Current URL: {self.selenium_helper.get_current_url()}")

            # Input username
            self.logger.info("Entering username")
            self.selenium_helper.input_text(By.ID, "userid", username)

            # Input password
            self.logger.info("Entering password")
            self.selenium_helper.input_text(By.ID, "pwd", password)

            # Click login button
            self.logger.info("Clicking login button")
            self.selenium_helper.click_element(By.NAME, "Submit")

            # Wait for page to load after login
            self.logger.info("Waiting for login response...")

            # Check if login was successful by waiting for URL change or specific element
            try:
                # Wait a moment for the page to load
                import time

                time.sleep(3)

                new_url = self.selenium_helper.get_current_url()
                new_title = self.selenium_helper.get_page_title()

                self.logger.info(f"After login - URL: {new_url}")
                self.logger.info(f"After login - Title: {new_title}")

                # Check if we're still on the login page (login failed)
                if "login" in new_url.lower() or "signin" in new_url.lower():
                    self.logger.warning("Still on login page - login may have failed")
                else:
                    self.logger.info("Login appears successful - redirected to new page")

            except Exception as e:
                self.logger.error(f"Error checking login status: {str(e)}")

            self.logger.info("Login process completed")

        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            raise

    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.selenium_helper:
                self.selenium_helper.close()
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")


def main():
    """Main function"""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("=" * 50)
        logger.info("WW Check-in System Started")
        logger.info(f"Timestamp: {datetime.now()}")
        logger.info("=" * 50)

        # Initialize check-in system
        check_in = WWCheckIn()
        check_in.initialize()

        # Perform login
        check_in.login()

        logger.info("=" * 50)
        logger.info("WW Check-in System Completed Successfully")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"System failed: {str(e)}")
        sys.exit(1)
    finally:
        if "check_in" in locals():
            check_in.cleanup()


if __name__ == "__main__":
    main()
