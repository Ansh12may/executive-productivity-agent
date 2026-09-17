from models.schemas import Task, TaskStatus


class ReconciliationAgent:
    def reconcile(self, tasks):
        for task in tasks:
            if not task.evidence:
                continue

            evidence_text = " ".join(
                evidence.content.lower()
                for evidence in task.evidence
            )

            unowned_signals = [
                "still unowned",
                "still unassigned",
                "unassigned",
                "no one picked it up",
                "not assigned",
                "unclear who",
                "ownership is unclear"
            ]

            if any(
                signal in evidence_text
                for signal in unowned_signals
            ):

                task.status = TaskStatus.UNOWNED

                task.owner = None

                task.confidence = max(
                    task.confidence,
                    0.90
                )

                continue 
        return tasks