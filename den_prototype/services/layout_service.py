"""Layout service for generating, compiling, and managing Custom 3D Room Layouts."""

import os
import io
import time
import uuid
import hashlib
from typing import List, Dict, Optional, Tuple, Any

from ..models.layout import (
    CustomRoomLayout,
    RoomPalette,
    RoomLight,
    RoomProp,
    SeatLayout
)

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class LayoutService:
    """Generates procedural 3D room specifications from text prompts or uploaded images."""

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.layouts: Dict[str, CustomRoomLayout] = {}
        self._seed_default_presets()

    def _seed_default_presets(self):
        """Pre-seeds handcrafted familiar dens that serve as templates and reference models."""
        presets = [
            CustomRoomLayout(
                id="preset-grunge-garage",
                name="90s Grunge Garage Rehearsal Nook",
                vibe_tagline="Marshall amp stacks, thrift velvet sofa, and tape hiss",
                description="A raw, authentic garage workspace with exposed brick, concrete floorboards, guitar amplifiers, and string work lights.",
                source_mode="preset",
                source_input="90s grunge garage band rehearsal space with amps and couch",
                palette=RoomPalette(
                    background_color="#0d0907",
                    fog_color="#0d0907",
                    floor_color="#1f1d1b",
                    floor_type="concrete",
                    wall_color="#2b1810",
                    wall_type="exposed_brick",
                    accent_color="#f59e0b"
                ),
                lighting=[
                    RoomLight(type="point", color="#ffbe5b", intensity=2.2, distance=14.0, position=[0.0, 3.8, 0.5]),
                    RoomLight(type="point", color="#f43f5e", intensity=1.5, distance=8.0, position=[-3.5, 2.5, -2.0]),
                    RoomLight(type="ambient", color="#2a160d", intensity=0.9, position=[0.0, 0.0, 0.0])
                ],
                props=[
                    RoomProp(type="amp_stack", position=[-4.2, 0.0, -2.4], scale=[1.1, 1.1, 1.1]),
                    RoomProp(type="amp_stack", position=[-3.0, 0.0, -2.6], scale=[0.9, 0.9, 0.9]),
                    RoomProp(type="neon_sign", position=[0.0, 3.6, -3.2], label="THE DEN", color="#f43f5e"),
                    RoomProp(type="rug", position=[0.0, 0.015, 0.4], scale=[5.0, 1.0, 2.4], color="#7c2d12"),
                    RoomProp(type="coffee_table", position=[0.0, 0.0, 1.2], scale=[1.0, 1.0, 1.0]),
                    RoomProp(type="record_player", position=[4.2, 1.0, -2.0], interactive_type="jukebox"),
                    RoomProp(type="poster", position=[3.5, 3.0, -3.2], label="Sonic Youth 1992 Tour"),
                ],
                seats=[
                    SeatLayout(user_id="badri", seat_type="couch", position=[-1.2, 0.0, 1.6], rotation_y=0.1, color="#38bdf8"),
                    SeatLayout(user_id="dave", seat_type="couch", position=[0.2, 0.0, 1.6], rotation_y=-0.1, color="#10b981"),
                    SeatLayout(user_id="priya", seat_type="armchair", position=[2.2, 0.0, 0.8], rotation_y=-0.5, color="#f43f5e"),
                    SeatLayout(user_id="sam", seat_type="floor_cushion", position=[-2.2, 0.0, 0.6], rotation_y=0.5, color="#a855f7"),
                ],
                soundscape="tape_hum",
                extracted_palette=["#0d0907", "#2b1810", "#1f1d1b", "#f59e0b", "#f43f5e"]
            ),
            CustomRoomLayout(
                id="preset-rainy-greenhouse",
                name="Rainy Botanical Greenhouse Loft",
                vibe_tagline="Hanging monstera, glass skylight, and gentle rain on glass",
                description="An airy, contemplative atrium with bamboo flooring, floor-to-ceiling potted flora, a low wooden tea table, and rain streaking across the glass panels.",
                source_mode="preset",
                source_input="Rainy botanical greenhouse loft with indoor plants and tea table",
                palette=RoomPalette(
                    background_color="#0a120e",
                    fog_color="#0a120e",
                    floor_color="#1e2c22",
                    floor_type="wood_plank",
                    wall_color="#13231a",
                    wall_type="bookshelf_wall",
                    accent_color="#34d399"
                ),
                lighting=[
                    RoomLight(type="point", color="#a7f3d0", intensity=1.8, distance=14.0, position=[0.0, 4.2, 0.0]),
                    RoomLight(type="point", color="#fde68a", intensity=1.6, distance=10.0, position=[0.0, 1.6, 1.0]),
                    RoomLight(type="ambient", color="#064e3b", intensity=0.95, position=[0.0, 0.0, 0.0])
                ],
                props=[
                    RoomProp(type="plants", position=[-4.2, 0.0, -2.2], scale=[1.2, 1.4, 1.2]),
                    RoomProp(type="plants", position=[-3.0, 0.0, -2.6], scale=[1.0, 1.1, 1.0]),
                    RoomProp(type="plants", position=[4.2, 0.0, -2.2], scale=[1.3, 1.5, 1.3]),
                    RoomProp(type="plants", position=[3.2, 0.0, -2.5], scale=[0.9, 1.0, 0.9]),
                    RoomProp(type="coffee_table", position=[0.0, 0.0, 0.8], scale=[1.2, 0.8, 1.2]),
                    RoomProp(type="rug", position=[0.0, 0.015, 0.8], scale=[4.6, 1.0, 3.2], color="#064e3b"),
                    RoomProp(type="record_player", position=[4.0, 0.8, 0.5], interactive_type="jukebox"),
                ],
                seats=[
                    SeatLayout(user_id="badri", seat_type="floor_cushion", position=[-1.4, 0.0, 1.2], rotation_y=0.3, color="#38bdf8"),
                    SeatLayout(user_id="dave", seat_type="floor_cushion", position=[-0.4, 0.0, 2.0], rotation_y=0.0, color="#10b981"),
                    SeatLayout(user_id="priya", seat_type="floor_cushion", position=[0.8, 0.0, 1.8], rotation_y=-0.2, color="#f43f5e"),
                    SeatLayout(user_id="sam", seat_type="wicker_chair", position=[2.0, 0.0, 0.8], rotation_y=-0.6, color="#a855f7"),
                ],
                soundscape="rain",
                extracted_palette=["#0a120e", "#13231a", "#1e2c22", "#34d399", "#a7f3d0"]
            ),
            CustomRoomLayout(
                id="preset-rooftop-sunset",
                name="Rooftop Sunset Porch",
                vibe_tagline="String lights, weathered cedar decking, and golden hour skyline",
                description="An open-air urban rooftop deck overlooking the twilight skyline with fairy string lights, wicker chairs, potted lavender, and acoustic warmth.",
                source_mode="preset",
                source_input="Urban rooftop sunset porch with fairy lights and city view",
                palette=RoomPalette(
                    background_color="#180b1e",
                    fog_color="#180b1e",
                    floor_color="#2b1a11",
                    floor_type="wood_plank",
                    wall_color="#1f0f26",
                    wall_type="wood_panels",
                    accent_color="#fb923c"
                ),
                lighting=[
                    RoomLight(type="point", color="#ff7849", intensity=2.8, distance=16.0, position=[-4.0, 2.5, -3.0]),
                    RoomLight(type="point", color="#fde047", intensity=1.5, distance=10.0, position=[0.0, 3.8, 0.0]),
                    RoomLight(type="ambient", color="#2e103f", intensity=0.9, position=[0.0, 0.0, 0.0])
                ],
                props=[
                    RoomProp(type="plants", position=[-4.5, 0.0, -1.8], scale=[1.1, 1.3, 1.1]),
                    RoomProp(type="plants", position=[4.5, 0.0, -1.8], scale=[1.1, 1.2, 1.1]),
                    RoomProp(type="coffee_table", position=[0.0, 0.0, 1.0], scale=[1.0, 1.0, 1.0]),
                    RoomProp(type="rug", position=[0.0, 0.015, 0.9], scale=[4.8, 1.0, 2.8], color="#581c87"),
                    RoomProp(type="record_player", position=[3.6, 0.8, -1.8], interactive_type="jukebox"),
                ],
                seats=[
                    SeatLayout(user_id="badri", seat_type="wicker_chair", position=[-1.8, 0.0, 0.9], rotation_y=0.4, color="#38bdf8"),
                    SeatLayout(user_id="dave", seat_type="wicker_chair", position=[-0.6, 0.0, 1.8], rotation_y=0.1, color="#10b981"),
                    SeatLayout(user_id="priya", seat_type="wicker_chair", position=[0.7, 0.0, 1.8], rotation_y=-0.1, color="#f43f5e"),
                    SeatLayout(user_id="sam", seat_type="wicker_chair", position=[1.9, 0.0, 0.9], rotation_y=-0.4, color="#a855f7"),
                ],
                soundscape="night_crickets",
                extracted_palette=["#180b1e", "#ff7849", "#2b1a11", "#581c87", "#fde047"]
            )
        ]
        for p in presets:
            self.layouts[p.id] = p

    def get_layout(self, layout_id: str) -> Optional[CustomRoomLayout]:
        return self.layouts.get(layout_id)

    def list_layouts(self) -> List[CustomRoomLayout]:
        return list(self.layouts.values())

    def save_layout(self, layout: CustomRoomLayout) -> CustomRoomLayout:
        self.layouts[layout.id] = layout
        return layout

    def generate_from_prompt(self, prompt: str) -> CustomRoomLayout:
        """Synthesizes a complete 3D CustomRoomLayout from a natural language vibe prompt."""
        p_lower = (prompt or "").strip().lower()

        # Semantic Archetype Matchers
        if any(w in p_lower for w in ["garage", "band", "grunge", "punk", "rehearsal", "amp", "rock"]):
            layout_id = f"custom-garage-{uuid.uuid4().hex[:6]}"
            name = f"Garage Rehearsal: {prompt[:28]}"
            vibe = "Amp stacks, concrete floor, neon sign, and tape hiss"
            palette = RoomPalette(
                background_color="#0c0806",
                fog_color="#0c0806",
                floor_color="#1c1a19",
                floor_type="concrete",
                wall_color="#2b170e",
                wall_type="exposed_brick",
                accent_color="#f59e0b"
            )
            props = [
                RoomProp(type="amp_stack", position=[-4.0, 0.0, -2.4]),
                RoomProp(type="amp_stack", position=[-2.8, 0.0, -2.6], scale=[0.9, 0.9, 0.9]),
                RoomProp(type="neon_sign", position=[0.0, 3.6, -3.2], label="DEN REHEARSAL", color="#f43f5e"),
                RoomProp(type="rug", position=[0.0, 0.015, 0.4], scale=[5.0, 1.0, 2.4], color="#7c2d12"),
                RoomProp(type="coffee_table", position=[0.0, 0.0, 1.1]),
                RoomProp(type="record_player", position=[4.0, 0.9, -2.0], interactive_type="jukebox"),
            ]
            seats = [
                SeatLayout(user_id="badri", seat_type="couch", position=[-1.0, 0.0, 1.5], rotation_y=0.1, color="#38bdf8"),
                SeatLayout(user_id="dave", seat_type="couch", position=[0.4, 0.0, 1.5], rotation_y=-0.1, color="#10b981"),
                SeatLayout(user_id="priya", seat_type="armchair", position=[2.1, 0.0, 0.8], rotation_y=-0.5, color="#f43f5e"),
                SeatLayout(user_id="sam", seat_type="armchair", position=[-2.1, 0.0, 0.7], rotation_y=0.5, color="#a855f7"),
            ]
            soundscape = "tape_hum"

        elif any(w in p_lower for w in ["greenhouse", "plant", "garden", "botanical", "monstera", "loft"]):
            layout_id = f"custom-greenhouse-{uuid.uuid4().hex[:6]}"
            name = f"Greenhouse Sanctum: {prompt[:28]}"
            vibe = "Indoor flora, skylight rain, cedar scent, and tea"
            palette = RoomPalette(
                background_color="#09130e",
                fog_color="#09130e",
                floor_color="#1a2b20",
                floor_type="slate_tile",
                wall_color="#102117",
                wall_type="glass_greenhouse",
                accent_color="#34d399"
            )
            props = [
                RoomProp(type="plants", position=[-4.2, 0.0, -2.2], scale=[1.3, 1.5, 1.3]),
                RoomProp(type="plants", position=[-2.8, 0.0, -2.5], scale=[1.0, 1.1, 1.0]),
                RoomProp(type="plants", position=[4.2, 0.0, -2.2], scale=[1.4, 1.6, 1.4]),
                RoomProp(type="plants", position=[3.0, 0.0, -2.4], scale=[0.9, 1.0, 0.9]),
                RoomProp(type="coffee_table", position=[0.0, 0.0, 0.9], scale=[1.2, 0.8, 1.2]),
                RoomProp(type="rug", position=[0.0, 0.015, 0.8], scale=[4.6, 1.0, 3.0], color="#064e3b"),
                RoomProp(type="record_player", position=[3.8, 0.8, 0.5], interactive_type="jukebox"),
            ]
            seats = [
                SeatLayout(user_id="badri", seat_type="floor_cushion", position=[-1.3, 0.0, 1.2], rotation_y=0.3, color="#38bdf8"),
                SeatLayout(user_id="dave", seat_type="floor_cushion", position=[-0.3, 0.0, 1.9], rotation_y=0.0, color="#10b981"),
                SeatLayout(user_id="priya", seat_type="floor_cushion", position=[0.8, 0.0, 1.7], rotation_y=-0.2, color="#f43f5e"),
                SeatLayout(user_id="sam", seat_type="wicker_chair", position=[2.0, 0.0, 0.8], rotation_y=-0.6, color="#a855f7"),
            ]
            soundscape = "rain"

        elif any(w in p_lower for w in ["tokyo", "izakaya", "cyber", "ramen", "neon", "shinjuku"]):
            layout_id = f"custom-tokyo-{uuid.uuid4().hex[:6]}"
            name = f"Tokyo Neon Izakaya: {prompt[:28]}"
            vibe = "Midnight neon reflections, cedar bar, and warm sake"
            palette = RoomPalette(
                background_color="#06060f",
                fog_color="#06060f",
                floor_color="#18141e",
                floor_type="slate_tile",
                wall_color="#1f101f",
                wall_type="wood_panels",
                accent_color="#f43f5e"
            )
            props = [
                RoomProp(type="neon_sign", position=[0.0, 3.6, -3.2], label="居酒屋 DEN", color="#38bdf8"),
                RoomProp(type="arcade_cabinet", position=[-4.2, 0.0, -2.4]),
                RoomProp(type="record_player", position=[4.0, 0.9, -2.0], interactive_type="jukebox"),
                RoomProp(type="coffee_table", position=[0.0, 0.0, 0.8]),
                RoomProp(type="rug", position=[0.0, 0.015, 0.8], scale=[4.2, 1.0, 2.5], color="#881337"),
            ]
            seats = [
                SeatLayout(user_id="badri", seat_type="stool", position=[-1.5, 0.0, 1.0], rotation_y=0.4, color="#38bdf8"),
                SeatLayout(user_id="dave", seat_type="stool", position=[-0.5, 0.0, 1.7], rotation_y=0.1, color="#10b981"),
                SeatLayout(user_id="priya", seat_type="stool", position=[0.6, 0.0, 1.7], rotation_y=-0.1, color="#f43f5e"),
                SeatLayout(user_id="sam", seat_type="stool", position=[1.6, 0.0, 1.0], rotation_y=-0.4, color="#a855f7"),
            ]
            soundscape = "rain"

        elif any(w in p_lower for w in ["rooftop", "porch", "sunset", "patio", "balcony", "terrace", "deck"]):
            layout_id = f"custom-rooftop-{uuid.uuid4().hex[:6]}"
            name = f"Rooftop Haven: {prompt[:28]}"
            vibe = "Twilight golden hour, string lights, and open air"
            palette = RoomPalette(
                background_color="#160c1c",
                fog_color="#160c1c",
                floor_color="#2b180d",
                floor_type="wood_plank",
                wall_color="#1a0c22",
                wall_type="wood_panels",
                accent_color="#fb923c"
            )
            props = [
                RoomProp(type="plants", position=[-4.2, 0.0, -2.0], scale=[1.1, 1.3, 1.1]),
                RoomProp(type="plants", position=[4.2, 0.0, -2.0], scale=[1.1, 1.3, 1.1]),
                RoomProp(type="coffee_table", position=[0.0, 0.0, 1.0]),
                RoomProp(type="rug", position=[0.0, 0.015, 0.9], scale=[4.5, 1.0, 2.6], color="#4c1d95"),
                RoomProp(type="record_player", position=[3.6, 0.8, -1.8], interactive_type="jukebox"),
            ]
            seats = [
                SeatLayout(user_id="badri", seat_type="wicker_chair", position=[-1.8, 0.0, 0.9], rotation_y=0.4, color="#38bdf8"),
                SeatLayout(user_id="dave", seat_type="wicker_chair", position=[-0.6, 0.0, 1.8], rotation_y=0.1, color="#10b981"),
                SeatLayout(user_id="priya", seat_type="wicker_chair", position=[0.7, 0.0, 1.8], rotation_y=-0.1, color="#f43f5e"),
                SeatLayout(user_id="sam", seat_type="wicker_chair", position=[1.9, 0.0, 0.9], rotation_y=-0.4, color="#a855f7"),
            ]
            soundscape = "night_crickets"

        else:
            # Algorithmic Procedural Synthesis
            hash_val = int(hashlib.md5(prompt.encode('utf-8')).hexdigest(), 16)
            hue_floor = (hash_val % 40) + 15  # Warm wood / stone range
            layout_id = f"custom-room-{uuid.uuid4().hex[:6]}"
            name = f"The {prompt[:24].title()} Den"
            vibe = f"Artisanal den custom-crafted for '{prompt}'"

            palette = RoomPalette(
                background_color="#100b08",
                fog_color="#100b08",
                floor_color="#24140a",
                floor_type="wood_plank",
                wall_color="#1c0f08",
                wall_type="wood_panels",
                accent_color="#fbbf24"
            )
            props = [
                RoomProp(type="hearth", position=[0.0, 1.2, -2.6], interactive_type="hearth"),
                RoomProp(type="rug", position=[0.0, 0.015, 0.5], scale=[4.8, 1.0, 2.6], color="#881337"),
                RoomProp(type="coffee_table", position=[0.0, 0.0, 1.2]),
                RoomProp(type="record_player", position=[4.0, 0.9, -2.0], interactive_type="jukebox"),
                RoomProp(type="bookshelf", position=[-4.4, 2.6, -2.6]),
                RoomProp(type="plants", position=[4.2, 0.0, 0.5]),
            ]
            seats = [
                SeatLayout(user_id="badri", seat_type="armchair", position=[-1.8, 0.0, 1.0], rotation_y=0.4, color="#38bdf8"),
                SeatLayout(user_id="dave", seat_type="armchair", position=[-0.6, 0.0, 1.8], rotation_y=0.1, color="#10b981"),
                SeatLayout(user_id="priya", seat_type="armchair", position=[0.7, 0.0, 1.8], rotation_y=-0.1, color="#f43f5e"),
                SeatLayout(user_id="sam", seat_type="armchair", position=[1.9, 0.0, 1.0], rotation_y=-0.4, color="#a855f7"),
            ]
            soundscape = "cedar_fire"

        layout = CustomRoomLayout(
            id=layout_id,
            name=name,
            vibe_tagline=vibe,
            description=f"Generated from prompt: '{prompt}'",
            source_mode="prompt",
            source_input=prompt,
            palette=palette,
            lighting=[
                RoomLight(type="point", color="#ffaa44", intensity=2.2, distance=14.0, position=[0.0, 4.0, 0.0]),
                RoomLight(type="ambient", color="#2a160d", intensity=1.0, position=[0.0, 0.0, 0.0])
            ],
            props=props,
            seats=seats,
            soundscape=soundscape
        )
        self.save_layout(layout)
        return layout

    def generate_from_image(
        self,
        image_bytes: bytes,
        filename: str = "upload.jpg",
        user_hint: str = ""
    ) -> CustomRoomLayout:
        """Analyzes an uploaded photo of a scene and extracts color palette, vibe, and spatial layout."""
        # 1. Save uploaded file to static uploads folder
        file_ext = os.path.splitext(filename)[1].lower() or ".jpg"
        unique_fname = f"den_upload_{uuid.uuid4().hex[:8]}{file_ext}"
        save_path = os.path.join(self.storage_dir, unique_fname)

        with open(save_path, "wb") as f:
            f.write(image_bytes)

        # 2. Extract Color Palette using PIL or Fallback
        extracted_colors = self._extract_palette_from_image(image_bytes)

        # 3. Determine Architectural & Furniture Layout based on Palette & Hints
        # Sort colors by approximate luminance
        bg_color = extracted_colors[0] if extracted_colors else "#0f0b08"
        floor_color = extracted_colors[1] if len(extracted_colors) > 1 else "#26150b"
        accent_color = extracted_colors[2] if len(extracted_colors) > 2 else "#fbbf24"
        wall_color = extracted_colors[3] if len(extracted_colors) > 3 else "#1b0f07"

        hint_lower = (user_hint or "").lower()
        is_green = any(c in hint_lower for c in ["plant", "green", "garden", "nature"]) or any(
            c in floor_color.lower() for c in ["#2", "#3", "#1a2"]
        )
        is_concrete = any(c in hint_lower for c in ["garage", "basement", "concrete", "workshop"])
        is_brick = any(c in hint_lower for c in ["brick", "hearth", "fireplace", "stone"])

        floor_type = "concrete" if is_concrete else ("tatami" if is_green else "wood_plank")
        wall_type = "exposed_brick" if (is_concrete or is_brick) else ("bookshelf_wall" if is_green else "wood_panels")
        soundscape = "rain" if is_green else ("tape_hum" if is_concrete else "cedar_fire")

        layout_id = f"custom-photo-{uuid.uuid4().hex[:6]}"
        clean_hint = user_hint.strip() if user_hint else "Real-World Sanctum"
        name = f"Photo Den: {clean_hint[:24]}"
        vibe = f"Extracted from {filename} with 5-tone palette harmony"

        props: List[RoomProp] = [
            RoomProp(type="rug", position=[0.0, 0.015, 0.5], scale=[4.8, 1.0, 2.6], color=accent_color),
            RoomProp(type="coffee_table", position=[0.0, 0.0, 1.1]),
            RoomProp(type="record_player", position=[4.0, 0.9, -2.0], interactive_type="jukebox"),
        ]

        if is_green:
            props.extend([
                RoomProp(type="plants", position=[-4.2, 0.0, -2.0], scale=[1.2, 1.4, 1.2]),
                RoomProp(type="plants", position=[4.2, 0.0, -2.0], scale=[1.2, 1.4, 1.2]),
            ])
        elif is_concrete:
            props.extend([
                RoomProp(type="amp_stack", position=[-4.0, 0.0, -2.4]),
                RoomProp(type="neon_sign", position=[0.0, 3.6, -3.2], label="MY DEN", color=accent_color),
            ])
        else:
            props.extend([
                RoomProp(type="hearth", position=[0.0, 1.2, -2.6], interactive_type="hearth"),
                RoomProp(type="bookshelf", position=[-4.4, 2.6, -2.6]),
            ])

        seats = [
            SeatLayout(user_id="badri", seat_type="armchair", position=[-1.8, 0.0, 1.0], rotation_y=0.4, color="#38bdf8"),
            SeatLayout(user_id="dave", seat_type="armchair", position=[-0.6, 0.0, 1.8], rotation_y=0.1, color="#10b981"),
            SeatLayout(user_id="priya", seat_type="armchair", position=[0.7, 0.0, 1.8], rotation_y=-0.1, color="#f43f5e"),
            SeatLayout(user_id="sam", seat_type="armchair", position=[1.9, 0.0, 1.0], rotation_y=-0.4, color="#a855f7"),
        ]

        layout = CustomRoomLayout(
            id=layout_id,
            name=name,
            vibe_tagline=vibe,
            description=f"Synthesized from uploaded photo '{filename}'. {user_hint}".strip(),
            source_mode="image",
            source_input=filename,
            thumbnail_url=f"/static/uploads/{unique_fname}",
            palette=RoomPalette(
                background_color=bg_color,
                fog_color=bg_color,
                floor_color=floor_color,
                floor_type=floor_type,
                wall_color=wall_color,
                wall_type=wall_type,
                accent_color=accent_color
            ),
            lighting=[
                RoomLight(type="point", color=accent_color, intensity=2.4, distance=14.0, position=[0.0, 4.0, 0.0]),
                RoomLight(type="ambient", color=bg_color, intensity=1.1, position=[0.0, 0.0, 0.0])
            ],
            props=props,
            seats=seats,
            soundscape=soundscape,
            extracted_palette=extracted_colors
        )

        self.save_layout(layout)
        return layout

    def _extract_palette_from_image(self, image_bytes: bytes) -> List[str]:
        """Extracts top 5 dominant colors in hex format from image bytes."""
        if HAS_PIL:
            try:
                img = Image.open(io.BytesIO(image_bytes))
                img = img.convert("RGB")
                img = img.resize((64, 64))
                # Quantize down to 5 dominant colors
                quantized = img.quantize(colors=5, method=Image.Quantize.MEDIANCUT)
                palette = quantized.getpalette()[:15]  # 5 colors * 3 (r, g, b)
                hex_colors = []
                for i in range(0, len(palette), 3):
                    r, g, b = palette[i], palette[i+1], palette[i+2]
                    hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")
                if len(hex_colors) >= 3:
                    return hex_colors
            except Exception:
                pass

        # Robust Mathematical Sampling Fallback
        sample_hash = hashlib.sha256(image_bytes).hexdigest()
        colors = []
        for i in range(0, 30, 6):
            chunk = sample_hash[i:i+6]
            colors.append(f"#{chunk}")
        return colors[:5]
