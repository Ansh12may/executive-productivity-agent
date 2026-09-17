from typing import Dict, Any

from langchain_groq import ChatGroq

from tools.calendar_tools import (
    get_calendar,
    check_conflicts
)


class CalendarAgent:
    """
    Specialist agent responsible for calendar information.

    Responsibilities:
    - Retrieve a person's calendar
    - Detect scheduling conflicts
    - Provide calendar evidence to downstream agents
    """

    def __init__(self, model: ChatGroq):
        self.model = model

    def get_schedule(self, person: str) -> Dict[str, Any]:
        """
        Retrieve calendar events for a person.
        """

        events = get_calendar(person)

        return {
            "person": person,
            "source": "calendar",
            "events": events
        }

    def find_conflicts(
        self,
        person: str,
        date: str
    ) -> Dict[str, Any]:
        """
        Detect conflicts within one person's calendar.
        """

        conflicts = check_conflicts(person, date)

        return {
            "person": person,
            "date": date,
            "source": "calendar",
            "conflicts": conflicts
        }