"""Tangent Cartographer & Conversation Continuity Service."""

from typing import List, Tuple
from ..models.tangents import TangentCard, ConversationImport, SparringChallenge

class TangentService:
    """Extracts, categorizes, and indexes conversational tangents from imported transcripts."""

    DEBATE_KEYWORDS = [
        "debate", "disagree", "argue", "vs", "wrong", "better", "worse",
        "benchmark", "overkill", "monolith", "microservice", "rust", "python"
    ]
    DECISION_KEYWORDS = [
        "offer", "decide", "move", "quit", "join", "buy", "sell",
        "planning", "should i", "crossroads", "tokyo", "relocate", "career"
    ]

    def stage_sparring_challenge(
        self,
        author: str,
        target_user: str,
        topic: str,
        argument: str,
        citation_link: str = ""
    ) -> SparringChallenge:
        """Stages an intellectual challenge onto a buddy's coaster (Solo ammo -> Social debate)."""
        return SparringChallenge(
            author=author,
            target_user=target_user,
            topic=topic,
            raw_argument=argument,
            citation_link=citation_link
        )

    def extract_tangent(
        self,
        user_name: str,
        partner_name: str,
        source: str,
        raw_text: str
    ) -> TangentCard:
        """Parses transcript lines, classifies topic type, and generates conversation starter."""
        cleaned_text = (raw_text or "").strip()
        lines = [l.strip() for l in cleaned_text.splitlines() if l.strip()]

        if not lines:
            return TangentCard(
                title="Open Tangent: Unspecified Thread",
                category="deep_rabbit_hole",
                last_discussed=f"Imported from {source}",
                summary=f"Empty transcript imported from {source} between {user_name} and {partner_name}.",
                key_quotes=["[No text provided]"],
                starter_prompt=f"Hey {partner_name}, I was thinking about our conversation from {source}..."
            )

        lower_text = cleaned_text.lower()
        first_line = lines[0][:32]

        if any(k in lower_text for k in self.DEBATE_KEYWORDS):
            category = "unfinished_debate"
            title = f"The Unfinished Debate: '{first_line}'"
            starter = f"Hey {partner_name}, we never settled that argument from {source}..."
        elif any(k in lower_text for k in self.DECISION_KEYWORDS):
            category = "unresolved_decision"
            title = f"Pending Crossroads: '{first_line}'"
            starter = f"{partner_name}, whatever happened with that decision you were weighing?"
        else:
            category = "deep_rabbit_hole"
            title = f"Shared Rabbit Hole: '{first_line}'"
            starter = f"I was just thinking about that tangent we got onto in {source}..."

        quotes = lines[:3]
        summary = (
            f"Imported from {source} transcript between {user_name} and {partner_name}. "
            f"Found {len(lines)} message segments with an active conversational thread."
        )

        return TangentCard(
            title=title,
            category=category,
            last_discussed=f"Imported from {source}",
            summary=summary,
            key_quotes=quotes,
            starter_prompt=starter
        )
