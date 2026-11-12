"""Shared dependencies and singleton engine for The Den FastAPI application."""

from .engine import DenEngine

# Application singleton instance
engine = DenEngine()

def get_engine() -> DenEngine:
    """Dependency provider returning the active DenEngine instance."""
    return engine
