# email_sender.py

import smtplib
from email.mime.text import MIMEText
from typing import List, Dict, Any

from constants import SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO


class EmailSender:
    def __init__(
        self,
        host: str = SMTP_HOST,
        port: int = SMTP_PORT,
        username: str = SMTP_USERNAME,
        password: str = SMTP_PASSWORD,
        from_addr: str = EMAIL_FROM,
        to_addr: str = EMAIL_TO,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addr = to_addr

    def build_report_body(self, analyses: List[Dict[str, Any]]) -> str:
        """
        Build a plain-text email body from a list of analysis dicts.
        """
        lines = []
        lines.append("Log Analysis Report")
        lines.append("===================\n")

        for result in analyses:
            lines.append(f"File: {result.get('file_name', 'N/A')}")
            tw = result.get("time_window", {})
            lines.append(f"Time Window: {tw.get('start', '')} -> {tw.get('end', '')}")
            lines.append(f"Severity: {result.get('severity', 'UNKNOWN')}")
            lines.append(f"Category: {result.get('category', 'UNKNOWN')}")
            lines.append("Summary:")
            lines.append(f"  {result.get('ai_summary', '')}")
            lines.append("Root Cause:")
            lines.append(f"  {result.get('root_cause', '')}")

            fixes = result.get("suggested_fixes", [])
            if fixes:
                lines.append("Suggested Fixes:")
                for f in fixes:
                    lines.append(f"  - {f}")

            highlights = result.get("error_highlights", [])
            if highlights:
                lines.append("Key Error Lines:")
                for h in highlights:
                    lines.append(f"  {h}")

            notes = result.get("additional_notes", "")
            if notes:
                lines.append("Additional Notes:")
                lines.append(f"  {notes}")

            lines.append("\n" + "-" * 60 + "\n")

        return "\n".join(lines)

    def send_report(self, analyses: List[Dict[str, Any]], subject: str = "Log Analysis Report"):
        body = self.build_report_body(analyses)
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = self.to_addr

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
'''
import smtplib
from email.mime.text import MIMEText

def send_gmail():
    sender = "vasanthvamshi20@gmail.com"
    password = "ifq myfp"   # your normal Gmail password
    receiver = "bandari.sunilkumar@gmail.com"

    msg = MIMEText("Test email without 2FA", "plain")
    msg["Subject"] = "SMTP Test"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("SMTP Error:", e)

send_gmail()'''

