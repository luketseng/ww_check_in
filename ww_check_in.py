#!/usr/bin/env python3
"""
WW Check-in System (refactored)

- Central business flow that delegates all Selenium work to utils.selenium_helper
- Supports both container and local execution (env-controlled)
"""
import logging
import os
import sys
import datetime
from typing import Optional
from dotenv import load_dotenv

from utils.selenium_helper import SeleniumHelper


load_dotenv()


def setup_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "logs/ww_check_in.log")

    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )


def decide_punch_type(explicit: Optional[str]) -> str:
    if explicit in ("Time-In", "Time-Out"):
        return explicit
    hour = datetime.datetime.now().time().hour
    if 8 <= hour < 12:
        return "Time-In"
    if 17 <= hour < 23:
        return "Time-Out"
    return "Time-In"


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    login_url = os.getenv("LOGIN_URL", "https://hr.wiwynn.com/psc/hcmprd/?cmd=login&languageCd=ZHT")
    username = os.getenv("WW_USERNAME")
    password = os.getenv("WW_PASSWORD")
    if not username or not password:
        logger.error("Missing WW_USERNAME or WW_PASSWORD in environment")
        sys.exit(1)

    # Optional: override punch via CLI arg
    punch_arg = None
    if len(sys.argv) > 1:
        punch_arg = sys.argv[1]

    target_punch = decide_punch_type(punch_arg)
    logger.info("=" * 60)
    logger.info("WW Check-in start")
    logger.info(f"Timestamp: {datetime.datetime.now()}")
    logger.info(f"Target punch: {target_punch}")
    logger.info("=" * 60)

    helper: Optional[SeleniumHelper] = None
    try:
        helper = SeleniumHelper()

        # Step 1: login
        logger.info("Step 1: login")
        helper.login(login_url=login_url, username=username, password=password)
        logger.info("Login submitted. Waiting for page to stabilize...")
        helper.wait_for_ajax_and_ready(10)

        # Step 2: 我的出勤/工時
        logger.info("Step 2: 我的出勤/工時")
        helper.click_by_id("win0groupletPTNUI_LAND_REC_GROUPLET$1", sleep_after=2)

        # Step 3: 工時回報
        logger.info("Step 3: 工時回報")
        helper.click_by_id("Z_ESS_TIMEREPORTED$2", sleep_after=2)

        # Step 4: 線上打卡
        logger.info("Step 4: 線上打卡")
        helper.open_online_checkin_step()

        # Step 5: Iframe and form
        logger.info("Step 5: Iframe and form")
        helper.switch_to_clock_iframe()
        helper.select_punch_type(target_punch)
        # helper.click_save()

        logger.info("=" * 60)
        logger.info("WW Check-in completed successfully")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Check-in failed: {e}")
        sys.exit(1)
    finally:
        if helper is not None:
            helper.close()


if __name__ == "__main__":
    main()
