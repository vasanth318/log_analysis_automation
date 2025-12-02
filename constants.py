

import os

# OpenAI
api_key = r"give your chagpt api key here"       
OPENAI_APIKEY = api_key 
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

# Logs directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Email settings (example – you MUST adapt for your environment)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "vasanthvamshi20@gmail.com"
SMTP_PASSWORD = "ifql tsbc vzcn myfp"   # App password, not plain account password
EMAIL_FROM = "vasanthvamshi20@gmail.com"
EMAIL_TO = "vasanthvamshi20@gmail.com"



from pathlib import Path
# Base directory where logs will be written (e.g., ./logs)
BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"

