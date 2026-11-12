"""Unit tests for TangentService."""

import unittest
from den_prototype.services.tangent_service import TangentService

class TestTangentService(unittest.TestCase):
    """Verifies NLP keyword parsing, topic classification, and starter generation."""

    def setUp(self):
        self.service = TangentService()

    def test_extract_debate_tangent(self):
        text = """
Dave: Monoliths are much easier to reason about.
Badri: Microservices give you domain boundary isolation vs monolith rot.
Dave: At what operational overhead though?
        """
        card = self.service.extract_tangent("Badri", "Dave", "Signal Export", text)
        self.assertEqual(card.category, "unfinished_debate")
        self.assertIn("The Unfinished Debate", card.title)
        self.assertIn("never settled that argument", card.starter_prompt)
        self.assertLessEqual(len(card.key_quotes), 3)

    def test_extract_decision_tangent(self):
        text = """
Dave: Got a leadership offer in Tokyo.
Badri: That is huge! Are you moving?
Dave: Weighing the timezone difference with family.
        """
        card = self.service.extract_tangent("Badri", "Dave", "WhatsApp Export", text)
        self.assertEqual(card.category, "unresolved_decision")
        self.assertIn("Pending Crossroads", card.title)
        self.assertIn("whatever happened with that decision", card.starter_prompt)

    def test_extract_rabbit_hole_tangent(self):
        text = """
Badri: Check out this Japanese jazz fusion record from 1978.
Dave: The Fender Rhodes tone on track 3 is sublime.
Badri: Pure analog tape saturation.
        """
        card = self.service.extract_tangent("Badri", "Dave", "Voice Note", text)
        self.assertEqual(card.category, "deep_rabbit_hole")
        self.assertIn("Shared Rabbit Hole", card.title)
        self.assertIn("tangent we got onto", card.starter_prompt)

    def test_empty_input_graceful_fallback(self):
        card = self.service.extract_tangent("Badri", "Dave", "Slack", "   \n\n  ")
        self.assertEqual(card.category, "deep_rabbit_hole")
        self.assertIn("Unspecified Thread", card.title)
        self.assertEqual(card.key_quotes, ["[No text provided]"])

    def test_stage_sparring_challenge(self):
        challenge = self.service.stage_sparring_challenge(
            author="Dave",
            target_user="badri",
            topic="SQLite WAL mode vs RocksDB on NVMe",
            argument="Read amplification on RocksDB isn't worth the overhead.",
            citation_link="https://sqlite.org/wal.html"
        )
        self.assertEqual(challenge.author, "Dave")
        self.assertEqual(challenge.target_user, "badri")
        self.assertEqual(challenge.status, "staged")
        self.assertIn("RocksDB", challenge.raw_argument)

if __name__ == "__main__":
    unittest.main()
