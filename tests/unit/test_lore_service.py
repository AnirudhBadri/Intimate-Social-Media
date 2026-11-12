"""Unit tests for LoreService & 2-Party Consecration."""

import unittest
from den_prototype.services.lore_service import LoreService

class TestLoreService(unittest.TestCase):
    """Verifies lore storage and strict 2-party mutual consent consecration."""

    def setUp(self):
        self.service = LoreService()

    def test_add_inside_joke(self):
        joke = self.service.add_inside_joke(
            author="Dave",
            quote="CSS is my passion",
            context="After breaking the modal layout"
        )
        self.assertEqual(joke.author, "Dave")
        self.assertEqual(joke.consecrated_by, ["Dave"])
        self.assertFalse(joke.is_consecrated)
        self.assertIn(joke, self.service.inside_jokes)

    def test_two_party_consecration_flow(self):
        joke = self.service.add_inside_joke(
            author="Priya",
            quote="It converged in my dreams",
            context="Training run 42"
        )

        # 1. Duplicate vote by Priya should not consecrate
        res1 = self.service.consecrate_lore(joke.id, "Priya")
        self.assertTrue(res1["success"])
        self.assertFalse(res1["is_consecrated"])
        self.assertEqual(res1["votes"], ["Priya"])

        # 2. Second distinct vote by Badri satisfies 2-party consent
        res2 = self.service.consecrate_lore(joke.id, "Badri")
        self.assertTrue(res2["success"])
        self.assertTrue(res2["is_consecrated"])
        self.assertEqual(set(res2["votes"]), {"Priya", "Badri"})

    def test_consecrate_missing_joke(self):
        res = self.service.consecrate_lore("non_existent_id", "Badri")
        self.assertFalse(res["success"])
        self.assertIn("not found", res["error"])

if __name__ == "__main__":
    unittest.main()
