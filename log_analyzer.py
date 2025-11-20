"""
Main file for log analyzer
"""

import os
import time
import constants
from log_manager import get_logger, set_log_filename
from log_reader import read_logs_between



logger = get_logger()

logger.info("Log using default filename.")

# Change filename dynamically
set_log_filename(os.path.join(os.path.dirname(constants.LOG_FILENAME),"sql.log"))

for ite in range(100):
    logger.info(f"Log for my analysis: {ite}")
    #time.sleep(1)

start_time = "2025-11-16 00:10:45"
end_time   = "2025-11-16 00:10:48"

# Read logs
logs = read_logs_between(os.path.join(os.path.dirname(constants.LOG_FILENAME),"sql.log"), start_time, end_time)

print("\n=== FILTERED LOGS ===")
for line in logs:
    print(line, end="")




