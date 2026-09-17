import json
from typing import List, Optional, Literal

from langchain_groq import ChatGroq
from pydantic import BaseModel, ValidationError


class QueryPlan(BaseModel):
    intent: Literal[
        "commitment_status",
        "executive_brief",
        "calendar_conflict",
        "source_lookup",
        "unknown"
    ]

    sources: List[
        Literal["email", "meeting", "voice", "calendar"]
    ]

    entity: Optional[str] = None


class SupervisorAgent:
    """
    Semantic supervisor.

    The Supervisor does not retrieve data or perform business logic.
    It decides:
      1. What the user is asking
      2. Which source agents are required
      3. Which entity/topic is relevant

    Execution remains deterministic in the graph.
    """

    def __init__(self, model: ChatGroq):
        self.model = model

    def _clean_json(self, text: str) -> str:
        text = text.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines)

        return text.strip()

    def create_plan(self, user_query: str) -> QueryPlan:

        prompt = f"""
You are the Supervisor Agent for an executive productivity system.

Analyze the user's request and return ONLY valid JSON.

User request:
{user_query}

Choose exactly one intent:

commitment_status
- Questions about commitments, tasks, ownership, deadlines, completion or status.

executive_brief
- Broad request for priorities, overview, weekly brief or important items.

calendar_conflict
- Questions about calendar conflicts, scheduling clashes or availability.

source_lookup
- User explicitly asks about information contained in a particular source.

unknown
- Cannot confidently determine the request.

Choose the sources needed to establish the CURRENT and LATEST state.

email
- Use for email commitments, requests, confirmations, deadline changes,
  completion updates, client calls, vendor lists, expenses and lease matters.
- For a commitment-status query involving a named task, prefer email when
  the task may have changed state through email.

meeting
- Use for commitments explicitly made or discussed in meetings.
- Use when the user asks about a meeting, transcript, or Leadership Sync.

voice
- Use for Arjun's personal reminders and commitments.

calendar
- Use for scheduling, calendar events and conflicts.

IMPORTANT:
For a commitment-status query involving a named task, you may select
MORE THAN ONE source when needed to reconstruct the latest state.

Example:

User: What is the status of the Meridian Logistics call?

JSON:
{{"intent":"commitment_status","sources":["email","meeting"],"entity":"Meridian Logistics"}}

Do not select meeting alone when email contains confirmation or
status updates for the same commitment.

Entity should be the main topic if one is clearly identifiable.
Examples:
- "vendor list"
- "expense variance"
- "Meridian Logistics"
- "Mumbai office lease"
- null

Examples:

User: What is the status of the vendor list?
JSON:
{{"intent":"commitment_status","sources":["email"],"entity":"vendor list"}}

User: What did I commit to in the leadership sync?
JSON:
{{"intent":"commitment_status","sources":["meeting"],"entity":"Leadership Sync"}}

User: Give me my executive priorities for this week.
JSON:
{{"intent":"executive_brief","sources":["email","meeting","voice","calendar"],"entity":null}}

User: Are there any calendar conflicts on Thursday?
JSON:
{{"intent":"calendar_conflict","sources":["calendar"],"entity":"Thursday"}}

Rules:
- Do not invent sources.
- Do not retrieve information.
- Do not answer the user.
- Return ONLY JSON.
"""

        try:
            response = self.model.invoke(prompt)
            raw = response.content if hasattr(response, "content") else str(response)

            cleaned = self._clean_json(raw)

            data = json.loads(cleaned)

            return QueryPlan.model_validate(data)

        except (json.JSONDecodeError, ValidationError, Exception):
            # Safe fallback.
            return QueryPlan(
                intent="unknown",
                sources=["email", "meeting", "voice", "calendar"],
                entity=None
            )