# 🛋️ Den Design Document: Spatial Architecture & UX Specification
*The Handcrafted Living Room for the Modern Digital Sanctuary*

---

> [!IMPORTANT]
> **Design Philosophy**: The Den is crafted with the holistic dedication of Eric Barone (*Stardew Valley*). Every pixel, material roughness, lighting drop-off, and audio oscillation is tuned to eliminate the cold sterility of corporate web design and evoke the tactile warmth of a physical sanctuary.

---

## 1. The 4 Handcrafted Spatial Environments

Users transition dynamically between four distinct architectural rooms, each tailored to different social moods:

```
    +-------------------------------------------------------------------------+
    |                         THE 4 SPATIAL ENVIRONMENTS                      |
    +-------------------------------------------------------------------------+
    |  1. The Velvet Speakeasy     |  Warm mahogany, hanging Edison pendants, |
    |     (Main Social Bar)        |  liquor bottles, Persian rug, dog Byte   |
    +------------------------------+------------------------------------------+
    |  2. The Corner Booth         |  Intimate L-shaped velvet banquette,     |
    |     (Whisper Nook Breakout)  |  Tiffany lamp, leather Tangent Journal   |
    +------------------------------+------------------------------------------+
    |  3. Basement Poker Den       |  Green felt circular table, chip stacks, |
    |     (Strategy & Play)        |  sharp overhead spotlight, board dice    |
    +------------------------------+------------------------------------------+
    |  4. The Hearth Library       |  Crackling stone fireplace, cedar wood   |
    |     (Quiet Co-Working)       |  bookshelves, deep reading armchairs     |
    +------------------------------+------------------------------------------+
```

### 1.1 The Velvet Speakeasy Bar (`buildSpeakeasyBar`)
* **Lighting**: Three warm Edison pendants (`THREE.PointLight`, 2.2 intensity, 2700K amber) with soft shadow mapping.
* **Materials**: Polished dark walnut bar counter, glossy oak floorboards (`roughness: 0.35`, `metalness: 0.1`), and backlit shelving holding procedural amber, emerald, and ruby spirit bottles.
* **Ambient Soul**: A sleeping golden retriever ("Byte") curled on a woven Persian rug, with procedural chest breathing animations.

### 1.2 The Corner Booth • Whisper Nook (`buildCornerBooth`)
* **Purpose**: Intimate 2-to-3 person breakout space for deep debates, private check-ins, or thread continuation.
* **Lighting**: Downward-focused stained glass Tiffany lamp casting warm amber illumination (`THREE.SpotLight`, `angle: Math.PI / 3.5`).
* **Tactile Centerpiece**: A 3D antique leather-bound **Thread Journal** on the mahogany table with glowing parchment edges (`emissive: 0xd97706`). Clicking the journal triggers the **Tangent Cartographer**.

### 1.3 The Basement Poker Den (`buildPokerDen`)
* **Atmosphere**: Speakeasy basement hideaway with a deep emerald circular table (`#047857`), padded leather rail bumpers, and multicolored poker chip stacks.
* **Interactive Coaster**: 3D dice coaster for taking turns in the asynchronous slow board game.

### 1.4 The Hearth Library (`buildHearthLibrary`)
* **Atmosphere**: Stone hearth with procedural flickering orange firelight (`THREE.PointLight`, 3.5 intensity), two tall dark-stained cedar bookshelves, and wingback reading armchairs.

---

## 2. Avatar Anatomy & Handcrafted Visual Rigging

Avatars in The Den avoid both corporate memojis and complex uncanny humanoid meshes. They are tactile, stylized tabletop figurines composed of geometric primitives:

```
           [ Head: SphereGeometry(0.22) ]
              |-- Hair/Hat: Beanie, Cap, Curly, Sleek, Messy
              |-- Accessory: Gold Wire Glasses, DJ Headphones, Scarf
           [ Torso: BoxGeometry(0.6, 0.65, 0.35) ]
              |-- Custom Knit Sweater / Outfit Color
           [ Hands & Drink Prop: Scotch, Coffee, Beer, Boba, Cocktail ]
```

### Procedural Micro-Animations
* **Resting Breath**: Subtle sine-wave vertical chest and head oscillation (`y = baseY + Math.sin(time * 2.0) * 0.02`).
* **Mouse Parallax**: Smooth camera float (`lerp(camera.position.x, mouseNormalized.x * 0.4, 0.05)`) creating tactile 3D depth without requiring player navigation.
* **Zero-Locomotion Guarantee**: Avatars remain permanently seated at their designated stools/chairs; users never navigate with WASD or arrow keys.

---

## 3. Procedural Web Audio Engine (`SoundEngine`)

To eliminate latency and external asset dependencies, all sound effects are synthesized organically in real time using the browser's native **Web Audio API**:

1. **Crystal Glass Clink (`playGlassClink()`)**: Dual sine oscillators (2400 Hz and 3600 Hz) with exponential decaying gain ramps simulating acoustic resonance of heavy bar crystal.
2. **Resin Dice Roll (`playDiceRoll()`)**: Multi-tap triangle oscillator bursts (140 Hz to 40 Hz) simulating tumbling resin dice on felt.
3. **Acetate Needle Drop (`playNeedleDrop()`)**: Low-frequency sawtooth transient ramp (60 Hz to 120 Hz) with crackle gain decay.
4. **Dog Whimper / Sigh (`playDogWhimper()`)**: Modulated sine frequency ramp (600 Hz -> 800 Hz -> 500 Hz) simulating a cozy sleeping companion.

---

## 4. UI Overlay Architecture

* **Spatial Speech Bubbles**: Fixed-position 3D projected bubbles (`Vector3.project(camera)`) displaying only the most recent status, live Spotify track, and Letterboxd rating. Bubbles auto-orient above the active avatar.
* **Top Artisan Navigation**:
  * Room Switcher: `🥃 Speakeasy Bar`, `🛋️ Corner Booth`, `♠️ Poker Den`, `📚 Hearth Library`.
  * Action Controls: `📜 Blueprints`, `🗺️ Tangents`, `🎨 Avatar Studio`, `📡 Exhaust Pipes`, `+ Extra Chair ($3.99)`.
* **Expandable Den Ledger**: A collapsible vintage drawer containing inside jokes, cinema logs, and GitHub commit histories.
* **In-Browser Blueprint Reader**: Full-screen markdown rendering suite displaying strategic architectures and design documents directly within the application.
