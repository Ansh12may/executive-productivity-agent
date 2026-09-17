import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


MEETING_FILE = Path(__file__).parent.parent / "data" / "meetings.json"


STOPWORDS = {
    "what", "is", "the", "of", "a", "an", "and",
    "to", "for", "with", "on", "in", "my", "me",
    "this", "that", "about", "status", "show",
    "tell", "give", "please", "can", "you",
    "who", "when", "where", "do", "does"
}


def load_meetings() -> List[Dict[str, Any]]:
    """Load meeting data from the local source."""

    with open(MEETING_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_meeting(
    meeting_id: str
) -> Optional[Dict[str, Any]]:

    meetings = load_meetings()

    for meeting in meetings:

        if meeting["meeting_id"] == meeting_id:
            return meeting

    return None


def _tokenize(text: str):

    return {
        word
        for word in re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )
        if len(word) >= 3
        and word not in STOPWORDS
    }


def search_meetings(
    query: str
) -> List[Dict[str, Any]]:
    """
    Token-based relevance search over meeting titles
    and transcript content.
    """

    if not query or not query.strip():
        return []

    query_words = _tokenize(query)

    meetings = load_meetings()

    scored = []

    for meeting in meetings:

        title = meeting["title"]

        transcript_text = " ".join(
            entry["speaker"] + " " + entry["text"]
            for entry in meeting["transcript"]
        )

        title_words = _tokenize(title)
        transcript_words = _tokenize(transcript_text)

        title_overlap = query_words.intersection(
            title_words
        )

        transcript_overlap = query_words.intersection(
            transcript_words
        )

        score = (
            len(title_overlap) * 3
            + len(transcript_overlap)
        )

        if score > 0:

            scored.append(
                (score, meeting)
            )

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        meeting
        for _, meeting in scored[:3]
    ]