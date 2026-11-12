"""User and avatar profile models for The Den."""

from typing import Dict, Optional
from pydantic import BaseModel, Field

class AvatarConfig(BaseModel):
    outfit_color: str = "#38bdf8"
    skin_tone: str = "#fbcfe8"
    hair_color: str = "#1c1917"
    hair_style: str = "beanie"  # beanie, cap, curly, sleek, messy, bald
    drink: str = "coffee"       # coffee, beer, cocktail, tea, boba, scotch
    accessory: str = "none"     # none, glasses, headphones, scarf, camera

class FeedConfig(BaseModel):
    user_id: str
    spotify_track: Optional[str] = None
    spotify_artist: Optional[str] = None
    spotify_playing: bool = True
    letterboxd_title: Optional[str] = None
    letterboxd_rating: float = 4.0
    letterboxd_review: Optional[str] = None
    github_repo: Optional[str] = None
    github_commit: Optional[str] = None
    custom_status: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    name: str
    handle: str
    avatar: str
    status_text: str
    location: str
    timezone: str
    is_online: bool = True
    vibe_card: Dict[str, str] = Field(default_factory=dict)
    avatar_config: AvatarConfig = Field(default_factory=AvatarConfig)
