import datetime

def read_logs_between(log_file, start_time, end_time):
    """
    Reads logs between start_time and end_time.

    start_time and end_time must be strings in 'YYYY-MM-DD HH:MM:SS' format.
    """

    start_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_dt   = datetime.datetime.strptime(end_time,   "%Y-%m-%d %H:%M:%S")

    matched_logs = []

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                # Extract timestamp (first 19 chars)
                timestamp_str = line[:19]

                log_dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                if start_dt <= log_dt <= end_dt:
                    matched_logs.append(line)

            except Exception:
                # If the line doesn't match timestamp format, skip
                continue

    return matched_logs
