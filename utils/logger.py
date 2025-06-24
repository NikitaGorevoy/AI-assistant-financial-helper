import csv
import os
from datetime import datetime, timezone
from typing import Optional

LOG_FILE = "logs/agent_calls.csv"

def init_logging():
    """
    Создаёт файл логов с заголовками, если он ещё не существует.
    """
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "timestamp",
                "user_input",
                "tool_used",
                "step_duration_sec",
                "input_token_count",
                "output_token_count",
                "final_answer",
                "agent_thought",
                "error"
            ])
            writer.writeheader()


def clean(text: Optional[str]) -> str:
    if not text:
        return ""
    return str(text).replace('\n', ' ').replace('\r', ' ').strip()


def log_agent_call(user_input: str, tool_used: Optional[str], duration: Optional[float], input_tokens: int, output_tokens: int, final_answer: str, agent_thought: str = "", error: Optional[str] = ""):
    timestamp = datetime.now(timezone.utc).isoformat()

    with open(LOG_FILE, mode="a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp",
            "user_input",
            "tool_used",
            "step_duration_sec",
            "input_token_count",
            "output_token_count",
            "final_answer",
            "agent_thought",
            "error"
        ])
        writer.writerow({
            "timestamp": timestamp,
            "user_input": clean(user_input),
            "tool_used": clean(tool_used),
            "step_duration_sec": duration,
            "input_token_count": input_tokens,
            "output_token_count": output_tokens,
            "final_answer": clean(final_answer)[:5000],
            "agent_thought": clean(agent_thought)[:1000],
            "error": clean(error or "")[:1000]
        })
