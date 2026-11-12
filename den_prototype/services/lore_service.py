"""Lore Vault & 2-Party Mutual Consecration Service."""

from typing import List, Dict, Any, Optional
from ..models.social import LoreItem

class LoreService:
    """Manages inside jokes, room lore, and 2-party mutual consecration."""

    def __init__(self, initial_lore: Optional[List[LoreItem]] = None):
        self.inside_jokes: List[LoreItem] = initial_lore if initial_lore is not None else []

    def add_inside_joke(self, author: str, quote: str, context: str) -> LoreItem:
        """Adds a candidate inside joke with 1 initial endorsement from author."""
        joke = LoreItem(
            author=author,
            quote=quote,
            context=context,
            consecrated_by=[author],
            is_consecrated=False
        )
        self.inside_jokes.insert(0, joke)
        return joke

    def consecrate_lore(self, joke_id: str, user_name: str) -> Dict[str, Any]:
        """Enforces Theme 7: 2-Party Mutual Consecration.
        Lore is only permanently enshrined once at least 2 distinct members endorse it.
        """
        for joke in self.inside_jokes:
            if joke.id == joke_id:
                if user_name not in joke.consecrated_by:
                    joke.consecrated_by.append(user_name)
                if len(joke.consecrated_by) >= 2:
                    joke.is_consecrated = True
                return {
                    "success": True,
                    "is_consecrated": joke.is_consecrated,
                    "votes": list(joke.consecrated_by)
                }
        return {"success": False, "error": "Lore item not found"}
