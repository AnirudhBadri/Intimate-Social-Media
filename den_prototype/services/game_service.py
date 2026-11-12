"""Slow Board Game Service for asynchronous companionable play."""

from typing import Optional, List
from ..models.social import SlowGameState

class GameService:
    """Manages asynchronous slow board game state and turn rotation."""

    DEFAULT_PLAYERS: List[str] = ["Badri", "Priya", "Sam", "Dave"]

    def __init__(self, initial_state: Optional[SlowGameState] = None):
        self.slow_game: SlowGameState = initial_state or SlowGameState()

    def take_turn(self, player_name: str) -> SlowGameState:
        """Advances the slow game turn, rolls the dice, and rotates active player."""
        self.slow_game.turn_number += 1
        self.slow_game.last_move_description = (
            f"{player_name} rolled 7! Advanced to 'Community Chest' and drew: "
            f"'Take a midnight walk with a buddy'."
        )

        curr_idx = (
            self.DEFAULT_PLAYERS.index(player_name)
            if player_name in self.DEFAULT_PLAYERS
            else 0
        )
        next_idx = (curr_idx + 1) % len(self.DEFAULT_PLAYERS)
        self.slow_game.active_player_name = self.DEFAULT_PLAYERS[next_idx]
        return self.slow_game
