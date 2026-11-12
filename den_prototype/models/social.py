"""Social, lore, poll, game, and theme models for The Den."""

from typing import List, Optional
from pydantic import BaseModel, Field
import time
import uuid

class InsideJoke(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    author: str
    quote: str
    context: str
    created_at: float = Field(default_factory=time.time)

class LoreItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    author: str
    quote: str
    context: str
    consecrated_by: List[str] = Field(default_factory=list)
    is_consecrated: bool = False
    created_at: float = Field(default_factory=time.time)

class MicroPollOption(BaseModel):
    id: str
    text: str
    votes: List[str] = Field(default_factory=list)

class MicroPoll(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    context: str
    options: List[MicroPollOption]
    created_by: str = "Den AI Wingman"
    is_active: bool = True

class BanterTurn(BaseModel):
    agent_name: str
    speaker_user: str
    message: str
    turn_number: int

class BanterSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    trigger_reason: str
    turns: List[BanterTurn]
    human_callout: str
    timestamp: float = Field(default_factory=time.time)

class ThemeConfig(BaseModel):
    theme_name: str
    bg_gradient: str
    surface_color: str
    border_color: str
    accent_color: str
    font_family: str
    vibe_description: str

class DogParkFamiliar(BaseModel):
    id: str
    owner_id: str
    owner_name: str
    name: str
    species: str = "Shiba Inu"
    avatar: str
    current_action: str
    toy: Optional[str] = None

class DogParkEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    familiar_names: List[str]
    description: str
    timestamp: float = Field(default_factory=time.time)

class SlowGameState(BaseModel):
    game_title: str = "Slow Monopoly (Found Family Edition)"
    turn_number: int = 14
    active_player_name: str = "Dave"
    board_state_summary: str = "Dave landed on Badri's 'Late Night Dosa Cafe' (Rent: $25). Priya holds 'Hackathon Basement'."
    last_move_description: str = "Dave rolled 8, landed on 'Late Night Dosa Cafe', paid Badri $25."
    next_turn_due: str = "In 18 hours (Async Grace Mode)"

class HearthFocusSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str = "badri"
    duration_minutes: int = 45
    logs_added: int = 1
    started_at: float = Field(default_factory=time.time)
    flame_intensity: float = 1.0  # 1.0 down to 0.0 as it burns down
    is_active: bool = True
