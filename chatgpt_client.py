# chatgpt_client.py

import json
from openai import OpenAI
from constants import OPENAI_APIKEY, OPENAI_MODEL
from typing import Dict, Any

from constants import OPENAI_APIKEY, OPENAI_MODEL
from typing import Dict, Any


LOG_ANALYSIS_SYSTEM_PROMPT = """
You are an expert software log analyst with deep knowledge of debugging, root cause analysis, and issue resolution in production and development environments.

I will provide you with:
- A log snippet (from application, backend, or service logs)
- The log file name
- The time window used to extract the logs (start_time, end_time)
- Optionally, a short description of the context

Your task is to:
1. Read and analyze the logs carefully (bottom-up if needed) to find the FIRST real failure.
2. Identify the ROOT CAUSE:
   - What exactly went wrong?
   - Where did it happen (module/component/operation if visible)?
   - Why did it happen (most likely cause)?
3. Classify the error into one of the following categories:
   - CONFIGURATION
   - CODE_LOGIC
   - DATABASE
   - NETWORK
   - AUTHENTICATION
   - RESOURCE_LIMIT
   - EXTERNAL_DEPENDENCY
   - UNKNOWN
4. Assign a severity:
   - LOW, MEDIUM, HIGH, or CRITICAL
5. Provide:
   - A short human-readable summary (2–3 lines)
   - A detailed root cause explanation
   - Clear, actionable FIX steps for a developer or SRE (code change, config change, infra fix, or follow-up investigation)
6. Highlight 3–10 key log lines that BEST show the failure and its cause.
7. Focus only on the PRIMARY failure, not all secondary cascading errors.

You MUST respond ONLY with valid JSON in the following exact schema:

{
  "file_name": "<log file name sent in the prompt>",
  "time_window": {
    "start": "<start_time passed in the prompt>",
    "end": "<end_time passed in the prompt>"
  },
  "severity": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "category": "<CONFIGURATION|CODE_LOGIC|DATABASE|NETWORK|AUTHENTICATION|RESOURCE_LIMIT|EXTERNAL_DEPENDENCY|UNKNOWN>",
  "ai_summary": "2-3 line brief explanation of what failed.",
  "root_cause": "Detailed description of the most likely root cause.",
  "suggested_fixes": [
    "Actionable step 1",
    "Actionable step 2"
  ],
  "error_highlights": [
    "Important log line 1",
    "Important log line 2",
    "..."
  ],
  "additional_notes": "Optional extra context. Can be an empty string if nothing to add."
}

Rules:
- Do NOT include markdown, HTML, or any text outside this JSON.
- Do NOT change field names or the JSON structure.
- If you are not certain, you MUST still provide your best guess in a safe and conservative way.
"""


class ChatGPTClient:
    def __init__(self, api_key: str = None, model: str = None, temperature: float = 0.2):
        self.client = OpenAI(api_key=api_key or OPENAI_APIKEY)
        self.model = model or OPENAI_MODEL
        self.temperature = temperature
      
    def parse_openai_json_block(self,text: str):
      text = text.strip()
      if text.startswith("```"):
          # Remove opening fence like ```json or ```python
          first_newline = text.find("\n")
          text = text[first_newline:].rstrip("`").strip()
      if text.endswith("```"):
          text = text[:-3].strip()
      return json.loads(text)


    def analyze_log(
        self,
        file_name: str,
        log_text: str,
        start_time: str,
        end_time: str,
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Sends log text to the ChatGPT model with the analysis system prompt and
        returns a parsed JSON dict.
        """
        user_prompt = f"""
File name: {file_name}
Time window: start={start_time}, end={end_time}
Context: {context}

Here are the logs:

-------------------- LOG START --------------------
{log_text}
-------------------- LOG END --------------------
"""

        response = self.client.responses.create(
            model=self.model,
            temperature=self.temperature,
            input=[
                {"role": "system", "content": LOG_ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt.strip()},
            ],
        )

        raw_text = response.output_text

        try:
            data = self.parse_openai_json_block(raw_text)
            return data
        except json.JSONDecodeError:
            # Fallback if model output is not perfect JSON
            return {
                "file_name": file_name,
                "time_window": {"start": start_time, "end": end_time},
                "severity": "UNKNOWN",
                "category": "UNKNOWN",
                "ai_summary": "Failed to parse JSON from model output.",
                "root_cause": "Model returned non-JSON output.",
                "suggested_fixes": ["Inspect raw_output in the report.", "Refine the prompt or logs."],
                "error_highlights": [],
                "additional_notes": raw_text,
            }
