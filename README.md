# Intimate Social Media: The Den
### *An Anti-Engagement Farm & Artisan 3D Spatial Sanctuary for Genuine Human Connection*

---

## 1. The Core Manifesto: Why Small Social Media Matters

Modern social media platforms are **engagement farms** engineered on algorithmic dopamine loops, infinite scroll treadmills, rage-baiting, context collapse, and parasitic advertising metrics. They treat human relationships like monetizable inventory:
- **Metrics over Meaning:** Follower counts, like ratios, retweets, and viral reach incentivize outrage, performative vulnerability, and shallow broadcast culture.
- **Context Collapse:** Close confidants, distant acquaintances, employers, and anonymous adversaries are crushed into a single public feed, destroying psychological safety and authentic communication.
- **Asymmetric Reply Debt:** Unread message indicators, red notification badges, and read receipts transform casual socializing into an anxiety-inducing administrative burden.

### The Antidote: Intimate Social Media
**The Den** is a standalone, bounded, anti-algorithmic digital living room designed for high-trust human cohorts (families, close friends, research collaborators):
1. **Mathematical Dunbar Cap ($N \le 15$):** Strict mathematical enforcement of Robin Dunbar’s core support clique size ($10-15$ individuals). A Den cannot be expanded beyond 15 members—eliminating the incentive to build an audience.
2. **Ambient Exhaust over Performative Broadcasts:** Instead of manual status updates and curated photos, presence is communicated passively through real-time ambient exhausts (what music you're listening to via Spotify, movies you've logged on Letterboxd, code commits on GitHub, and hearth status).
3. **Zero-Debt Presence (Embers & Familiars):** Sending an "Ember" or letting AI familiars interact in the dog park conveys warmth and acknowledgment without creating a reply obligation or notification backlog.
4. **Mutual Lore Consecration:** Inside jokes, quotes, and memories require multi-party consensus to be consecrated into the permanent Den lore wall.
5. **Acoustic Corner Booth & Spatial Voice:** Dedicated private nooks for deep epistemic sparring, audio voice exchanges, and shared reflection without public exposure.

---

## 2. System Architecture & Features

```
+-----------------------------------------------------------------------------------+
|                           THE DEN ARCHITECTURE                                    |
+-----------------------------------------------------------------------------------+
|  FRONTEND (Three.js WebGL)      BACKEND (FastAPI / WebSockets)   STATE & ISOLATION|
|  - 3D Spatial Living Room       - Modular FastAPI Routers        - In-Memory State|
|  - Real-time Avatar Positions   - Real-time WebSocket Hub        - Air-Gapped Dens|
|  - Interactive Furnishings      - REST APIs (Booth, Lore, Poll)  - Multi-Sanctum  |
+-----------------------------------------------------------------------------------+
```

### Core Subsystems
- **3D Spatial Living Room Client (`den_prototype/templates/index.html`):** An artisan Three.js canvas featuring customizable room themes, avatars, interactive furniture (record player, bookshelf, hearth, coffee table), and ambient lighting.
- **The Dunbar Guard (`den_prototype/engine.py`):** Mathematically forbids adding a 16th user to maintain an authentic intimate cohort.
- **Ambient Exhausts (`den_prototype/models/exhaust.py`):** Live streaming of Spotify tracks, Letterboxd film logs, and GitHub development telemetry.
- **Asynchronous Slow Games & Micro-Polls (`den_prototype/models/social.py`):** Turn-based casual board games and low-friction group consensus tools that respect members' time and attention.
- **Acoustic Corner Booth (`den_prototype/routers/booth_router.py`):** Private audio and tangent recording sanctuary for 1-on-1 dialogue.
- **Air-Gapped Multi-Den Isolation:** Seamlessly switch between separate intimate spheres (e.g. *Buddies Den*, *Family Sanctum*, *Sovereign Hearth*) with zero data leakage.

---

## 3. Quick Start & Local Execution

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Modern Web Browser (Zen Browser, Firefox, Chrome) with WebGL support

### Running The Den Server

To launch the live spatial server:
```powershell
py -3.14 launch_den_server.py
```
Or use the automated verification runner:
```powershell
py -3.14 run_den_prototype.py
```

Open your browser to:
```text
http://127.0.0.1:8090
```

---

## 4. Repository Structure

```text
Intimate-Social-Media/
├── README.md                           # Core Manifesto & Architecture Guide
├── launch_den_server.py                # Standalone server launcher (port 8090)
├── run_den_prototype.py                # Verification harness & automated test suite
├── den_prototype/                      # The Den Core Application
│   ├── app.py                          # FastAPI application factory & router mount
│   ├── engine.py                       # DenEngine state machine & Dunbar cap enforcer
│   ├── dependencies.py                 # Engine singleton dependency injection
│   ├── models/                         # Domain models
│   │   ├── exhaust.py                  # Spotify, Letterboxd & GitHub passive streams
│   │   ├── social.py                   # Lore items, micro-polls, dog park familiars, slow game
│   │   ├── tangents.py                 # Tangent cards, corner booth, sparring challenges
│   │   ├── state.py                    # Real-time room state & residues
│   │   ├── layout.py                   # Custom 3D room layout schemas
│   │   └── user.py                     # User profile & avatar customization
│   ├── routers/                        # FastAPI REST & WebSocket endpoints
│   │   ├── den_router.py               # State queries, den switching, hearth focus
│   │   ├── social_router.py            # Micro-polls, lore consecration, slow game, embers
│   │   ├── user_router.py              # User profiles, avatars & passive exhausts
│   │   ├── booth_router.py             # Corner booth private voice & tangents
│   │   ├── layout_router.py            # Room layouts & generative space themes
│   │   └── websocket_router.py         # Real-time multi-user live synchronization
│   ├── services/                       # Specialized domain services
│   │   ├── lore_service.py             # Multi-party lore consecration
│   │   ├── game_service.py             # Asynchronous turn-based game logic
│   │   ├── tangent_service.py          # Audio dispatches & tangent archive
│   │   ├── theme_service.py            # Ambient generative room themes
│   │   └── layout_service.py           # Custom 3D furniture & asset placement
│   ├── static/                         # Textures, audio dispatches & uploaded media
│   └── templates/
│       └── index.html                  # Artisan Three.js 3D Spatial Living Room Client
└── docs/
    └── ARCHITECTURE.md                 # Technical architecture & protocol documentation
```

---

## 5. Verification & Test Suite

The test runner programmatically asserts:
- **Dunbar Cap Saturation & Rejection:** Verifies $N=15$ friend ceiling and blocks the 16th member.
- **Ambient Exhaust Streaming:** Validates Spotify, Letterboxd, and GitHub data flows.
- **2-Party Lore Consecration:** Asserts consensus voting before quotes become permanent lore.
- **Zero-Debt Presence:** Tests Ember delivery without conversational reply debt.
- **FastAPI Endpoints:** Complete HTTP test coverage across all REST and WebSocket routes.
