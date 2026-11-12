"""Integration tests for all HTTP API endpoints of The Den."""

import unittest
from starlette.testclient import TestClient
from den_prototype.app import app

class TestApiEndpoints(unittest.TestCase):
    """End-to-end integration tests for all FastAPI REST endpoints."""

    def setUp(self):
        self.client = TestClient(app)

    def test_frontend_template_render(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("The Den", resp.text)
        self.assertIn("webgl-canvas", resp.text)
        self.assertIn("scene-switcher", resp.text)

    def test_get_state(self):
        resp = self.client.get("/api/state")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("name", data)
        self.assertIn("users", data)
        self.assertEqual(data["dunbar_cap"], 15)
        self.assertGreaterEqual(len(data["users"]), 4)

    def test_den_switch_endpoint(self):
        resp = self.client.post("/api/den/switch", json={"den_id": "personal"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["state"]["den_type"], "personal")
        self.assertIn("Sovereign Hearth", data["state"]["name"])

        # Switch back to buddies
        self.client.post("/api/den/switch", json={"den_id": "buddies"})

    def test_ember_endpoint(self):
        resp = self.client.post("/api/ember", json={"from_user": "badri", "to_user": "dave"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["ember"]["to"], "Dave")

    def test_poll_vote_endpoint(self):
        resp = self.client.post("/api/poll/vote", json={"option_id": "opt1", "user_id": "dave"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])

    def test_inside_joke_and_consecration_endpoints(self):
        # 1. Add joke
        j_resp = self.client.post("/api/joke", json={
            "author": "Priya",
            "quote": "Gradient descent is just gravity for weights",
            "context": "Late night math session"
        })
        self.assertEqual(j_resp.status_code, 200)
        joke = j_resp.json()["joke"]
        joke_id = joke["id"]

        # 2. Consecrate with second party
        c_resp = self.client.post("/api/lore/consecrate", json={
            "joke_id": joke_id,
            "user_name": "Badri"
        })
        self.assertEqual(c_resp.status_code, 200)
        self.assertTrue(c_resp.json()["is_consecrated"])

    def test_roast_endpoint(self):
        resp = self.client.post("/api/roast", json={
            "from_user": "badri",
            "target_user": "dave",
            "message": "Nice variable names, did your cat walk on the keyboard?"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])

    def test_slow_game_endpoint(self):
        resp = self.client.post("/api/game/roll", json={"player_name": "Badri"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertIn("turn_number", data["game"])

    def test_theme_generation_endpoint(self):
        resp = self.client.post("/api/theme", json={"prompt": "rainy izakaya tokyo"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["theme"]["theme_name"], "Neo-Tokyo Rainy Izakaya")

    def test_avatar_and_feed_update_endpoints(self):
        # Update avatar
        av_resp = self.client.post("/api/user/avatar", json={
            "user_id": "badri",
            "avatar_config": {
                "outfit_color": "#10b981",
                "skin_tone": "#fbcfe8",
                "hair_color": "#1c1917",
                "hair_style": "cap",
                "drink": "scotch",
                "accessory": "glasses"
            }
        })
        self.assertEqual(av_resp.status_code, 200)
        self.assertTrue(av_resp.json()["success"])

        # Update feeds
        feed_resp = self.client.post("/api/user/feeds", json={
            "user_id": "badri",
            "spotify_track": "Idioteque",
            "spotify_artist": "Radiohead",
            "letterboxd_title": "Interstellar",
            "letterboxd_rating": 5.0,
            "github_repo": "badri/the-den",
            "github_commit": "refactor: modular routers"
        })
        self.assertEqual(feed_resp.status_code, 200)
        self.assertTrue(feed_resp.json()["success"])

    def test_booth_import_and_artifacts_endpoints(self):
        # Import chat thread
        booth_resp = self.client.post("/api/booth/import", json={
            "user_id": "badri",
            "partner_id": "dave",
            "source": "Signal Export",
            "raw_text": "Dave: Monorepo vs multirepo debate is never ending.\nBadri: Monorepos win for small teams."
        })
        self.assertEqual(booth_resp.status_code, 200)
        data = booth_resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["tangent"]["category"], "unfinished_debate")

        # Get strategy artifacts
        art_resp = self.client.get("/api/artifacts")
        self.assertEqual(art_resp.status_code, 200)
        artifacts = art_resp.json()
        self.assertIsInstance(artifacts, dict)
        self.assertGreater(len(artifacts), 0)

    def test_hearth_log_endpoint(self):
        resp = self.client.post("/api/hearth/log", json={
            "user_id": "badri",
            "minutes": 45
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["hearth_session"]["is_active"])
        self.assertGreaterEqual(data["hearth_session"]["duration_minutes"], 45)

    def test_booth_challenge_endpoint(self):
        resp = self.client.post("/api/booth/challenge", json={
            "author": "badri",
            "target_user": "dave",
            "topic": "Zig vs Rust for Embedded",
            "argument": "Comptime is cleaner than proc-macros for register mapping.",
            "citation_link": "https://ziglang.org"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["challenge"]["author"], "badri")
        self.assertEqual(data["challenge"]["target_user"], "dave")
        self.assertEqual(data["challenge"]["status"], "staged")

if __name__ == "__main__":
    unittest.main()
