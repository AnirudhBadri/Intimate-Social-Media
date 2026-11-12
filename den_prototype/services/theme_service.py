"""Theme service for Generative UI aesthetics."""

from typing import Optional
from ..models.social import ThemeConfig

class ThemeService:
    """Generates dynamic ambient styling palettes based on natural language vibe prompts."""

    DEFAULT_THEME = ThemeConfig(
        theme_name="Velvet & Vintage Oak",
        bg_gradient="linear-gradient(135deg, #0c0805 0%, #170d07 50%, #1f1209 100%)",
        surface_color="rgba(24, 15, 8, 0.85)",
        border_color="rgba(217, 119, 6, 0.35)",
        accent_color="#fbbf24",
        font_family="'Inter', sans-serif",
        vibe_description="Handcrafted speakeasy aesthetic with warm amber Edison pendants and oak paneling."
    )

    def __init__(self, initial_theme: Optional[ThemeConfig] = None):
        self.current_theme: ThemeConfig = initial_theme or self.DEFAULT_THEME

    def generate_theme(self, prompt: str) -> ThemeConfig:
        """Applies generative UI styling based on a natural language vibe prompt."""
        p_lower = (prompt or "").lower()

        if "tokyo" in p_lower or "cyber" in p_lower or "rain" in p_lower:
            theme = ThemeConfig(
                theme_name="Neo-Tokyo Rainy Izakaya",
                bg_gradient="linear-gradient(135deg, #05050d 0%, #0d111a 50%, #17091d 100%)",
                surface_color="rgba(18, 22, 38, 0.8)",
                border_color="rgba(244, 63, 94, 0.35)",
                accent_color="#f43f5e",
                font_family="'JetBrains Mono', 'Fira Code', monospace",
                vibe_description="Rain-soaked neon reflections, lo-fi beats, steam rising from ramen counters."
            )
        elif "retro" in p_lower or "paper" in p_lower or "coffee" in p_lower or "warm" in p_lower:
            theme = ThemeConfig(
                theme_name="Analog Warm Paper & Espresso",
                bg_gradient="linear-gradient(135deg, #1f1b18 0%, #2a241f 50%, #1a1614 100%)",
                surface_color="rgba(42, 36, 31, 0.85)",
                border_color="rgba(217, 119, 6, 0.35)",
                accent_color="#f59e0b",
                font_family="'Georgia', serif",
                vibe_description="Worn paperback books, cedar wood desks, amber desk lamps, warm coffee steam."
            )
        elif "minimal" in p_lower or "nordic" in p_lower or "slate" in p_lower:
            theme = ThemeConfig(
                theme_name="Nordic Slate & Pine",
                bg_gradient="linear-gradient(135deg, #0b0f14 0%, #111822 50%, #0d151c 100%)",
                surface_color="rgba(23, 32, 45, 0.75)",
                border_color="rgba(56, 189, 248, 0.3)",
                accent_color="#38bdf8",
                font_family="'Inter', sans-serif",
                vibe_description="Clean Scandinavian aesthetic, cold slate stone, calm focus."
            )
        else:
            theme = ThemeConfig(
                theme_name=f"Custom: {prompt[:24]}",
                bg_gradient="linear-gradient(135deg, #0d0e15 0%, #181926 50%, #151020 100%)",
                surface_color="rgba(30, 32, 50, 0.8)",
                border_color="rgba(168, 85, 247, 0.35)",
                accent_color="#a855f7",
                font_family="'Inter', sans-serif",
                vibe_description=f"AI synthesized vibe: {prompt}"
            )

        self.current_theme = theme
        return theme
