#  Executive Productivity Agent

A multi-agent AI executive assistant built for **Arjun Malhotra, VP Sales**.

The agent analyzes supplied emails, calendars, meeting transcripts, and voice-note transcripts to identify commitments, deadlines, ownership, priorities, completed work, and calendar conflicts.

> **Assignment:** AIONOS — Assignment 1: Executive Productivity Agent

---

## Live Demo

**Streamlit App:**  
https://executive-appuctivity-agent-o37appc9up56tmhymkdkgsq.streamlit.app/

---

##  Problem

Executives receive information across multiple channels. Important commitments can become difficult to track when deadlines change, ownership is unclear, or information is spread across emails, meetings, voice notes, and calendars.

This agent provides a single executive view of:

- Open commitments
- Completed tasks
- Scheduled meetings
- Unowned responsibilities
- Deadlines
- Priorities
- Calendar conflicts
- Source evidence

---

## Architecture

The system uses a multi-agent architecture implemented with **LangGraph**.

```text
                    User Query
                        │
                        ▼
                ┌───────────────┐
                │   Supervisor  │
                │     Agent     │
                └───────┬───────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
     Email Agent   Meeting Agent   Voice Agent
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                 Calendar Agent
                        │
                        ▼
                Conflict Agent
                        │
                        ▼
               Commitment Agent
                        │
                        ▼
              Reconciliation Agent
                        │
                        ▼
                 Priority Agent
                        │
                        ▼
                Executive Agent
                        │
                        ▼
                Executive Brief
