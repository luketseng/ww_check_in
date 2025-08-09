"""
Schedule configuration for WW check-in system
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ScheduleConfig:
    """Configuration class for work schedule"""

    def __init__(self):
        self.work_days = self._parse_work_days()
        self.work_start_time = os.getenv("WORK_START_TIME", "08:30")
        self.work_end_time = os.getenv("WORK_END_TIME", "18:00")

    def _parse_work_days(self) -> List[int]:
        """Parse work days from environment variable"""
        work_days_str = os.getenv("WORK_DAYS", "1,2,3,4")
        return [int(day.strip()) for day in work_days_str.split(",")]

    def is_work_day(self, weekday: int) -> bool:
        """Check if given weekday is a work day"""
        return weekday in self.work_days

    def get_work_start_time(self) -> str:
        """Get work start time"""
        return self.work_start_time

    def get_work_end_time(self) -> str:
        """Get work end time"""
        return self.work_end_time
