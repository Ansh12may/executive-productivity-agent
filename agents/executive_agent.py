from typing import List

from langchain_groq import ChatGroq

from models.schemas import Task, CalendarEvent


class ExecutiveAgent:
    """
    Synthesizes information from specialist agents into
    an executive-friendly response.
    """

    def __init__(self, model: ChatGroq):
        self.model = model

    def build_context(
        self,
        tasks: List[Task],
        calendar_events: List[CalendarEvent],
        conflicts: List[str]
    ) -> str:
        """
        Convert structured state into context for the LLM.
        """

        task_text = "\n".join(
            [
                f"- {task.title} | "
                f"Owner: {task.owner or 'Unknown'} | "
                f"Deadline: {task.deadline or 'Unknown'} | "
                f"Status: {task.status.value} | "
                f"Priority: {task.priority.value}"
                for task in tasks
            ]
        )

        calendar_text = "\n".join(
            [
                f"- {event.person}: "
                f"{event.date} {event.start_time}-{event.end_time} "
                f"{event.title}"
                for event in calendar_events
            ]
        )

        conflict_text = "\n".join(
            [f"- {conflict}" for conflict in conflicts]
        )

        return f"""
TASKS:
{task_text or "No tasks found."}

CALENDAR:
{calendar_text or "No calendar events found."}

CONFLICTS:
{conflict_text or "No conflicts found."}
"""

    def generate_response(
        self,
        tasks: List[Task],
        calendar_events: List[CalendarEvent],
        conflicts: List[str]
    ) -> str:
        """
        Generate the final executive-facing response.
        """

        context = self.build_context(
            tasks,
            calendar_events,
            conflicts
        )

        prompt = f"""
You are an executive productivity assistant.

Use ONLY the information provided in the context.

Do not invent:
- tasks
- owners
- deadlines
- status
- meetings
- priorities

If information is unknown, explicitly say it is unknown.

Organize the response into:
1. Priority items
2. Open commitments
3. Calendar conflicts
4. Completed items

Keep the response concise and actionable.

CONTEXT:
{context}
"""

        response = self.model.invoke(prompt)

        return response.content