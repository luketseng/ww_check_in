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
import time
import random
from typing import Optional
from dotenv import load_dotenv, dotenv_values, find_dotenv
from utils.config import get_config_value

from utils.selenium_helper import SeleniumHelper


# Load .env early. Default behavior: do not override existing environment variables.
# You can force .env to take precedence by setting PREFER_DOTENV=true when running the script.
_DOTENV_PATH = find_dotenv()
_DOTENV_MAP = dotenv_values(_DOTENV_PATH) if _DOTENV_PATH else {}
load_dotenv(dotenv_path=_DOTENV_PATH, override=False)


def setup_logging() -> None:
    log_level = str(get_config_value("LOG_LEVEL", "INFO")).upper()
    log_file = str(get_config_value("LOG_FILE", "logs/ww_check_in.log"))

    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )


def _map_cli_to_ui_punch(cli_value: str) -> Optional[str]:
    """Map CLI punch values to UI visible text options.

    Accepted CLI values (case-insensitive):
    - "check-in"  -> "Time-In"
    - "check-out" -> "Time-Out"
    """
    value = (cli_value or "").strip().lower()
    if value == "check-in":
        return "Time-In"
    if value == "check-out":
        return "Time-Out"
    return None


def decide_punch_type(explicit_cli: Optional[str]) -> str:
    """Decide the UI punch option to use.

    - If CLI provides one of ["check-in", "check-out"], map to ["Time-In", "Time-Out"].
    - Backward compatibility: if CLI already provided ["Time-In", "Time-Out"], keep as is.
    - Otherwise, decide automatically by local time.
    """
    # New CLI mapping
    mapped = _map_cli_to_ui_punch(explicit_cli) if explicit_cli else None
    if mapped:
        return mapped

    # Backward compatibility with previous CLI values
    if explicit_cli in ("Time-In", "Time-Out"):
        return explicit_cli  # type: ignore[return-value]

    # Auto decision window
    hour = datetime.datetime.now().time().hour
    if 8 <= hour < 12:
        return "Time-In"
    if 17 <= hour < 23:
        return "Time-Out"
    return "Time-In"


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    login_url = str(get_config_value("LOGIN_URL", "https://hr.wiwynn.com/psc/hcmprd/?cmd=login&languageCd=ZHT"))
    username = get_config_value("WW_USERNAME")
    password = get_config_value("WW_PASSWORD")
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
    if punch_arg:
        logger.info(f"CLI punch arg: {punch_arg} -> UI option: {target_punch}")
    else:
        logger.info(f"Auto-decided UI punch option: {target_punch}")
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
        # Randomize submit time between 60-600 seconds (in 60s intervals)
        random_delay_minutes = random.randint(1, 10)  # 1-10 minutes
        random_delay_seconds = random_delay_minutes * 60
        logger.info(f"Random delay before click save button: {random_delay_minutes}m({random_delay_seconds}s)")
        time.sleep(random_delay_seconds)
        # logger.info("Disabled auto-submit button for temporary use")
        helper.click_save()

        # Handle duplicate clock-in popup if it appears
        helper.handle_duplicate_clockin_popup()

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
