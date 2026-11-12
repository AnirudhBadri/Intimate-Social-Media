"""Ambient exhaust models (Spotify, Letterboxd, GitHub) for The Den."""

from pydantic import BaseModel

class SpotifyExhaust(BaseModel):
    is_playing: bool = True
    track_name: str
    artist: str
    album: str
    cover_url: str
    duration_ms: int = 210000
    progress_ms: int = 85000
    external_url: str = "#"

class LetterboxdExhaust(BaseModel):
    title: str
    year: int
    rating: float  # e.g. 4.5 out of 5
    poster_url: str
    review_snippet: str
    watched_at: str

class GitHubExhaust(BaseModel):
    repo: str
    commit_msg: str
    branch: str = "main"
    timestamp: str
