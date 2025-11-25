import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from constants import LOGS_DIR   # LOGS_DIR should be a Path, e.g. LOGS_DIR = Path("logs")


class SampleLogGenerator:
    """
    Generates synthetic log files for different error scenarios.
    Each log file:
      - Has >= total_lines lines (default 100)
      - Contains mostly normal INFO/WARN/DEBUG lines
      - Places the real ERROR block after the first filler section
      - Adds at least 10 normal lines *after* the error block
      - Filler lines: 1-second gaps
      - Error lines:  2-second gaps
    """

    def __init__(self, logs_dir: Path, total_lines: int = 100):
        self.logs_dir = Path(logs_dir)
        self.total_lines = max(total_lines, 50)  # enforce >= 100

    def _generate_filler_lines(
        self,
        start_time: datetime,
        count: int,
        component: str
    ) -> List[str]:
        """
        Generate 'count' normal (non-error) log lines with 1-second increments.
        """
        levels = ["INFO", "DEBUG", "INFO", "WARN"]
        lines: List[str] = []

        for i in range(count):
            # If you want to simulate real time, you could uncomment:
            # time.sleep(1)

            ts = start_time + timedelta(seconds=i)  # 1-second increments
            level = levels[i % len(levels)]
            msg = f"Normal operation heartbeat {i} in {component}"
            line = f"{ts.strftime('%Y-%m-%d %H:%M:%S')} {level} [{component}] {msg}"
            lines.append(line)

        return lines

    def _write_log_file(self, filename: str, error_block: list[str], component: str):
        """
        Create a log file with:
        - filler_before_count normal lines (1s gap)
        - error_block in the middle (2s gap)
        - exactly 10 normal lines after the error block (1s gap)
        """
        path = self.logs_dir / filename
        base_time = datetime.now()

        # We want a fixed 10 lines after the error block
        filler_after_count = 10
        error_count = len(error_block)

        # Compute how many lines we can put before the error
        # Total lines = filler_before + error_count + filler_after_count
        filler_before_count = max(self.total_lines - error_count - filler_after_count, 0)

        # --- Filler BEFORE the error block (1-second gap) ---
        filler_before_lines = self._generate_filler_lines(
            start_time=base_time,
            count=filler_before_count,
            component=component,
        )

        # Error starts right after the last filler-before timestamp
        error_start_time = base_time + timedelta(seconds=filler_before_count)

        # --- Error block in the middle (2-second gap) ---
        error_lines_with_ts: list[str] = []
        for i, raw in enumerate(error_block):
            ts = error_start_time + timedelta(seconds=i * 2)  # 2-second increments
            line = f"{ts.strftime('%Y-%m-%d %H:%M:%S')} {raw}"
            error_lines_with_ts.append(line)

        # Last error timestamp
        last_error_time = error_start_time + timedelta(
            seconds=(error_count - 1) * 2
        )
        after_start_time = last_error_time + timedelta(seconds=1)

        # --- Filler AFTER the error block (1-second gap, exactly 10) ---
        filler_after_lines = self._generate_filler_lines(
            start_time=after_start_time,
            count=filler_after_count,
            component=component,
        )

        # Write everything
        all_lines = filler_before_lines + error_lines_with_ts + filler_after_lines

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for line in all_lines:
                f.write(line + "\n")

        #print(f"Generated: {path} (lines: {len(all_lines)})")

        # ====== Scenario-specific generators ======

    def generate_sql_syntax_error_log(self):
        error_block = [
            'ERROR [DBWorker] Failed to execute SQL query.',
            'ERROR [DBWorker] ERROR: syntax error at or near "FROMM"',
            'ERROR [DBWorker] QUERY: SELECT * FROMM trades WHERE id = 123;',
            'INFO  [DBWorker] Retrying with fallback query...',
        ]
        self._write_log_file("sql_syntax_error.log", error_block, component="DBWorker")

    def generate_db_timeout_log(self):
        error_block = [
            "INFO  [ApiServer] Received /positions request.",
            "WARN  [DBPool] Connection to db-prod-01 is slow.",
            "ERROR [DBPool] Timeout: failed to obtain connection from pool after 30 seconds.",
            "ERROR [ApiServer] Failed to fetch positions: DB_TIMEOUT",
            "INFO  [ApiServer] Returning HTTP 500 to client.",
        ]
        self._write_log_file("db_timeout.log", error_block, component="ApiServer")

    def generate_network_connection_refused_log(self):
        error_block = [
            "INFO  [Scheduler] Running nightly job: risk_report.",
            "ERROR [HttpClient] Failed to call https://pricing-service.internal/api/curve",
            "ERROR [HttpClient] ConnectionError: [Errno 111] Connection refused",
            "WARN  [Scheduler] Marking job risk_report as FAILED.",
            "INFO  [Alerting] Sending PagerDuty alert: PRICING_SERVICE_DOWN.",
        ]
        self._write_log_file("network_connection_refused.log", error_block, component="Scheduler")

    def generate_null_pointer_error_log(self):
        error_block = [
            "INFO  [Worker] Starting batch process for portfolio=ABC.",
            "ERROR [Worker] Exception while processing portfolio=ABC",
            "ERROR [Worker] Traceback (most recent call last):",
            'ERROR [Worker]   File "/app/worker.py", line 120, in run',
            "ERROR [Worker]     price = position['price'] * fx_rate['rate']",
            "ERROR [Worker] TypeError: 'NoneType' object is not subscriptable",
            "ERROR [Worker] Batch failed due to NULL fx_rate for currency=EUR.",
        ]
        self._write_log_file("null_pointer_error.log", error_block, component="Worker")

    def generate_out_of_memory_log(self):
        error_block = [
            "INFO  [RiskEngine] Starting full revaluation.",
            "WARN  [RiskEngine] Memory usage at 85%.",
            "ERROR [RiskEngine] java.lang.OutOfMemoryError: Java heap space",
            "ERROR [RiskEngine] Risk run aborted. Increase -Xmx or reduce portfolio size.",
        ]
        self._write_log_file("out_of_memory.log", error_block, component="RiskEngine")

    def generate_config_missing_key_log(self):
        error_block = [
            "INFO  [ConfigLoader] Loading configuration from /etc/app/config.yaml",
            "ERROR [ConfigLoader] Missing required key: database.connection_string",
            "ERROR [App] Failed to start application due to configuration error.",
        ]
        self._write_log_file("config_missing_key.log", error_block, component="ConfigLoader")

    def generate_auth_failure_log(self):
        error_block = [
            "INFO  [AuthService] Login attempt for user=john.doe",
            "WARN  [AuthService] Invalid credentials for user=john.doe",
            "ERROR [AuthService] AuthenticationFailedException: invalid username or password.",
            "INFO  [ApiServer] Returning HTTP 401 for /login",
        ]
        self._write_log_file("auth_failure.log", error_block, component="AuthService")

    def generate_service_dependency_error_log(self):
        error_block = [
            "INFO  [OrderService] Creating order for user=alice",
            'ERROR [PaymentClient] 500 from payment-gateway: "Internal Server Error"',
            "ERROR [OrderService] Payment failed for order=12345 due to upstream error.",
        ]
        self._write_log_file("service_dependency_error.log", error_block, component="OrderService")

    def generate_disk_space_full_log(self):
        error_block = [
            "INFO  [BackupJob] Starting full backup.",
            "ERROR [BackupJob] IOError: [Errno 28] No space left on device",
            "ERROR [BackupJob] Backup failed due to insufficient disk space.",
        ]
        self._write_log_file("disk_space_full.log", error_block, component="BackupJob")

    def generate_generic_stacktrace_log(self):
        error_block = [
            "INFO  [ReportGenerator] Starting report job.",
            "ERROR [ReportGenerator] Unexpected error",
            "ERROR [ReportGenerator] Traceback (most recent call last):",
            'ERROR [ReportGenerator]   File "/app/report.py", line 90, in generate',
            "ERROR [ReportGenerator]     self._render(template, data)",
            "ERROR [ReportGenerator] KeyError: 'total_amount'",
            "ERROR [ReportGenerator] Job aborted due to missing key in data.",
        ]
        self._write_log_file("generic_stacktrace.log", error_block, component="ReportGenerator")

    def generate_all(self, all: bool = True, specific_file: str = ""):
        """
        Generate logs.
        - If all=True  -> generate all scenarios.
        - If specific_file contains a keyword like 'sql', 'db_timeout', etc.,
          only that log is generated.
        """
        key = specific_file.lower()

        if all or "sql" in key:
            self.generate_sql_syntax_error_log()
        if all or "db_timeout" in key:
            self.generate_db_timeout_log()
        if all or "network" in key:
            self.generate_network_connection_refused_log()
        if all or "null_pointer" in key:
            self.generate_null_pointer_error_log()
        if all or "out_of_memory" in key:
            self.generate_out_of_memory_log()
        if all or "config_missing_key" in key:
            self.generate_config_missing_key_log()
        if all or "auth_failure" in key:
            self.generate_auth_failure_log()
        if all or "service_dependency" in key:
            self.generate_service_dependency_error_log()
        if all or "disk_space_full" in key:
            self.generate_disk_space_full_log()
        if all or "generic_stacktrace" in key:
            self.generate_generic_stacktrace_log()


if __name__ == "__main__":
    LOGS_DIR.mkdir(exist_ok=True)
    generator = SampleLogGenerator(LOGS_DIR, total_lines=50)
    # Generate only SQL log:
    generator.generate_all(all=False, specific_file="sql")
    # Or generate everything:
    #generator.generate_all(all=True)
