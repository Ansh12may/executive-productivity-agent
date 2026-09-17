import re

from tools.email_tools import load_emails


class EmailThreadRetriever:

    _instance = None

    STOPWORDS = {
        "what", "is", "the", "of", "a", "an", "and",
        "to", "for", "with", "on", "in", "my", "me",
        "this", "that", "about", "status", "show",
        "tell", "give", "please", "can", "you"
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if getattr(self, "_initialized", False):
            return

        self.threads = load_emails()
        self._initialized = True

    def _tokenize(self, text: str):

        return {
            word
            for word in re.findall(
                r"\b[a-zA-Z0-9]+\b",
                text.lower()
            )
            if len(word) >= 3
            and word not in self.STOPWORDS
        }

    def _score(self, query, thread):

        query_words = self._tokenize(query)

        text = (
            thread["subject"]
            + " "
            + " ".join(
                email["body"]
                for email in thread["emails"]
            )
        )

        text_words = self._tokenize(text)

        # Exact token overlap instead of substring matching
        overlap = query_words.intersection(text_words)

        score = len(overlap)

        # Subject matches receive additional weight
        subject_words = self._tokenize(
            thread["subject"]
        )

        subject_overlap = query_words.intersection(
            subject_words
        )

        score += len(subject_overlap) * 3

        return score

    def search(
        self,
        query: str,
        top_k: int = 3
    ):

        if not query or not query.strip():
            return []

        scored = []

        for thread in self.threads:

            score = self._score(
                query,
                thread
            )

            if score > 0:
                scored.append(
                    (score, thread)
                )

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        results = []

        for score, thread in scored[:top_k]:

            results.append({
                "thread_id": thread["thread_id"],
                "subject": thread["subject"],
                "emails": thread["emails"],
                "score": float(score),
            })

        return results