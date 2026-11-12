"""Root state model for The Den prototype."""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

from .user import UserProfile
from .exhaust import SpotifyExhaust, LetterboxdExhaust, GitHubExhaust
from .social import LoreItem, MicroPoll, DogParkFamiliar, DogParkEvent, SlowGameState, ThemeConfig, HearthFocusSession
from .tangents import CornerBoothState
from .layout import CustomRoomLayout

class RoomResidue(BaseModel):
    friend_id: str
    friend_name: str
    departed_at_label: str  # e.g. "2 hours ago"
    last_action: str         # e.g. "Finished a glass of scotch and left note"
    left_note: str           # e.g. "Benchmarking WAL mode tomorrow"
    drink_status: str = "melted_ice"  # 'melted_ice', 'empty_mug', 'cold_tea'

class DenState(BaseModel):
    den_id: str
    name: str
    den_type: str = "buddies"  # 'personal', 'buddies', 'family'
    available_dens: List[Dict[str, str]] = Field(default_factory=lambda: [
        {"id": "buddies", "name": "College Buddies Den 🍻", "type": "buddies"},
        {"id": "personal", "name": "Badri's Sovereign Hearth 🛋️", "type": "personal"},
        {"id": "family", "name": "Family Sanctum 🏡", "type": "family"}
    ])
    host_id: str
    dunbar_cap: int = 15  # Strict Dunbar limit
    active_friends_count: int
    users: List[UserProfile]
    spotify_streams: Dict[str, SpotifyExhaust]
    letterboxd_streams: Dict[str, LetterboxdExhaust]
    github_streams: Dict[str, GitHubExhaust]
    inside_jokes: List[LoreItem]
    active_poll: Optional[MicroPoll] = None
    dog_park_familiars: List[DogParkFamiliar] = Field(default_factory=list)
    dog_park_events: List[DogParkEvent] = Field(default_factory=list)
    slow_game: Optional[SlowGameState] = None
    current_theme: ThemeConfig
    recent_dispatches: List[Dict[str, Any]] = Field(default_factory=list)
    active_embers: List[Dict[str, str]] = Field(default_factory=list)
    corner_booth: Optional[CornerBoothState] = None
    room_residues: List[RoomResidue] = Field(default_factory=list)
    hearth_session: Optional[HearthFocusSession] = None
    current_custom_layout: Optional[CustomRoomLayout] = None
    available_custom_layouts: List[CustomRoomLayout] = Field(default_factory=list)
