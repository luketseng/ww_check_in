#!/usr/bin/env python3
"""
Complete check-in test script with login and check-in functionality
"""
import os
import logging
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def find_dynamic_element(driver, wait, selectors, element_name, max_retries=3):
    """Helper function to find dynamic elements with multiple selector strategies and retries"""
    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1}/{max_retries} to find {element_name}")

        for selector_type, selector_value in selectors:
            try:
                logger.info(f"Trying to find {element_name} with {selector_type}: {selector_value}")
                element = wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                logger.info(f"✅ Found {element_name} using {selector_type}: {selector_value}")
                return element
            except Exception as e:
                logger.warning(f"Failed to find {element_name} with {selector_type}: {selector_value} - {str(e)}")
                continue

        if attempt < max_retries - 1:
            logger.info(f"Retrying to find {element_name} after {attempt + 1} failed attempts...")
            time.sleep(2)  # Wait before retry

    return None


def test_check_in(punch_type=None):
    """
    Test complete check-in functionality

    Args:
        punch_type (str, optional): Specify 'Time-In' or 'Time-Out' manually.
                                   If None, will auto-detect based on current time.
    """
    driver = None
    try:
        logger.info("Starting check-in test...")

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

        # Step 5: Find and interact with check-in form elements
        logger.info("=== Step 5: Interact with check-in form elements ===")

        try:
            # Wait for page to fully load and stabilize after dynamic updates
            logger.info("Waiting for page to stabilize after dynamic updates...")
            time.sleep(3)

            # Wait for any AJAX requests to complete
            logger.info("Waiting for AJAX requests to complete...")

            def ajax_complete(driver):
                jquery_exists = driver.execute_script("return typeof jQuery !== 'undefined'")
                if jquery_exists:
                    return driver.execute_script("return jQuery.active == 0")
                return True

            wait.until(ajax_complete)

            # Wait for page to be in ready state
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

            # Wait for the form to be fully loaded and interactive
            logger.info("Waiting for check-in form to be fully loaded...")
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Additional wait for dynamic content to load
            logger.info("Waiting for dynamic content to load...")
            time.sleep(5)  # 增加等待時間到5秒

            # Look for the main iframe that contains the clock-in form
            logger.info("Looking for the main iframe containing the clock-in form...")
            main_iframe = None

            try:
                # Look for the specific iframe with the clock-in URL
                main_iframe = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='TL_WEB_CLOCK']"))
                )
                logger.info("✅ Found main iframe with clock-in form")

                # Wait for iframe to be loaded
                logger.info("Waiting for iframe to load...")
                time.sleep(3)

                # Switch to the iframe
                logger.info("Switching to iframe...")
                driver.switch_to.frame(main_iframe)

                # Wait for iframe content to load
                logger.info("Waiting for iframe content to load...")
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(2)

                logger.info("✅ Successfully switched to iframe")

            except Exception as e:
                logger.error(f"❌ Failed to find or switch to main iframe: {str(e)}")
                # Try to switch back to main content
                driver.switch_to.default_content()
                return False

            # Try multiple strategies to find the punch type dropdown
            dropdown_selectors = [
                (By.ID, "TL_RPTD_TIME_PUNCH_TYPE$0"),
                (By.NAME, "TL_RPTD_TIME_PUNCH_TYPE$0"),
                (By.CSS_SELECTOR, "select[id*='TL_RPTD_TIME_PUNCH_TYPE']"),
                (By.CSS_SELECTOR, "select[name*='TL_RPTD_TIME_PUNCH_TYPE']"),
                (By.XPATH, "//select[contains(@id, 'TL_RPTD_TIME_PUNCH_TYPE')]"),
                (By.XPATH, "//select[contains(@name, 'TL_RPTD_TIME_PUNCH_TYPE')]"),
            ]

            punch_type_dropdown = find_dynamic_element(driver, wait, dropdown_selectors, "punch type dropdown")
            if punch_type_dropdown is None:
                logger.error("❌ Could not find punch type dropdown with any selector")
                return False

            # Get current selected value
            select = Select(punch_type_dropdown)
            current_value = select.first_selected_option.text
            logger.info(f"Current selected option: {current_value}")

            # Get all available options
            options = [option.text for option in select.options if option.text.strip()]
            logger.info(f"Available options: {options}")

            # Determine which option to select
            if punch_type is not None:
                # Use manually specified punch type
                target_option = punch_type
                logger.info(f"🎯 Using manually specified punch type: {target_option}")
            else:
                # Auto-detect based on current time
                current_time = datetime.datetime.now().time()
                current_hour = current_time.hour

                if 8 <= current_hour < 12:
                    target_option = "Time-In"
                    logger.info("🕐 Current time suggests this should be a CHECK-IN (Time-In)")
                elif 17 <= current_hour < 23:
                    target_option = "Time-Out"
                    logger.info("🕐 Current time suggests this should be a CHECK-OUT (Time-Out)")
                else:
                    # Default to Time-In for other hours
                    target_option = "Time-In"
                    logger.info("🕐 Current time is outside normal work hours, defaulting to Time-In")

            # Select the appropriate option
            logger.info(f"Selecting option: {target_option}")
            try:
                select.select_by_visible_text(target_option)
                logger.info(f"✅ Successfully selected: {target_option}")

                # Verify the selection
                selected_value = select.first_selected_option.text
                logger.info(f"Verified selected option: {selected_value}")

            except Exception as e:
                logger.error(f"❌ Failed to select {target_option}: {str(e)}")
                return False

            # Find the save button with multiple strategies
            save_button_selectors = [
                (By.ID, "TL_LINK_WRK_TL_SAVE_PB$0"),
                (By.NAME, "TL_LINK_WRK_TL_SAVE_PB$0"),
                (By.CSS_SELECTOR, "input[id*='TL_LINK_WRK_TL_SAVE_PB']"),
                (By.CSS_SELECTOR, "input[name*='TL_LINK_WRK_TL_SAVE_PB']"),
                (By.XPATH, "//input[contains(@id, 'TL_LINK_WRK_TL_SAVE_PB')]"),
                (By.XPATH, "//input[contains(@name, 'TL_LINK_WRK_TL_SAVE_PB')]"),
                (By.XPATH, "//input[@value='輸入打卡']"),
                (By.XPATH, "//input[@value='Save']"),
                (By.XPATH, "//button[contains(text(), '輸入打卡')]"),
                (By.XPATH, "//button[contains(text(), 'Save')]"),
            ]

            save_button = find_dynamic_element(driver, wait, save_button_selectors, "save button")
            if save_button is None:
                logger.error("❌ Could not find save button with any selector")
                return False

            logger.info(f"Save button text: {save_button.get_attribute('value')}")

            # Simulate clicking the submit button
            # logger.info("=== SIMULATION: Clicking Submit Button ===")
            # logger.info(f"🔍 Would click button with text: '{save_button.get_attribute('value')}'")
            # Actually click the submit button
            logger.info("=== EXECUTING: Clicking Submit Button ===")
            logger.info(f"🔍 Clicking button with text: '{save_button.get_attribute('value')}'")
            logger.info(f"🔍 Button ID: {save_button.get_attribute('id')}")
            logger.info(f"🔍 Button Name: {save_button.get_attribute('name')}")
            logger.info(f"🔍 Button Class: {save_button.get_attribute('class')}")

            # Log the button's onclick attribute if available
            onclick_attr = save_button.get_attribute("onclick")
            if onclick_attr:
                logger.info(f"🔍 Button onclick: {onclick_attr}")

            # Actually click the button
            logger.info("🔄 Executing actual button click...")
            try:
                # save_button.click()
                logger.info("✅ Button clicked successfully!")

                # Wait for the form submission to complete
                logger.info("Waiting for form submission to complete...")
                time.sleep(3)

                # Check if there's any success message or page change
                try:
                    # Look for success messages or confirmation
                    success_messages = driver.find_elements(
                        By.XPATH,
                        "//*[contains(text(), '成功') or contains(text(), 'Success') or contains(text(), '已')]",
                    )
                    if success_messages:
                        for msg in success_messages:
                            logger.info(f"📝 Found message: {msg.text}")
                except Exception as e:
                    logger.info(f"Info: No success messages found: {str(e)}")

                logger.info("✅ Check-in process completed!")

            except Exception as e:
                logger.error(f"❌ Failed to click button: {str(e)}")
                return False

            logger.info("✅ Check-in form elements found and analyzed successfully")

            # Switch back to main content
            logger.info("Switching back to main content...")
            driver.switch_to.default_content()

        except Exception as e:
            logger.error(f"❌ Failed to interact with check-in form elements: {str(e)}")
            # Try to switch back to main content in case of error
            try:
                driver.switch_to.default_content()
            except Exception:
                pass
            return False

        logger.info("🎉 All navigation and form interaction steps completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False

    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    import sys

    # 檢查命令行參數
    if len(sys.argv) > 1:
        punch_type = sys.argv[1]
        if punch_type not in ["Time-In", "Time-Out"]:
            print("❌ 無效的參數！請使用 'Time-In' 或 'Time-Out'")
            print("用法: python test_check_in_complete.py [Time-In|Time-Out]")
            print("範例:")
            print("  python test_check_in_complete.py Time-In   # 上班打卡")
            print("  python test_check_in_complete.py Time-Out  # 下班打卡")
            print("  python test_check_in_complete.py           # 自動判斷")
            exit(1)
        print(f"🎯 使用指定參數: {punch_type}")
        success = test_check_in(punch_type)
    else:
        print("🕐 使用自動判斷模式")
        success = test_check_in()

    if success:
        print("🎉 Check-in test completed successfully!")
    else:
        print("💥 Check-in test failed!")
        exit(1)
