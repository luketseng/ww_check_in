#!/usr/bin/env python3
"""
Simple login test script
"""
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_login():
    """Test login functionality"""
    driver = None
    try:
        logger.info("Starting login test...")

        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        # Set headless mode based on environment variable
        if os.getenv("HEADLESS", "false").lower() == "true":
            chrome_options.add_argument("--headless")

        # Setup ChromeDriver
        logger.info("Setting up ChromeDriver...")
        service = Service(ChromeDriverManager().install())

        # Initialize driver
        logger.info("Initializing Chrome driver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Set timeouts
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)

        logger.info("Chrome driver initialized successfully")

        # Navigate to login page
        login_url = "https://hr.wiwynn.com/psc/hcmprd/?cmd=login&languageCd=ZHT"
        logger.info(f"Navigating to: {login_url}")
        driver.get(login_url)

        # Wait for page to load
        wait = WebDriverWait(driver, 10)

        # Get page title and URL
        title = driver.title
        current_url = driver.current_url
        logger.info(f"Page title: {title}")
        logger.info(f"Current URL: {current_url}")

        # Check if we're on the login page
        if "userid" in driver.page_source.lower():
            logger.info("✅ Login page loaded successfully")

            # Get credentials from environment
            username = os.getenv("WW_USERNAME")
            password = os.getenv("WW_PASSWORD")

            if not username or not password:
                logger.error("❌ Username or password not found in .env file")
                return False

            logger.info(f"Found credentials for user: {username}")

            # Find and fill username field
            logger.info("Filling username field...")
            username_field = wait.until(EC.presence_of_element_located((By.ID, "userid")))
            username_field.clear()
            username_field.send_keys(username)

            # Find and fill password field
            logger.info("Filling password field...")
            password_field = driver.find_element(By.ID, "pwd")
            password_field.clear()
            password_field.send_keys(password)

            # Find and click submit button
            logger.info("Clicking submit button...")
            submit_button = driver.find_element(By.NAME, "Submit")
            submit_button.click()

            # Wait for page to load after login
            logger.info("Waiting for page to load after login...")
            import time

            time.sleep(3)

            # Check if login was successful
            new_title = driver.title
            new_url = driver.current_url
            logger.info(f"New page title: {new_title}")
            logger.info(f"New URL: {new_url}")

            # Check if we're still on login page (login failed) or moved to another page (login successful)
            if "userid" in driver.page_source.lower():
                logger.error("❌ Login failed - still on login page")
                return False
            else:
                logger.info("✅ Login successful - moved to new page")
                return True

        else:
            logger.error("❌ Login page not loaded properly")
            return False

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False

    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    success = test_login()
    if success:
        print("🎉 Login test completed successfully!")
    else:
        print("💥 Login test failed!")
        exit(1)
