"""
Selenium helper utilities for WW check-in system (refactored)

This module centralizes all WebDriver setup and page interactions so that
the main script remains small and easy to maintain.
"""

import logging
import os
import shutil
import subprocess
import re
import time
from typing import Iterable, List, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager


# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


Selector = Tuple[By, str]


class SeleniumHelper:
    """High-level helper for Selenium operations with robust utilities."""

    def __init__(self) -> None:
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self._setup_driver()

    # ------------------------- Driver Setup ------------------------- #
    def _setup_driver(self) -> None:
        """Setup ChromeDriver and base timeouts/options."""
        try:
            chrome_options = Options()

            # Stable defaults for containerized and CI environments
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("--window-size=1440,900")

            # Allow overriding Chrome binary (optional)
            chrome_binary = os.getenv("CHROME_BINARY")
            if chrome_binary and os.path.exists(chrome_binary):
                chrome_options.binary_location = chrome_binary

            # Headless control via env
            if os.getenv("HEADLESS", "false").lower() == "true":
                # Use the newer headless mode when available
                chrome_options.add_argument("--headless=new")

            # Resolve chromedriver path preferring version match with Chrome
            driver_path = self._select_best_chromedriver()

            # If not found or mismatch, optionally use webdriver-manager
            use_wdm = os.getenv("USE_WEBDRIVER_MANAGER", "true").lower() == "true"
            chrome_major = self._detect_chrome_major()
            drv_major = self._get_major_version_from_path(driver_path) if driver_path else None
            mismatch = chrome_major is not None and drv_major is not None and chrome_major != drv_major

            if (driver_path is None or not os.path.exists(driver_path) or mismatch) and use_wdm:
                logger.info(
                    f"Preparing driver via webdriver-manager (found={bool(driver_path)}, mismatch={mismatch})"
                )
                try:
                    # Let webdriver-manager auto-detect proper driver
                    driver_path = ChromeDriverManager().install()
                    logger.info(f"Webdriver-manager installed driver at: {driver_path}")
                except Exception as e:
                    logger.error(
                        "webdriver-manager failed. Set CHROMEDRIVER_PATH to a valid driver matching your Chrome. "
                        f"Error: {e}"
                    )
                    # Fall through to validation below

            if not driver_path or not os.path.exists(driver_path):
                raise FileNotFoundError(
                    "Chromedriver not found. Ensure the container image includes a compatible chromedriver, "
                    "set CHROMEDRIVER_PATH, or enable USE_WEBDRIVER_MANAGER=true with network access."
                )

            service = Service(driver_path)
            logger.info(f"Using ChromeDriver at {driver_path}")

            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            implicit_wait = int(os.getenv("IMPLICIT_WAIT", "10"))
            page_load_timeout = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))
            self.driver.implicitly_wait(implicit_wait)
            self.driver.set_page_load_timeout(page_load_timeout)
            self.wait = WebDriverWait(self.driver, implicit_wait)

            logger.info("Chrome driver initialized successfully")

        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {str(e)}")
            raise

    # ------------------------- Driver discovery ------------------------- #
    @staticmethod
    def _get_major_version_from_cmd(cmd: str) -> Optional[int]:
        try:
            out = subprocess.check_output([cmd, "--version"], stderr=subprocess.STDOUT).decode("utf-8", "ignore")
        except Exception:
            return None
        return SeleniumHelper._extract_major_version(out)

    @staticmethod
    def _get_major_version_from_path(path: str) -> Optional[int]:
        if not os.path.exists(path):
            return None
        try:
            out = subprocess.check_output([path, "--version"], stderr=subprocess.STDOUT).decode("utf-8", "ignore")
        except Exception:
            return None
        return SeleniumHelper._extract_major_version(out)

    @staticmethod
    def _extract_major_version(text: str) -> Optional[int]:
        # Match first number like 138.0.XXXX or 114.0...
        m = re.search(r"(\d+)\.", text)
        if not m:
            return None
        try:
            return int(m.group(1))
        except Exception:
            return None

    @staticmethod
    def _detect_chrome_major() -> Optional[int]:
        # Prefer explicit binary if provided
        chrome_binary = os.getenv("CHROME_BINARY")
        if chrome_binary and os.path.exists(chrome_binary):
            ver = SeleniumHelper._get_major_version_from_path(chrome_binary)
            if ver:
                return ver

        for name in ["google-chrome", "chromium", "chromium-browser", "chrome"]:
            path = shutil.which(name)
            if not path:
                continue
            ver = SeleniumHelper._get_major_version_from_cmd(path)
            if ver:
                return ver
        return None

    def _select_best_chromedriver(self) -> Optional[str]:
        # 1) Honor explicit env
        explicit = os.getenv("CHROMEDRIVER_PATH")
        if explicit and os.path.exists(explicit):
            logger.info(f"Using CHROMEDRIVER_PATH from env: {explicit}")
            return explicit

        # 2) Detect Chrome major version
        chrome_major = self._detect_chrome_major()
        if chrome_major:
            logger.info(f"Detected Chrome major version: {chrome_major}")
        else:
            logger.info("Could not detect Chrome version; will use best-effort driver selection")

        # 3) Candidate drivers (prefer /usr/bin over /usr/local/bin; also include which)
        which_driver = shutil.which("chromedriver")
        candidates = [
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            which_driver,
        ]

        # 4) If we know Chrome major, pick matching driver
        if chrome_major:
            for path in candidates:
                if not path or not os.path.exists(path):
                    continue
                drv_major = self._get_major_version_from_path(path)
                if drv_major:
                    logger.info(f"Candidate driver {path} major={drv_major}")
                if drv_major == chrome_major:
                    return path

        # 5) Fallback preference: /usr/bin/chromedriver if exists, else first existing
        for path in candidates:
            if path and os.path.exists(path):
                return path
        return None

    # ------------------------- Generic Utils ------------------------- #
    def navigate_to(self, url: str) -> None:
        """Navigate the browser to a URL."""
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)

    def find_element(self, by: By, value: str, timeout: Optional[int] = None):
        """Find an element with explicit wait."""
        wait_time = timeout or int(os.getenv("IMPLICIT_WAIT", "10"))
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            logger.error(f"Element not found within {wait_time}s: {by}={value}")
            raise

    def find_dynamic_element(
        self,
        selectors: Iterable[Selector],
        element_name: str,
        max_retries: int = 3,
        condition=EC.presence_of_element_located,
    ):
        """Try multiple selectors with retries to locate a dynamic element."""
        for attempt in range(max_retries):
            logger.info(f"Attempt {attempt + 1}/{max_retries} to find {element_name}")
            for by, locator in selectors:
                try:
                    logger.info(f"Trying {element_name} with {by}: {locator}")
                    element = WebDriverWait(self.driver, int(os.getenv("IMPLICIT_WAIT", "10"))).until(
                        condition((by, locator))
                    )
                    logger.info(f"✅ Found {element_name} using {by}: {locator}")
                    return element
                except Exception as e:
                    logger.debug(f"Not found via {by}: {locator} - {e}")
                    continue
            if attempt < max_retries - 1:
                time.sleep(2)
        return None

    def robust_click(self, element) -> bool:
        """Scroll into view and attempt normal click; fallback to JS click."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            try:
                element.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            logger.error(f"Failed to click element: {e}")
            return False

    def wait_for_ajax_and_ready(self, timeout: int = 10) -> None:
        """Wait for jQuery ajax (if present) and document ready state complete."""
        def ajax_complete(driver):
            try:
                jquery_exists = driver.execute_script("return typeof jQuery !== 'undefined'")
                if jquery_exists:
                    return driver.execute_script("return jQuery.active == 0")
            except Exception:
                pass
            return True

        try:
            WebDriverWait(self.driver, timeout).until(ajax_complete)
        except Exception:
            pass

        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def switch_to_default(self) -> None:
        try:
            self.driver.switch_to.default_content()
        except Exception:
            pass

    def wait_for_body(self, timeout: int = 10) -> None:
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    def close(self) -> None:
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

    # ------------------------- WW-specific Flows ------------------------- #
    def login(self, login_url: str, username: str, password: str) -> None:
        """Perform login to WW HR portal."""
        self.navigate_to(login_url)
        self.wait_for_body()

        user_el = self.find_element(By.ID, "userid")
        user_el.clear(); user_el.send_keys(username)
        pwd_el = self.find_element(By.ID, "pwd")
        pwd_el.clear(); pwd_el.send_keys(password)
        self.find_element(By.NAME, "Submit").click()

        time.sleep(2)
        logger.info("Login submitted")

    def click_by_id(self, element_id: str, sleep_after: float = 2.0) -> None:
        """Click an element that is expected to be clickable by id."""
        el = WebDriverWait(self.driver, int(os.getenv("IMPLICIT_WAIT", "10"))).until(
            EC.element_to_be_clickable((By.ID, element_id))
        )
        self.robust_click(el)
        time.sleep(sleep_after)

    def open_online_checkin_step(self) -> None:
        """Navigate to the '線上打卡' step using robust locators."""
        self.switch_to_default()
        time.sleep(1)

        step_selectors: List[Selector] = [
            # Direct role-link with steplabel
            (By.XPATH, "//div[@role='link' and @steplabel='線上打卡']"),
            # Container that includes target label text
            (By.XPATH, "//div[contains(@id,'PTGP_STEP_DVW_PTGP_STEP_BTN_GB')][.//span[normalize-space()='線上打卡']]"),
            # From label id to container
            (By.XPATH, "//*[@id='PTGP_STEP_DVW_PTGP_STEP_LABEL$3']/ancestor::div[contains(@id,'PTGP_STEP_DVW_PTGP_STEP_BTN_GB')]")
        ]

        node = self.find_dynamic_element(step_selectors, "online check-in step")
        if node is None:
            raise RuntimeError("Unable to locate '線上打卡' step")

        # If the container isn't the clickable node, try inner role=link
        try:
            if node.get_attribute("role") != "link":
                node = node.find_element(By.XPATH, ".//div[@role='link']")
        except Exception:
            pass

        if not self.robust_click(node):
            href = node.get_attribute("href")
            if href:
                logger.info(f"Fallback navigating to href: {href}")
                self.navigate_to(href)
            else:
                raise RuntimeError("Failed to click '線上打卡'")

        time.sleep(2)
        logger.info("Opened '線上打卡' step")

    def switch_to_clock_iframe(self) -> None:
        """Switch to the TL_WEB_CLOCK iframe."""
        self.switch_to_default()
        self.wait_for_ajax_and_ready(10)
        self.wait_for_body(10)
        time.sleep(2)

        iframe = self.find_dynamic_element(
            selectors=[(By.CSS_SELECTOR, "iframe[src*='TL_WEB_CLOCK']")],
            element_name="clock iframe",
        )
        if iframe is None:
            raise RuntimeError("Failed to locate TL_WEB_CLOCK iframe")

        time.sleep(1)
        self.driver.switch_to.frame(iframe)
        self.wait_for_body(10)
        logger.info("Switched to TL_WEB_CLOCK iframe")

    def select_punch_type(self, target_option: str) -> None:
        """Select the desired punch type in dropdown."""
        dropdown = self.find_dynamic_element(
            selectors=[
                (By.ID, "TL_RPTD_TIME_PUNCH_TYPE$0"),
                (By.CSS_SELECTOR, "select[id*='TL_RPTD_TIME_PUNCH_TYPE']"),
                (By.XPATH, "//select[contains(@id,'TL_RPTD_TIME_PUNCH_TYPE')]"),
            ],
            element_name="punch type dropdown",
        )
        if dropdown is None:
            raise RuntimeError("Could not find punch type dropdown")

        select = Select(dropdown)
        options = [o.text for o in select.options if o.text.strip()]
        logger.info(f"Available punch options: {options}")
        select.select_by_visible_text(target_option)
        logger.info(f"Selected punch type: {target_option}")

    def click_save(self) -> None:
        """Click the save/submit button within the iframe."""
        btn = self.find_dynamic_element(
            selectors=[
                (By.XPATH, "//input[contains(@id,'TL_LINK_WRK_TL_SAVE_PB') or @value='輸入打卡' or @value='Save']"),
                (By.XPATH, "//button[contains(text(),'輸入打卡') or contains(text(),'Save')]")
            ],
            element_name="save button",
            condition=EC.element_to_be_clickable,
        )
        if btn is None:
            raise RuntimeError("Could not find save button")
        if not self.robust_click(btn):
            raise RuntimeError("Failed to click save button")
        logger.info("Clicked save button")
