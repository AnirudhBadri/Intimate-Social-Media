"""Unit tests for GameService (Slow Board Game)."""

import unittest
from den_prototype.services.game_service import GameService
from den_prototype.models.social import SlowGameState

class TestGameService(unittest.TestCase):
    """Verifies slow board game asynchronous turn progression and player rotation."""

    def test_default_game_state(self):
        service = GameService()
        self.assertEqual(service.slow_game.turn_number, 14)
        self.assertEqual(service.slow_game.active_player_name, "Dave")

    def test_take_turn_increments_and_rotates(self):
        service = GameService()
        init_turn = service.slow_game.turn_number
        updated = service.take_turn("Dave")

        self.assertEqual(updated.turn_number, init_turn + 1)
        self.assertIn("Dave rolled 7", updated.last_move_description)
        # Next player in ["Badri", "Priya", "Sam", "Dave"] after Dave is Badri
        self.assertEqual(updated.active_player_name, "Badri")

        # Advance again from Badri
        updated2 = service.take_turn("Badri")
        self.assertEqual(updated2.active_player_name, "Priya")

    def test_custom_initial_state(self):
        custom = SlowGameState(turn_number=100, active_player_name="Sam")
        service = GameService(initial_state=custom)
        self.assertEqual(service.slow_game.turn_number, 100)
        updated = service.take_turn("Sam")
        self.assertEqual(updated.turn_number, 101)
        self.assertEqual(updated.active_player_name, "Dave")

if __name__ == "__main__":
    unittest.main()
