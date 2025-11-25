# log_analyzer.py

import os
import argparse
from typing import List, Dict, Any
from datetime import datetime,timedelta

from constants import LOGS_DIR
from log_reader import LogReader
from chatgpt_client import ChatGPTClient
from log_generator import SampleLogGenerator
from email_sender import EmailSender



class LogAnalyzerApp:
    def __init__(self, logs_dir: str):
        self.logs_dir = logs_dir
        self.client = ChatGPTClient()
        self.email_sender = EmailSender()

    def get_log_files(self,file_to_analyze) -> List[str]:
        """
        Returns full paths of all .log files in logs_dir.
        """
        files = []
        is_all = "all" in file_to_analyze.lower()

        for name in os.listdir(self.logs_dir):
            if not name.lower().endswith(".log"):
                continue

            if is_all or file_to_analyze in name:
                full_path = os.path.join(self.logs_dir, name)
                files.append(full_path)

        return files

    def analyze_file(
        self, file_path: str, start_time: str, end_time: str
    ) -> Dict[str, Any] | None:
        """
        Filter logs by time, send to ChatGPT, return analysis.
        If no lines in the window, returns None.
        """
        reader = LogReader(file_path)
        snippet = reader.read_between(start_time, end_time)

        if not snippet.strip():
            # Nothing in this time window
            return None

        file_name = os.path.basename(file_path)
        result = self.client.analyze_log(
            file_name=file_name,
            log_text=snippet,
            start_time=start_time,
            end_time=end_time,
            context="Automated log analysis for failure detection.",
        )
        return result

    def run(self, start_time: str, end_time: str, file_to_analyze:str, send_email: bool = True):
        log_files = self.get_log_files(file_to_analyze)
        analyses: List[Dict[str, Any]] = []

        for fpath in log_files:
            result = self.analyze_file(fpath, start_time, end_time)
            if result:
                analyses.append(result)

        # Print to console
        print("\n=== Log Analysis Results ===\n")
        for r in analyses:
            print(f"File: {r.get('file_name')}")
            print(f"Severity: {r.get('severity')} | Category: {r.get('category')}")
            print(f"Summary: {r.get('ai_summary')}")
            print("-" * 80)

        # Send email if requested
        if send_email and analyses:
            self.email_sender.send_report(analyses)
            print("\nReport emailed to configured recipient.\n")
        elif not analyses:
            print("\nNo log entries found in the specified time window.\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-driven log analysis.")
    parser.add_argument(
        "--start",
        required=True,
        help="Start time in 'YYYY-MM-DD HH:MM:SS' format",
    )
    parser.add_argument(
        "--end",
        required=True,
        help="End time in 'YYYY-MM-DD HH:MM:SS' format",
    )
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Do not send email, only print results.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    #args = parse_args()
    send_email = True
    all_files = False
    specific_file  = "db_timeout"
    LOGS_DIR.mkdir(exist_ok=True)
    generator = SampleLogGenerator(LOGS_DIR, total_lines=60)
    
    #Get today's date
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    generator.generate_all(all=all_files, specific_file=specific_file)
    end_time = (datetime.now()+timedelta(seconds=120)).strftime("%Y-%m-%d %H:%M:%S")
    print("Start Time:", start_time)
    print("End Time:  ", end_time)
    app = LogAnalyzerApp(LOGS_DIR)
    if all_files:
        file_to_analyze = "all"
    else:
        file_to_analyze = specific_file
    app.run(start_time=start_time, end_time=end_time, file_to_analyze = file_to_analyze, send_email=send_email)
