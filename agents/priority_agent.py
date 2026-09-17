from datetime import datetime
from typing import List

from models.schemas import Task, Priority


class PriorityAgent:
    """
    Determines task priority using transparent, deterministic rules.

    The agent does not invent priorities using free-form LLM reasoning.
    """

    def calculate_priority(self, task: Task) -> Priority:
        """
        Calculate priority based on deadline, status, and ownership.
        """

        # Unowned work is a high-risk item.
        if task.status.value == "unowned":
            return Priority.HIGH

        # Critical when the deadline is explicitly marked as critical.
        if task.deadline and "critical" in task.deadline.lower():
            return Priority.CRITICAL

        # High priority for active work with a known deadline.
        if task.status.value in {"open", "in_progress"} and task.deadline:
            return Priority.HIGH

        return Priority.MEDIUM

    def prioritize(self, tasks: List[Task]) -> List[Task]:
        """
        Apply priority calculation to all tasks.
        """

        for task in tasks:
            task.priority = self.calculate_priority(task)

        return tasks