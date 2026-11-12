"""Unit tests for ThemeService (Generative UI Styling)."""

import unittest
from den_prototype.services.theme_service import ThemeService

class TestThemeService(unittest.TestCase):
    """Verifies generative UI aesthetic presets and natural language fallback generation."""

    def setUp(self):
        self.service = ThemeService()

    def test_default_theme(self):
        theme = self.service.current_theme
        self.assertEqual(theme.theme_name, "Velvet & Vintage Oak")
        self.assertEqual(theme.accent_color, "#fbbf24")

    def test_tokyo_cyberpunk_preset(self):
        theme = self.service.generate_theme("rainy tokyo cyberpunk neon bar")
        self.assertEqual(theme.theme_name, "Neo-Tokyo Rainy Izakaya")
        self.assertEqual(theme.accent_color, "#f43f5e")

    def test_warm_paper_retro_preset(self):
        theme = self.service.generate_theme("retro warm coffee library with paper books")
        self.assertEqual(theme.theme_name, "Analog Warm Paper & Espresso")
        self.assertEqual(theme.accent_color, "#f59e0b")

    def test_nordic_slate_minimal_preset(self):
        theme = self.service.generate_theme("minimal scandinavian slate and pine")
        self.assertEqual(theme.theme_name, "Nordic Slate & Pine")
        self.assertEqual(theme.accent_color, "#38bdf8")

    def test_custom_generative_prompt(self):
        theme = self.service.generate_theme("deep ocean bioluminescent jellyfish")
        self.assertIn("Custom:", theme.theme_name)
        self.assertEqual(theme.accent_color, "#a855f7")

if __name__ == "__main__":
    unittest.main()
