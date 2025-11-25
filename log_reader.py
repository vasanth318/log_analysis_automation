# log_reader.py

import datetime
from typing import List


class LogReader:
    """
    Reads log files and filters by time window.
    Assumes log lines start with 'YYYY-MM-DD HH:MM:SS'.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_between(self, start_time: str, end_time: str) -> str:
        """
        Returns the concatenated log lines between start_time and end_time (inclusive).

        start_time / end_time format: 'YYYY-MM-DD HH:MM:SS'
        """
        start_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

        selected_lines: List[str] = []

        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                if len(line) < 19:
                    continue
                ts_str = line[:19]
                try:
                    ts = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # Not a timestamp line, include only if we've started within window
                    continue

                if start_dt <= ts <= end_dt:
                    selected_lines.append(line.rstrip("\n"))

        return "\n".join(selected_lines)
