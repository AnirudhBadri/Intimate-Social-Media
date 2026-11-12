"""Unit tests for DenEngine core state machine."""

import asyncio
import unittest
from den_prototype.engine import DenEngine
from den_prototype.models.user import UserProfile, AvatarConfig, FeedConfig

class TestDenEngine(unittest.TestCase):
    """Verifies central DenEngine business logic, state safety, and boundary guards."""

    def setUp(self):
        self.engine = DenEngine("unit-test-den")

    def test_initial_state_defaults(self):
        state = self.engine.get_state()
        self.assertEqual(state.den_id, "unit-test-den")
        self.assertEqual(state.den_type, "buddies")
        self.assertEqual(len(state.users), 4)
        self.assertEqual(state.dunbar_cap, 15)
        self.assertIsNotNone(state.corner_booth)
        self.assertGreater(len(state.corner_booth.active_tangents), 0)

    def test_dunbar_limit_enforcement(self):
        # Initial users count is 4
        self.assertEqual(len(self.engine.users), 4)

        # Add 11 more to hit 15 exactly
        for i in range(4, 15):
            u = UserProfile(
                id=f"friend_{i}",
                name=f"Friend {i}",
                handle=f"@friend_{i}",
                avatar="https://example.com/avatar.jpg",
                status_text="Testing",
                location="Remote",
                timezone="UTC"
            )
            res = self.engine.add_friend(u)
            self.assertTrue(res["success"])

        self.assertEqual(len(self.engine.users), 15)

        # Attempt to add 16th member (should fail)
        intruder = UserProfile(
            id="intruder",
            name="Intruder",
            handle="@intruder",
            avatar="https://example.com/avatar.jpg",
            status_text="Breaching",
            location="Nowhere",
            timezone="UTC"
        )
        fail_res = self.engine.add_friend(intruder)
        self.assertFalse(fail_res["success"])
        self.assertIn("Dunbar Limit Reached", fail_res["error"])

        # Updating an existing user should succeed even when at cap
        existing = self.engine.users["friend_14"]
        existing.status_text = "Updated status"
        update_res = self.engine.add_friend(existing)
        self.assertTrue(update_res["success"])

    def test_multi_den_switching(self):
        self.engine.switch_den("personal")
        self.assertEqual(self.engine.den_type, "personal")
        self.assertIn("Sovereign Hearth", self.engine.get_state().name)

        self.engine.switch_den("family")
        self.assertEqual(self.engine.den_type, "family")
        self.assertIn("Family Sanctum", self.engine.get_state().name)

        # Invalid den_id should not change type
        self.engine.switch_den("invalid_den_slug")
        self.assertEqual(self.engine.den_type, "family")

    def test_ember_protocol(self):
        res = self.engine.send_ember("badri", "dave")
        self.assertTrue(res["success"])
        self.assertEqual(res["ember"]["from"], "Badri")
        self.assertEqual(res["ember"]["to"], "Dave")
        self.assertIn("Zero-Debt Presence", res["ember"]["message"])
        self.assertLessEqual(len(self.engine.active_embers), 5)

    def test_poll_voting(self):
        # Valid option vote
        success = self.engine.vote_poll("opt1", "dave")
        self.assertTrue(success)
        self.assertIn("dave", self.engine.active_poll.options[0].votes)

        # Changing vote to opt2
        self.engine.vote_poll("opt2", "dave")
        self.assertNotIn("dave", self.engine.active_poll.options[0].votes)
        self.assertIn("dave", self.engine.active_poll.options[1].votes)

        # Invalid option vote returns False
        invalid_res = self.engine.vote_poll("non_existent_opt", "dave")
        self.assertFalse(invalid_res)

    def test_user_avatar_and_feed_update(self):
        # Valid avatar update
        av_cfg = AvatarConfig(outfit_color="#065f46", drink="scotch")
        av_res = self.engine.update_user_avatar("badri", av_cfg)
        self.assertTrue(av_res["success"])
        self.assertEqual(self.engine.users["badri"].avatar_config.drink, "scotch")

        # Non-existent user avatar update
        av_fail = self.engine.update_user_avatar("unknown_user", av_cfg)
        self.assertFalse(av_fail["success"])

        # Feed update
        feed_cfg = FeedConfig(
            user_id="badri",
            spotify_track="Paranoid Android",
            spotify_artist="Radiohead",
            custom_status="Deep in flow"
        )
        feed_res = self.engine.update_user_feed(feed_cfg)
        self.assertTrue(feed_res["success"])
        self.assertEqual(self.engine.spotify_streams["badri"].track_name, "Paranoid Android")
        self.assertEqual(self.engine.users["badri"].status_text, "Deep in flow")

    def test_import_thread_and_extract_tangents(self):
        raw = """
Dave: We should benchmark SQLite with WAL mode.
Badri: Postgres connection pooling is much better for scale.
        """
        res = self.engine.import_thread_and_extract_tangents("badri", "dave", "WhatsApp", raw)
        self.assertTrue(res["success"])
        self.assertIn("tangent", res)
        self.assertEqual(self.engine.corner_booth.active_tangents[0].title, res["tangent"]["title"])

    def test_subscriber_lifecycle(self):
        queue = asyncio.Queue()
        self.engine.subscribe(queue)
        self.assertIn(queue, self.engine.subscribers)

        self.engine._notify_subscribers()
        self.assertEqual(queue.qsize(), 1)
        snapshot = queue.get_nowait()
        self.assertEqual(snapshot["den_id"], "unit-test-den")

        self.engine.unsubscribe(queue)
        self.assertNotIn(queue, self.engine.subscribers)

    def test_single_player_hearth_session(self):
        state = self.engine.get_state()
        self.assertIsNotNone(state.hearth_session)
        initial_logs = state.hearth_session.logs_added

        # Feed log to hearth
        session = self.engine.feed_hearth_log("badri", minutes=45)
        self.assertTrue(session.is_active)
        self.assertEqual(session.logs_added, initial_logs + 1)
        self.assertEqual(session.duration_minutes, 90)

    def test_single_player_room_residues(self):
        state = self.engine.get_state()
        self.assertGreaterEqual(len(state.room_residues), 2)
        priya_res = next((r for r in state.room_residues if r.friend_id == "priya"), None)
        self.assertIsNotNone(priya_res)
        self.assertEqual(priya_res.drink_status, "cold_tea")
        self.assertIn("modal.com", priya_res.left_note)

    def test_single_player_stage_sparring_challenge(self):
        challenge = self.engine.stage_sparring_challenge(
            author="badri",
            target_user="dave",
            topic="WASM in the Browser vs Native Web Workers",
            raw_argument="WASM runtime initialization cost dominates small operations.",
            citation_link="https://webassembly.org"
        )
        self.assertEqual(challenge.author, "badri")
        self.assertEqual(challenge.target_user, "dave")
        self.assertIn(challenge, self.engine.corner_booth.active_challenges)

    def test_engine_custom_layout_methods(self):
        # 1. List layouts (should include presets)
        layouts = self.engine.list_custom_layouts()
        self.assertGreaterEqual(len(layouts), 3)

        # 2. Prompt synthesis
        layout = self.engine.generate_layout_from_prompt("Rainy greenhouse botanical sanctuary")
        self.assertIsNotNone(layout)
        self.assertEqual(self.engine.current_custom_layout.id, layout.id)
        self.assertEqual(self.engine.get_state().current_custom_layout.id, layout.id)

        # 3. Setting specific layout
        switched = self.engine.set_custom_layout("preset-grunge-garage")
        self.assertIsNotNone(switched)
        self.assertEqual(self.engine.current_custom_layout.id, "preset-grunge-garage")

        # 4. Image synthesis
        img_layout = self.engine.generate_layout_from_image(b"fake-bytes-12345", "test_room.jpg", "A basement nook")
        self.assertIsNotNone(img_layout)
        self.assertEqual(self.engine.current_custom_layout.id, img_layout.id)

if __name__ == "__main__":
    unittest.main()

