import streamlit as st

from agents.graph import build_graph
from security.guards import validate_user_query


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="Executive Productivity Agent",
    page_icon="🤖",
    layout="wide"
)


# -----------------------------
# Styling
# -----------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        color: #666;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .metric-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        background-color: #fafafa;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Header
# -----------------------------

st.markdown(
    '<div class="main-title">🤖 Executive Productivity Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Multi-agent executive assistant for commitments, priorities, '
    'calendar conflicts and source-grounded decisions.'
    '</div>',
    unsafe_allow_html=True
)


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.header("Agent Architecture")

    st.success("🟢 Security Guard")

    st.write("Supervisor Agent")
    st.write("↳ Email Agent")
    st.write("↳ Meeting Agent")
    st.write("↳ Voice Agent")
    st.write("↳ Calendar Agent")
    st.write("↳ Commitment Agent")
    st.write("↳ Reconciliation Agent")
    st.write("↳ Priority Agent")
    st.write("↳ Executive Agent")

    st.divider()

    st.header("Security")

    st.write("✓ Prompt injection detection")
    st.write("✓ Query validation")
    st.write("✓ Source-grounding rules")
    st.write("✓ Read-only tools")

    st.divider()

    st.caption("Assignment 1 — Executive Productivity Agent")


# -----------------------------
# Query
# -----------------------------

st.subheader("Ask your Executive Agent")

query = st.text_area(
    "Executive query",
    placeholder=(
        "Example: What are my priority items this week?\n"
        "Example: Who owns the Mumbai lease renewal?\n"
        "Example: Show my calendar conflicts."
    ),
    height=100
)

ask = st.button(
    "🚀 Ask Executive Agent",
    type="primary",
    use_container_width=True
)


# -----------------------------
# Run Agent
# -----------------------------

if ask:

    if not query.strip():
        st.warning("Please enter a query.")
        st.stop()

    valid, message = validate_user_query(query)

    if not valid:
        st.error(f"🛡️ Request blocked: {message}")
        st.stop()

    with st.spinner("Agents are analyzing the available evidence..."):

        try:

            graph = build_graph()

            initial_state = {
                "user_query": query,
                "routes": [],
                "evidence": [],
                "tasks": [],
                "calendar_events": [],
                "conflicts": [],
                "final_response": "",
            }

            result = graph.invoke(initial_state)

            st.session_state["result"] = result

        except Exception as error:

            st.error(
                "The agent encountered an error while processing the request."
            )

            st.code(str(error))


# -----------------------------
# Display Result
# -----------------------------

if "result" in st.session_state:

    result = st.session_state["result"]

    st.divider()

    # -------------------------
    # Security
    # -------------------------

    st.subheader("🛡️ Security Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("Query validated")

    with col2:
        st.success("Read-only workflow")

    with col3:
        st.success("Source grounded")


    # -------------------------
    # Executive Response
    # -------------------------

    st.subheader("💼 Executive Summary")

    st.info(result.get("final_response", "No response generated."))


    # -------------------------
    # Tasks
    # -------------------------

    tasks = result.get("tasks", [])

    if tasks:

        st.subheader("📌 Commitments & Tasks")

        col1, col2, col3, col4 = st.columns(4)

        open_count = sum(
            1 for task in tasks
            if task.get("status") in ["open", "in_progress"]
        )

        scheduled_count = sum(
            1 for task in tasks
            if task.get("status") == "scheduled"
        )

        completed_count = sum(
            1 for task in tasks
            if task.get("status") == "completed"
        )

        unowned_count = sum(
            1 for task in tasks
            if task.get("status") == "unowned"
        )

        with col1:
            st.metric("Open", open_count)

        with col2:
            st.metric("Scheduled", scheduled_count)

        with col3:
            st.metric("Completed", completed_count)

        with col4:
            st.metric("Unowned", unowned_count)


        # Task details

        for task in tasks:

            status = task.get("status", "unknown")
            priority = task.get("priority", "unknown")

            with st.expander(
                f"{task.get('title', 'Unknown task')} "
                f"— {status.upper()}"
            ):

                c1, c2 = st.columns(2)

                with c1:
                    st.write(
                        f"**Owner:** {task.get('owner') or 'Unknown'}"
                    )

                    st.write(
                        f"**Stakeholder:** "
                        f"{task.get('stakeholder') or 'Unknown'}"
                    )

                    st.write(
                        f"**Deadline:** "
                        f"{task.get('deadline') or 'Unknown'}"
                    )

                with c2:

                    st.write(
                        f"**Status:** {status}"
                    )

                    st.write(
                        f"**Priority:** {priority}"
                    )

                    st.write(
                        f"**Confidence:** "
                        f"{task.get('confidence', 0):.0%}"
                    )

                evidence = task.get("evidence", [])

                if evidence:

                    st.markdown("**Evidence**")

                    for item in evidence[:3]:

                        st.caption(
                            f"{item.get('source_type')} | "
                            f"{item.get('source_id')}"
                        )

                        st.write(item.get("content", "")[:500])


    # -------------------------
    # Calendar Conflicts
    # -------------------------

    conflicts = result.get("conflicts", [])

    st.subheader("📅 Calendar Conflicts")

    if conflicts:

        for conflict in conflicts:
            st.warning(conflict)

    else:

        st.success("No calendar conflicts detected.")


    # -------------------------
    # Agent Routing
    # -------------------------

    routes = result.get("routes", [])

    if routes:

        st.subheader("🔀 Agent Routing")

        st.write(
            " → ".join(
                route.replace("_", " ").title()
                for route in routes
            )
        )


    # -------------------------
    # Evidence
    # -------------------------

    evidence = result.get("evidence", [])

    if evidence:

        st.subheader("🔎 Retrieved Evidence")

        st.caption(
            f"{len(evidence)} evidence items retrieved from supplied sources."
        )

        for item in evidence[:10]:

            with st.expander(
                f"{item.get('source_type', '').title()} — "
                f"{item.get('source_id', '')}"
            ):

                st.write(item.get("content", ""))


st.divider()

st.caption(
    "Prototype uses supplied assignment data only. "
    "The agent does not send emails, modify calendars, or execute external actions."
)