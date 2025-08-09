"""
Selenium helper utilities for WW check-in system
"""

import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class SeleniumHelper:
    """Helper class for Selenium operations"""

    def __init__(self):
        self.driver = None
        self.wait = None
        self._setup_driver()

    def _setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        try:
            chrome_options = Options()

            # Add Chrome options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)

            # Set headless mode based on environment variable
            if os.getenv("HEADLESS", "false").lower() == "true":
                chrome_options.add_argument("--headless")

            # Use fixed ChromeDriver path
            service = Service("/usr/local/bin/chromedriver")
            logger.info("Using fixed ChromeDriver at /usr/local/bin/chromedriver")

            # Initialize driver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Set timeouts
            implicit_wait = int(os.getenv("IMPLICIT_WAIT", "10"))
            page_load_timeout = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))

            self.driver.implicitly_wait(implicit_wait)
            self.driver.set_page_load_timeout(page_load_timeout)

            # Setup WebDriverWait
            self.wait = WebDriverWait(self.driver, implicit_wait)

            logger.info("Chrome driver initialized successfully")

        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {str(e)}")
            raise

    def navigate_to(self, url: str):
        """Navigate to specified URL"""
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            logger.info("Navigation completed successfully")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            raise

    def find_element(self, by: By, value: str, timeout: int = None):
        """Find element with explicit wait"""
        try:
            wait_time = timeout or int(os.getenv("IMPLICIT_WAIT", "10"))
            wait = WebDriverWait(self.driver, wait_time)
            element = wait.until(EC.presence_of_element_located((by, value)))
            logger.debug(f"Element found: {by}={value}")
            return element
        except TimeoutException:
            logger.error(f"Element not found within {wait_time} seconds: {by}={value}")
            raise
        except Exception as e:
            logger.error(f"Error finding element {by}={value}: {str(e)}")
            raise

    def click_element(self, by: By, value: str, timeout: int = None):
        """Click element with explicit wait"""
        try:
            element = self.find_element(by, value, timeout)
            element.click()
            logger.debug(f"Element clicked: {by}={value}")
        except Exception as e:
            logger.error(f"Failed to click element {by}={value}: {str(e)}")
            raise

    def input_text(self, by: By, value: str, text: str, timeout: int = None):
        """Input text into element with explicit wait"""
        try:
            element = self.find_element(by, value, timeout)
            element.clear()
            element.send_keys(text)
            logger.debug(f"Text entered in {by}={value}: {text}")
        except Exception as e:
            logger.error(f"Failed to input text in {by}={value}: {str(e)}")
            raise

    def get_page_title(self) -> str:
        """Get current page title"""
        return self.driver.title

    def get_current_url(self) -> str:
        """Get current URL"""
        return self.driver.current_url

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
