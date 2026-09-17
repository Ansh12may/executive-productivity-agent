from typing import TypedDict, List, Optional

from langgraph.graph import StateGraph, END

from config.llm import get_llm
from models.schemas import Evidence, Task, CalendarEvent

from agents.supervisor import SupervisorAgent
from agents.commitment_agent import CommitmentAgent
from agents.reconciliation_agent import ReconciliationAgent
from agents.priority_agent import PriorityAgent
from agents.executive_agent import ExecutiveAgent

from tools.retriever import EmailThreadRetriever
from tools.meeting_tools import search_meetings, load_meetings
from tools.voice_tools import search_voice_notes, load_voice_notes
from tools.calendar_tools import (
    get_calendar,
    check_cross_person_conflicts
)

from security.guards import validate_user_query

# GRAPH STATE
class GraphState(TypedDict):

    user_query: str

    # Supervisor output
    routes: List[str]
    entity: Optional[str]

    # Shared state
    evidence: List[dict]
    tasks: List[dict]
    calendar_events: List[dict]
    conflicts: List[str]

    # Final response
    final_response: str



def security_node(state):

    is_valid, message = validate_user_query(
        state["user_query"]
    )

    if not is_valid:

        state["final_response"] = (
            f"Request blocked: {message}"
        )

        state["routes"] = []
        state["entity"] = None
        state["evidence"] = []
        state["tasks"] = []
        state["calendar_events"] = []
        state["conflicts"] = []

    return state


def route_after_security(state):

    if state["final_response"]:
        return "blocked"

    return "allowed"


def supervisor_node(state):

    supervisor = SupervisorAgent(
        get_llm()
    )

    plan = supervisor.create_plan(
        state["user_query"]
    )

    state["routes"] = plan.sources
    state["entity"] = plan.entity

    return state



def email_node(state):

    if "email" not in state["routes"]:
        return state

    retriever = EmailThreadRetriever()

    results = retriever.search(
        state["user_query"],
        top_k=3
    )

    for thread in results:

        for email in thread["emails"]:

            state["evidence"].append(
                {
                    "source_type": "email",
                    "source_id": email["id"],
                    "content": (
                        f"From: {email['from']}\n"
                        f"To: {', '.join(email['to'])}\n"
                        f"Timestamp: {email['timestamp']}\n"
                        f"Subject: {thread['subject']}\n"
                        f"Body: {email['body']}"
                    )
                }
            )

    return state


def meeting_node(state):

    if "meeting" not in state["routes"]:
        return state

    query = state["user_query"].lower()

    broad_query = any(
        keyword in query
        for keyword in [
            "important",
            "priority",
            "priorities",
            "this week",
            "executive",
            "brief",
            "overview",
            "commitments"
        ]
    )

    if broad_query:

        results = load_meetings()

    else:

        results = search_meetings(
            state["user_query"]
        )

    for meeting in results:

        for entry in meeting["transcript"]:

            state["evidence"].append(
                {
                    "source_type": "meeting",
                    "source_id": meeting["meeting_id"],
                    "content": (
                        f"{entry['speaker']}: "
                        f"{entry['text']}"
                    )
                }
            )

    return state




def voice_node(state):

    if "voice" not in state["routes"]:
        return state

    query = state["user_query"].lower()

    broad_query = any(
        keyword in query
        for keyword in [
            "important",
            "priority",
            "priorities",
            "this week",
            "executive",
            "brief",
            "overview",
            "commitments"
        ]
    )

    if broad_query:

        results = load_voice_notes()

    else:

        results = search_voice_notes(
            state["user_query"]
        )

    for note in results:

        state["evidence"].append(
            {
                "source_type": "voice_note",
                "source_id": note["voice_note_id"],
                "content": note["text"]
            }
        )

    return state


def calendar_node(state):

    if "calendar" not in state["routes"]:
        return state

    state["calendar_events"] = get_calendar(
        "Arjun Malhotra"
    )

    return state



def conflict_node(state):

    if "calendar" not in state["routes"]:
        return state

    conflicts = check_cross_person_conflicts(
        "2026-09-24",
        primary_person="Arjun Malhotra"
    )

    state["conflicts"] = [
        (
            f"{conflict['person_1']} — "
            f"{conflict['event_1']['title']} "
            f"({conflict['event_1']['start_time']}-"
            f"{conflict['event_1']['end_time']}) "
            f"overlaps with "
            f"{conflict['person_2']} — "
            f"{conflict['event_2']['title']} "
            f"({conflict['event_2']['start_time']}-"
            f"{conflict['event_2']['end_time']}) "
            f"on {conflict['date']}."
        )
        for conflict in conflicts
    ]

    return state




def commitment_node(state):

    if not state["evidence"]:
        return state

    evidence_objects = [
        Evidence(**item)
        for item in state["evidence"]
    ]

    agent = CommitmentAgent(
        get_llm()
    )

    tasks = agent.extract_tasks(
        evidence_objects,
        entity=state.get("entity")
    )

    state["tasks"] = [
        task.model_dump()
        for task in tasks
    ]

    return state




def reconciliation_node(state):

    if not state["tasks"]:
        return state

    tasks = [
        Task(**task)
        for task in state["tasks"]
    ]

    agent = ReconciliationAgent()

    tasks = agent.reconcile(tasks)

    state["tasks"] = [
        task.model_dump()
        for task in tasks
    ]

    return state




def priority_node(state):

    if not state["tasks"]:
        return state

    tasks = [
        Task(**task)
        for task in state["tasks"]
    ]

    agent = PriorityAgent()

    tasks = agent.prioritize(tasks)

    state["tasks"] = [
        task.model_dump()
        for task in tasks
    ]

    return state


def executive_node(state):

    tasks = [
        Task(**task)
        for task in state["tasks"]
    ]

    calendar_events = [
        CalendarEvent(**event)
        for event in state["calendar_events"]
    ]


    if (
        "calendar" in state["routes"]
        and not state["tasks"]
        and state["conflicts"]
    ):

        state["final_response"] = (
            "Calendar conflicts:\n\n"
            + "\n".join(
                f"- {conflict}"
                for conflict in state["conflicts"]
            )
        )

        return state


    agent = ExecutiveAgent(
        get_llm()
    )

    response = agent.generate_response(
        tasks=tasks,
        calendar_events=calendar_events,
        conflicts=state["conflicts"]
    )

    state["final_response"] = response

    return state




def build_graph(model=None):

    graph = StateGraph(GraphState)

  

    graph.add_node(
        "security",
        security_node
    )

    graph.add_node(
        "supervisor",
        supervisor_node
    )

    graph.add_node(
        "email_agent",
        email_node
    )

    graph.add_node(
        "meeting_agent",
        meeting_node
    )

    graph.add_node(
        "voice_agent",
        voice_node
    )

    graph.add_node(
        "calendar_agent",
        calendar_node
    )

    graph.add_node(
        "conflict_agent",
        conflict_node
    )

    graph.add_node(
        "commitment_agent",
        commitment_node
    )

    graph.add_node(
        "reconciliation_agent",
        reconciliation_node
    )

    graph.add_node(
        "priority_agent",
        priority_node
    )

    graph.add_node(
        "executive_agent",
        executive_node
    )

   

    graph.set_entry_point(
        "security"
    )

    
    graph.add_conditional_edges(
        "security",
        route_after_security,
        {
            "allowed": "supervisor",
            "blocked": END
        }
    )

   

    def route_specialists(state):

        routes = state["routes"]

        if "email" in routes:
            return "email_agent"

        if "meeting" in routes:
            return "meeting_agent"

        if "voice" in routes:
            return "voice_agent"

        if "calendar" in routes:
            return "calendar_agent"

        return "commitment_agent"

    graph.add_conditional_edges(
        "supervisor",
        route_specialists,
        {
            "email_agent": "email_agent",
            "meeting_agent": "meeting_agent",
            "voice_agent": "voice_agent",
            "calendar_agent": "calendar_agent",
            "commitment_agent": "commitment_agent"
        }
    )

    

    graph.add_edge(
        "email_agent",
        "meeting_agent"
    )

    graph.add_edge(
        "meeting_agent",
        "voice_agent"
    )

    graph.add_edge(
        "voice_agent",
        "calendar_agent"
    )

    graph.add_edge(
        "calendar_agent",
        "conflict_agent"
    )

    graph.add_edge(
        "conflict_agent",
        "commitment_agent"
    )

   

    graph.add_edge(
        "commitment_agent",
        "reconciliation_agent"
    )

    graph.add_edge(
        "reconciliation_agent",
        "priority_agent"
    )

    graph.add_edge(
        "priority_agent",
        "executive_agent"
    )

    graph.add_edge(
        "executive_agent",
        END
    )

    return graph.compile()