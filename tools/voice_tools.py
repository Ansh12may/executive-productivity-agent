import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


VOICE_FILE = Path(__file__).parent.parent / "data" / "voice_notes.json"


STOPWORDS = {
    "what", "is", "the", "of", "a", "an", "and",
    "to", "for", "with", "on", "in", "my", "me",
    "this", "that", "about", "status", "show",
    "tell", "give", "please", "can", "you",
    "who", "when", "where", "do", "does"
}


def load_voice_notes() -> List[Dict[str, Any]]:

    with open(VOICE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_voice_note(
    voice_note_id: str
) -> Optional[Dict[str, Any]]:

    notes = load_voice_notes()

    for note in notes:

        if note["voice_note_id"] == voice_note_id:
            return note

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


def search_voice_notes(
    query: str
) -> List[Dict[str, Any]]:
    """
    Token-based relevance search over voice notes.
    """

    if not query or not query.strip():
        return []

    query_words = _tokenize(query)

    notes = load_voice_notes()

    scored = []

    for note in notes:

        searchable_text = (
            note["text"]
            + " "
            + note["speaker"]
            + " "
            + note["type"]
        )

        note_words = _tokenize(
            searchable_text
        )

        overlap = query_words.intersection(
            note_words
        )

        score = len(overlap)

        if score > 0:

            scored.append(
                (score, note)
            )

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        note
        for _, note in scored[:3]
    ]