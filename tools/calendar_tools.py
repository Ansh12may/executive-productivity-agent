import json
from pathlib import Path
from typing import List, Dict, Any


CALENDAR_FILE = (
    Path(__file__).parent.parent
    / "data"
    / "calendar.json"
)


def load_calendar() -> List[Dict[str, Any]]:
    with open(CALENDAR_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_calendar(person: str) -> List[Dict[str, Any]]:
    events = load_calendar()

    return [
        event
        for event in events
        if event["person"].lower() == person.lower()
    ]


def check_conflicts(
    person: str,
    date: str
) -> List[Dict[str, Any]]:

    events = [
        event
        for event in get_calendar(person)
        if event["date"] == date
    ]

    events.sort(
        key=lambda event: event["start_time"]
    )

    conflicts = []

    for i in range(len(events)):

        current = events[i]

        for j in range(i + 1, len(events)):

            next_event = events[j]

            if current["end_time"] > next_event["start_time"]:

                conflicts.append({
                    "date": date,
                    "person": person,
                    "event_1": current,
                    "event_2": next_event
                })

    return conflicts


# CROSS-PERSON CONFLICT DETECTION

def check_cross_person_conflicts(
    date: str,
    primary_person: str = "Arjun Malhotra"
) -> List[Dict[str, Any]]:

    events = load_calendar()

    # Only look at events on the requested date.
    events = [
        event
        for event in events
        if event["date"] == date
    ]

    conflicts = []

    for i in range(len(events)):

        event_a = events[i]

        for j in range(i + 1, len(events)):

            event_b = events[j]

            # We only care about conflicts involving
            # the executive.
            if (
                event_a["person"].lower() != primary_person.lower()
                and
                event_b["person"].lower() != primary_person.lower()
            ):
                continue

            # Same person is handled separately.
            if event_a["person"] == event_b["person"]:
                continue

            # Ignore generic blocked periods.
            if (
                event_a["title"].lower() == "blocked"
                or
                event_b["title"].lower() == "blocked"
            ):
                continue

            # If both people have the same meeting,
            # they are attending the same event rather
            # than conflicting with each other.
            if event_a["title"] == event_b["title"]:
                continue

            # Standard interval overlap.
            if (
                event_a["start_time"] < event_b["end_time"]
                and
                event_b["start_time"] < event_a["end_time"]
            ):

                conflicts.append({
                    "date": date,
                    "person_1": event_a["person"],
                    "event_1": event_a,
                    "person_2": event_b["person"],
                    "event_2": event_b
                })

    return conflicts