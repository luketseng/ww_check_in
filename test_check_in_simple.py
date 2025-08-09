#!/usr/bin/env python3
"""
Simple check-in test script - navigation only
"""
import os
import logging
import time
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


def test_check_in():
    """Test check-in navigation"""
    driver = None
    try:
        logger.info("Starting check-in navigation test...")

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

        # Step 1: Login
        logger.info("=== Step 1: Login ===")
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
        else:
            logger.error("❌ Login page not loaded properly")
            return False

        # Step 2: Navigate to "我的出勤/工時"
        logger.info("=== Step 2: Navigate to '我的出勤/工時' ===")

        # Wait for the page to fully load
        time.sleep(2)

        try:
            # Try to find the element by the specific ID
            my_time_element = wait.until(EC.element_to_be_clickable((By.ID, "win0groupletPTNUI_LAND_REC_GROUPLET$1")))
            logger.info("Found '我的出勤/工時' element")

            # Click on the element
            logger.info("Clicking on '我的出勤/工時'...")
            my_time_element.click()

            # Wait for page to load
            time.sleep(3)

            # Check if we're on a new page
            new_title = driver.title
            new_url = driver.current_url
            logger.info(f"Page title after clicking: {new_title}")
            logger.info(f"URL after clicking: {new_url}")

            logger.info("✅ Successfully navigated to '我的出勤/工時' page")

        except Exception as e:
            logger.error(f"❌ Failed to find or click '我的出勤/工時' element: {str(e)}")
            return False

        # Step 3: Navigate to "工時回報" (Z_ESS_TIMEREPORTED)
        logger.info("=== Step 3: Navigate to '工時回報' ===")

        # Wait for the page to fully load
        time.sleep(2)

        try:
            # Look for the "工時回報" element
            time_reported_element = wait.until(EC.element_to_be_clickable((By.ID, "Z_ESS_TIMEREPORTED$2")))
            logger.info("Found '工時回報' element")

            # Click on the element
            logger.info("Clicking on '工時回報'...")
            time_reported_element.click()

            # Wait for page to load
            time.sleep(3)

            # Check if we're on a new page
            new_title = driver.title
            new_url = driver.current_url
            logger.info(f"Page title after clicking: {new_title}")
            logger.info(f"URL after clicking: {new_url}")

            logger.info("✅ Successfully navigated to '工時回報' page")

        except Exception as e:
            logger.error(f"❌ Failed to find or click '工時回報' element: {str(e)}")
            return False

        # Step 4: Navigate to "線上打卡"
        logger.info("=== Step 4: Navigate to '線上打卡' ===")

        # Wait for the page to fully load
        time.sleep(2)

        try:
            # Look for the "線上打卡" element
            online_checkin_element = wait.until(EC.element_to_be_clickable((By.ID, "PTGP_STEP_DVW_PTGP_STEP_LABEL$3")))
            logger.info("Found '線上打卡' element")

            # Click on the element
            logger.info("Clicking on '線上打卡'...")
            online_checkin_element.click()

            # Wait for page to load
            time.sleep(3)

            # Check if we're on a new page
            new_title = driver.title
            new_url = driver.current_url
            logger.info(f"Page title after clicking: {new_title}")
            logger.info(f"URL after clicking: {new_url}")

            logger.info("✅ Successfully navigated to '線上打卡' page")

        except Exception as e:
            logger.error(f"❌ Failed to find or click '線上打卡' element: {str(e)}")
            return False

        # Step 5: Basic page analysis
        logger.info("=== Step 5: Basic page analysis ===")

        # Wait for the page to fully load
        time.sleep(5)

        # Get page information
        page_title = driver.title
        page_url = driver.current_url
        logger.info(f"Final page title: {page_title}")
        logger.info(f"Final page URL: {page_url}")

        # Analyze page content
        logger.info("Analyzing page content...")
        page_source = driver.page_source.lower()

        # Check for expected elements
        if "tl_rptd_time_punch_type" in page_source:
            logger.info("✅ Found punch type dropdown in page source")
        else:
            logger.info("❌ Punch type dropdown not found in page source")

        if "tl_link_wrk_tl_save_pb" in page_source:
            logger.info("✅ Found save button in page source")
        else:
            logger.info("❌ Save button not found in page source")

        if "time-in" in page_source:
            logger.info("✅ Found Time-In option in page source")
        else:
            logger.info("❌ Time-In option not found in page source")

        if "time-out" in page_source:
            logger.info("✅ Found Time-Out option in page source")
        else:
            logger.info("❌ Time-Out option not found in page source")

        # Simulate check-in process
        logger.info("=== SIMULATION: Check-in Process ===")
        logger.info("🔍 Would perform the following actions:")
        logger.info("   1. Select 'Time-In' from dropdown (for check-in)")
        logger.info("   2. Click '輸入打卡' button to confirm")
        logger.info("   3. Wait for confirmation message")
        logger.info("⚠️  SIMULATION MODE: No actual check-in performed")

        logger.info("✅ Navigation and analysis completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False

    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    success = test_check_in()
    if success:
        print("🎉 Check-in navigation test completed successfully!")
    else:
        print("💥 Check-in navigation test failed!")
        exit(1)
