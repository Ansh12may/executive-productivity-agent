import json
from pathlib import Path
from typing import List, Dict, Any


EMAIL_FILE = Path(__file__).parent.parent / "data" / "emails.json"


def load_emails() -> List[Dict[str, Any]]:
    """Load all email threads from the local data source."""
    with open(EMAIL_FILE, "r", encoding="utf-8") as file:
        return json.load(file)



def get_email_thread(thread_id: str) -> Dict[str, Any] | None:
    """Retrieve one complete email thread by thread ID."""

    emails = load_emails()

    for thread in emails:
        if thread["thread_id"] == thread_id:
            return thread

    return None