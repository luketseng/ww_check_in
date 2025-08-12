#!/usr/bin/env python3
"""
Improved end-to-end check-in test with robust locator for '線上打卡'.
This file does not replace the original. Use this version if Step 4 fails in the original script.
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


load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def find_dynamic_element(driver, wait, selectors, element_name, max_retries=3):
    """Try multiple selectors with retries to locate a dynamic element."""
    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1}/{max_retries} to find {element_name}")
        for selector_type, selector_value in selectors:
            try:
                logger.info(f"Trying {element_name} with {selector_type}: {selector_value}")
                element = wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                logger.info(f"✅ Found {element_name} using {selector_type}: {selector_value}")
                return element
            except Exception as e:
                logger.warning(f"Failed {element_name} with {selector_type}: {selector_value} - {str(e)}")
                continue
        if attempt < max_retries - 1:
            logger.info(f"Retrying to find {element_name} after {attempt + 1} failed attempts...")
            time.sleep(2)
    return None


def robust_click(driver, element):
    """Click using JS fallback after scrolling into view."""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        try:
            element.click()
        except Exception:
            driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        logger.error(f"Failed to click element: {e}")
        return False


def test_check_in(punch_type=None):
    driver = None
    try:
        logger.info("Starting check-in test (v2)...")

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        if os.getenv("HEADLESS", "false").lower() == "true":
            chrome_options.add_argument("--headless=new")

        logger.info("Setting up ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(int(os.getenv("IMPLICIT_WAIT", "10")))
        driver.set_page_load_timeout(int(os.getenv("PAGE_LOAD_TIMEOUT", "30")))

        wait = WebDriverWait(driver, max(15, int(os.getenv("IMPLICIT_WAIT", "10"))))

        # Step 1: Login
        login_url = "https://hr.wiwynn.com/psc/hcmprd/?cmd=login&languageCd=ZHT"
        logger.info(f"Navigating to: {login_url}")
        driver.get(login_url)

        username = os.getenv("WW_USERNAME")
        password = os.getenv("WW_PASSWORD")
        if not username or not password:
            logger.error("Username or password not found in environment")
            return False

        username_field = wait.until(EC.presence_of_element_located((By.ID, "userid")))
        username_field.clear()
        username_field.send_keys(username)
        password_field = driver.find_element(By.ID, "pwd")
        password_field.clear()
        password_field.send_keys(password)
        driver.find_element(By.NAME, "Submit").click()
        time.sleep(3)

        # Step 2: Go to 我的出勤/工時
        try:
            element = wait.until(EC.element_to_be_clickable((By.ID, "win0groupletPTNUI_LAND_REC_GROUPLET$1")))
            robust_click(driver, element)
            time.sleep(3)
        except Exception as e:
            logger.error(f"Failed to open '我的出勤/工時': {e}")
            return False

        # Step 3: Navigate to 工時回報
        try:
            element = wait.until(EC.element_to_be_clickable((By.ID, "Z_ESS_TIMEREPORTED$2")))
            robust_click(driver, element)
            time.sleep(3)
        except Exception as e:
            logger.error(f"Failed to open '工時回報': {e}")
            return False

        # Step 4: Navigate to 線上打卡 (robust locators)
        logger.info("=== Step 4: Navigate to '線上打卡' (robust) ===")
        time.sleep(2)
        try:
            # Ensure we are at top-level content
            try:
                driver.switch_to.default_content()
            except Exception:
                pass

            # Candidate locators for the step button (PeopleSoft side nav)
            step_selectors = [
                # Direct role-link node with steplabel
                (By.XPATH, "//div[@role='link' and @steplabel='線上打卡']"),
                # Step button container that contains the target label text
                (
                    By.XPATH,
                    "//div[contains(@id,'PTGP_STEP_DVW_PTGP_STEP_BTN_GB')][.//span[normalize-space()='線上打卡']]",
                ),
                # From known label id climb to clickable container
                (
                    By.XPATH,
                    "//*[@id='PTGP_STEP_DVW_PTGP_STEP_LABEL$3']/ancestor::div[contains(@id,'PTGP_STEP_DVW_PTGP_STEP_BTN_GB')]",
                ),
            ]

            online_step = None
            for by, expr in step_selectors:
                try:
                    online_step = wait.until(EC.presence_of_element_located((by, expr)))
                    if online_step:
                        logger.info(f"Found '線上打卡' step via: {expr}")
                        break
                except Exception:
                    continue

            if not online_step:
                raise RuntimeError("Unable to locate '線上打卡' step button")

            # Prefer clicking the role-link node if present
            if online_step.get_attribute("role") != "link":
                try:
                    online_step = online_step.find_element(By.XPATH, ".//div[@role='link']")
                except Exception:
                    pass

            # Click with scroll + JS fallback
            if not robust_click(driver, online_step):
                # Fallback: if the node has an href attribute, open it directly
                href = online_step.get_attribute("href")
                if href:
                    logger.info(f"Fallback navigating to href: {href}")
                    driver.get(href)
                else:
                    raise RuntimeError("Failed to click '線上打卡'")

            time.sleep(3)
            logger.info("✅ Successfully navigated to '線上打卡' page")

        except Exception as e:
            logger.error(f"❌ Failed to find or click '線上打卡': {e}")
            return False

        # Step 5: Interact within TL_WEB_CLOCK iframe as in original script
        logger.info("=== Step 5: Interact within TL_WEB_CLOCK iframe ===")
        time.sleep(2)
        try:
            logger.info("Waiting for dynamic loads before form interaction...")
            time.sleep(3)

            def ajax_complete(drv):
                jquery_exists = drv.execute_script("return typeof jQuery !== 'undefined'")
                if jquery_exists:
                    return drv.execute_script("return jQuery.active == 0")
                return True

            try:
                WebDriverWait(driver, 10).until(ajax_complete)
            except Exception:
                pass

            WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)

            # Switch into TL_WEB_CLOCK iframe
            logger.info("Locating TL_WEB_CLOCK iframe...")
            main_iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='TL_WEB_CLOCK']")))
            time.sleep(2)
            driver.switch_to.frame(main_iframe)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(1)

            # Punch type dropdown
            dropdown_selectors = [
                (By.ID, "TL_RPTD_TIME_PUNCH_TYPE$0"),
                (By.CSS_SELECTOR, "select[id*='TL_RPTD_TIME_PUNCH_TYPE']"),
                (By.XPATH, "//select[contains(@id, 'TL_RPTD_TIME_PUNCH_TYPE')]"),
            ]
            punch_type_dropdown = find_dynamic_element(driver, wait, dropdown_selectors, "punch type dropdown")
            if punch_type_dropdown is None:
                logger.error("Could not find punch type dropdown")
                return False

            select = Select(punch_type_dropdown)
            options = [option.text for option in select.options if option.text.strip()]
            logger.info(f"Available options: {options}")

            if punch_type is not None:
                target_option = punch_type
            else:
                current_hour = datetime.datetime.now().time().hour
                target_option = (
                    "Time-In" if 8 <= current_hour < 12 else ("Time-Out" if 17 <= current_hour < 23 else "Time-In")
                )

            logger.info(f"Selecting: {target_option}")
            select.select_by_visible_text(target_option)

            # Save button
            save_button_selectors = [
                (By.XPATH, "//input[contains(@id,'TL_LINK_WRK_TL_SAVE_PB') or @value='輸入打卡' or @value='Save']"),
                (By.XPATH, "//button[contains(text(),'輸入打卡') or contains(text(),'Save')]"),
            ]
            save_button = find_dynamic_element(driver, wait, save_button_selectors, "save button")
            if save_button is None:
                logger.error("Could not find save button")
                return False

            # Uncomment to actually click
            # robust_click(driver, save_button)
            logger.info("Simulation complete (no actual click).")

            driver.switch_to.default_content()

        except Exception as e:
            logger.error(f"❌ Failed to interact with check-in form: {e}")
            try:
                driver.switch_to.default_content()
            except Exception:
                pass
            return False

        logger.info("🎉 Flow completed successfully (v2)")
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

    if len(sys.argv) > 1:
        punch_type = sys.argv[1]
        if punch_type not in ["Time-In", "Time-Out"]:
            print("Invalid arg. Use 'Time-In' or 'Time-Out'")
            sys.exit(1)
        ok = test_check_in(punch_type)
    else:
        ok = test_check_in()
    sys.exit(0 if ok else 1)
