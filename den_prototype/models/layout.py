"""Domain models for Custom Room Layouts, Spatial Objects, Lighting, and Color Palettes."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import time
import uuid

class RoomPalette(BaseModel):
    background_color: str = "#0c0805"
    fog_color: str = "#0c0805"
    floor_color: str = "#241309"
    floor_type: str = "wood_plank"  # 'wood_plank', 'parquet', 'concrete', 'carpet', 'tatami', 'slate_tile'
    wall_color: str = "#180d07"
    wall_type: str = "wood_panels"  # 'wood_panels', 'exposed_brick', 'concrete', 'bookshelf_wall', 'drywall'
    accent_color: str = "#fbbf24"

class RoomLight(BaseModel):
    type: str = "point"  # 'point', 'spot', 'ambient', 'pendant'
    color: str = "#ffaa44"
    intensity: float = 2.0
    distance: float = 12.0
    position: List[float] = Field(default_factory=lambda: [0.0, 3.5, 0.0])

class RoomProp(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str  # 'amp_stack', 'plants', 'neon_sign', 'record_player', 'arcade_cabinet', 'hearth', 'bookshelf', 'coffee_table', 'rug', 'poster'
    position: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: List[float] = Field(default_factory=lambda: [1.0, 1.0, 1.0])
    color: Optional[str] = None
    label: Optional[str] = None
    interactive_type: Optional[str] = None  # 'jukebox', 'journal', 'dice', 'hearth', 'dog'

class SeatLayout(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: Optional[str] = None
    seat_type: str = "armchair"  # 'armchair', 'couch', 'stool', 'floor_cushion', 'wicker_chair'
    position: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation_y: float = 0.0
    color: Optional[str] = None

class CustomRoomLayout(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    vibe_tagline: str
    description: str
    source_mode: str = "preset"  # 'prompt', 'image', 'preset'
    source_input: str = ""        # The original prompt or image path/filename
    palette: RoomPalette = Field(default_factory=RoomPalette)
    lighting: List[RoomLight] = Field(default_factory=list)
    props: List[RoomProp] = Field(default_factory=list)
    seats: List[SeatLayout] = Field(default_factory=list)
    soundscape: str = "cedar_fire"  # 'rain', 'cedar_fire', 'vinyl_hiss', 'tape_hum', 'night_crickets'
    created_at: float = Field(default_factory=time.time)
    thumbnail_url: Optional[str] = None
    extracted_palette: List[str] = Field(default_factory=list)
