"""Unit tests for Pydantic data models."""

import unittest
from den_prototype.models import (
    AvatarConfig,
    FeedConfig,
    UserProfile,
    SpotifyExhaust,
    LetterboxdExhaust,
    GitHubExhaust,
    LoreItem,
    MicroPoll,
    MicroPollOption,
    SlowGameState,
    ThemeConfig,
    TangentCard,
    ConversationImport,
    CornerBoothState,
    DenState,
)

class TestModels(unittest.TestCase):
    """Verifies schema validation, default factories, and serialization."""

    def test_avatar_config_defaults(self):
        cfg = AvatarConfig()
        self.assertEqual(cfg.outfit_color, "#38bdf8")
        self.assertEqual(cfg.drink, "coffee")
        self.assertEqual(cfg.accessory, "none")
        dump = cfg.model_dump()
        self.assertIn("hair_style", dump)

    def test_user_profile_customization(self):
        user = UserProfile(
            id="test_user",
            name="Test User",
            handle="@test_user",
            avatar="https://example.com/avatar.jpg",
            status_text="Testing status",
            location="Berlin",
            timezone="CET",
            is_online=True,
            avatar_config=AvatarConfig(outfit_color="#10b981", drink="scotch")
        )
        self.assertEqual(user.avatar_config.drink, "scotch")
        self.assertEqual(user.avatar_config.outfit_color, "#10b981")
        self.assertTrue(user.is_online)

    def test_ambient_exhaust_models(self):
        sp = SpotifyExhaust(
            is_playing=True,
            track_name="Karma Police",
            artist="Radiohead",
            album="OK Computer",
            cover_url="https://example.com/cover.jpg"
        )
        self.assertTrue(sp.is_playing)
        self.assertEqual(sp.track_name, "Karma Police")

        lb = LetterboxdExhaust(
            title="Dune 2",
            year=2024,
            rating=4.5,
            poster_url="https://example.com/poster.jpg",
            review_snippet="Cinema at its finest",
            watched_at="Yesterday"
        )
        self.assertEqual(lb.rating, 4.5)

        gh = GitHubExhaust(
            repo="org/repo",
            commit_msg="feat: modular refactor",
            branch="main",
            timestamp="Just now"
        )
        self.assertEqual(gh.branch, "main")

    def test_social_and_lore_models(self):
        lore = LoreItem(
            author="Badri",
            quote="It works on my machine",
            context="Deployment Friday",
            consecrated_by=["Badri"]
        )
        self.assertFalse(lore.is_consecrated)
        self.assertEqual(len(lore.consecrated_by), 1)

        poll = MicroPoll(
            title="Dinner plans?",
            context="Hungry after hackathon",
            options=[
                MicroPollOption(id="o1", text="Ramen", votes=["badri"]),
                MicroPollOption(id="o2", text="Pizza", votes=[])
            ]
        )
        self.assertEqual(len(poll.options), 2)
        self.assertEqual(poll.options[0].votes, ["badri"])

    def test_tangent_and_corner_booth_models(self):
        card = TangentCard(
            title="Postgres vs SQLite",
            category="unfinished_debate",
            summary="Discussion on write contention.",
            starter_prompt="Hey, let's talk about SQLite."
        )
        self.assertEqual(card.category, "unfinished_debate")
        self.assertTrue(card.is_active)

        imp = ConversationImport(
            partner_id="dave",
            partner_name="Dave",
            raw_snippet="Snippet text",
            extracted_tangents=[card]
        )
        self.assertEqual(imp.source, "WhatsApp")
        self.assertEqual(len(imp.extracted_tangents), 1)

        booth = CornerBoothState(
            participants=["badri", "dave"],
            active_tangents=[card],
            history_imports=[imp]
        )
        self.assertEqual(booth.booth_id, "corner-booth-whisper")
        self.assertEqual(len(booth.active_tangents), 1)

    def test_den_state_structure(self):
        theme = ThemeConfig(
            theme_name="Vintage",
            bg_gradient="linear-gradient(#000, #111)",
            surface_color="#222",
            border_color="#333",
            accent_color="#fbbf24",
            font_family="serif",
            vibe_description="Cozy vintage"
        )
        state = DenState(
            den_id="test-den",
            name="Test Den",
            den_type="buddies",
            host_id="badri",
            dunbar_cap=15,
            active_friends_count=1,
            users=[],
            spotify_streams={},
            letterboxd_streams={},
            github_streams={},
            inside_jokes=[],
            current_theme=theme
        )
        self.assertEqual(state.dunbar_cap, 15)
        self.assertEqual(state.name, "Test Den")
        dump = state.model_dump()
        self.assertIn("available_dens", dump)
        self.assertEqual(len(dump["available_dens"]), 3)

if __name__ == "__main__":
    unittest.main()
