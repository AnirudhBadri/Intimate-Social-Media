"""Core DenEngine state machine & orchestrator for The Den prototype.
Delegates domain behaviors to specialized modular services while maintaining
thread-safe real-time state and WebSocket synchronization.
"""

import asyncio
from typing import Dict, List, Optional, Any

from .models.user import UserProfile, AvatarConfig, FeedConfig
from .models.exhaust import SpotifyExhaust, LetterboxdExhaust, GitHubExhaust
from .models.social import (
    LoreItem,
    MicroPollOption,
    MicroPoll,
    DogParkFamiliar,
    DogParkEvent,
    SlowGameState,
    ThemeConfig,
    HearthFocusSession,
)
from .models.tangents import TangentCard, ConversationImport, CornerBoothState, SparringChallenge
from .models.state import DenState, RoomResidue
from .models.layout import CustomRoomLayout

from .services.tangent_service import TangentService
from .services.lore_service import LoreService
from .services.game_service import GameService
from .services.theme_service import ThemeService
from .services.artifacts_service import ArtifactsService
from .services.layout_service import LayoutService


class DenEngine:
    """Central state machine coordinating users, ambient exhausts, and social rituals."""

    def __init__(self, den_id: str = "living-room-alpha"):
        self.den_id = den_id
        self.den_type = "buddies"
        self.dunbar_cap = 15  # Strict Dunbar limit

        # Domain Services
        self.tangent_service = TangentService()
        self.lore_service = LoreService()
        self.game_service = GameService()
        self.theme_service = ThemeService()
        self.artifacts_service = ArtifactsService()
        self.layout_service = LayoutService()

        # In-Memory State
        self.users: Dict[str, UserProfile] = {}
        self.spotify_streams: Dict[str, SpotifyExhaust] = {}
        self.letterboxd_streams: Dict[str, LetterboxdExhaust] = {}
        self.github_streams: Dict[str, GitHubExhaust] = {}
        self.active_poll: Optional[MicroPoll] = None
        self.dog_park_familiars: List[DogParkFamiliar] = []
        self.dog_park_events: List[DogParkEvent] = []
        self.recent_dispatches: List[Dict[str, Any]] = []
        self.active_embers: List[Dict[str, str]] = []
        self.corner_booth: Optional[CornerBoothState] = None
        self.room_residues: List[RoomResidue] = []
        self.hearth_session: Optional[HearthFocusSession] = None
        self.current_custom_layout: Optional[CustomRoomLayout] = None

        # Real-time WebSocket Subscribers
        self.subscribers: List[asyncio.Queue] = []

        # Seed initial authentic mock state
        self._seed_initial_state()

    @property
    def inside_jokes(self) -> List[LoreItem]:
        return self.lore_service.inside_jokes

    @property
    def slow_game(self) -> SlowGameState:
        return self.game_service.slow_game

    @property
    def current_theme(self) -> ThemeConfig:
        return self.theme_service.current_theme

    def _seed_initial_state(self):
        """Seeds rich, realistic data for the Core Trio and familiar friends."""
        # 1. Core Trio + 1 Close Friend (4 total seats filled out of 15)
        self.users = {
            "badri": UserProfile(
                id="badri",
                name="Badri",
                handle="@badri_dev",
                avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
                status_text="Refactoring the payment gateway in the rain 🌧️",
                location="Bengaluru",
                timezone="IST",
                is_online=True,
                vibe_card={"role": "Host & Architect", "drink": "Filter Coffee", "music": "Post-Rock"},
                avatar_config=AvatarConfig(
                    outfit_color="#38bdf8",
                    skin_tone="#fbcfe8",
                    hair_color="#1c1917",
                    hair_style="beanie",
                    drink="coffee",
                    accessory="glasses"
                )
            ),
            "dave": UserProfile(
                id="dave",
                name="Dave",
                handle="@dave_london",
                avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
                status_text="Reviewing PRs with warm Darjeeling tea ☕",
                location="London",
                timezone="BST",
                is_online=True,
                vibe_card={"role": "Systems Sceptic", "drink": "Darjeeling", "music": "Ambient Techno"},
                avatar_config=AvatarConfig(
                    outfit_color="#10b981",
                    skin_tone="#fde047",
                    hair_color="#78350f",
                    hair_style="cap",
                    drink="scotch",
                    accessory="headphones"
                )
            ),
            "priya": UserProfile(
                id="priya",
                name="Priya",
                handle="@priya_sf",
                avatar="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80",
                status_text="Deploying ML weights on modal.com",
                location="San Francisco",
                timezone="PST",
                is_online=False,
                vibe_card={"role": "Research Lead", "drink": "Matcha Latte", "music": "IDM"},
                avatar_config=AvatarConfig(
                    outfit_color="#f43f5e",
                    skin_tone="#f59e0b",
                    hair_color="#1c1917",
                    hair_style="curly",
                    drink="boba",
                    accessory="scarf"
                )
            ),
            "sam": UserProfile(
                id="sam",
                name="Sam",
                handle="@sam_berlin",
                avatar="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80",
                status_text="Building in public • Offline in 20m",
                location="Berlin",
                timezone="CEST",
                is_online=True,
                vibe_card={"role": "Hardware Hacker", "drink": "Club Mate", "music": "Minimalist"},
                avatar_config=AvatarConfig(
                    outfit_color="#a855f7",
                    skin_tone="#b45309",
                    hair_color="#d97706",
                    hair_style="messy",
                    drink="beer",
                    accessory="camera"
                )
            )
        }

        # 2. Ambient Exhaust Streams
        self.spotify_streams = {
            "badri": SpotifyExhaust(
                is_playing=True,
                track_name="Nude",
                artist="Radiohead",
                album="In Rainbows",
                cover_url="https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17?w=150&auto=format&fit=crop&q=80"
            ),
            "dave": SpotifyExhaust(
                is_playing=True,
                track_name="Windowlicker",
                artist="Aphex Twin",
                album="Selected Ambient Works",
                cover_url="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=150&auto=format&fit=crop&q=80"
            ),
            "sam": SpotifyExhaust(
                is_playing=False,
                track_name="Avril 14th",
                artist="Aphex Twin",
                album="Drukqs",
                cover_url="https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=150&auto=format&fit=crop&q=80"
            )
        }

        self.letterboxd_streams = {
            "dave": LetterboxdExhaust(
                title="Dune: Part Two",
                year=2024,
                rating=4.5,
                poster_url="https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=150&auto=format&fit=crop&q=80",
                review_snippet="Gurney Halleck playing the baliset had me ascending in IMAX.",
                watched_at="Yesterday 11:20 PM"
            ),
            "priya": LetterboxdExhaust(
                title="Perfect Days",
                year=2023,
                rating=5.0,
                poster_url="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=150&auto=format&fit=crop&q=80",
                review_snippet="Wim Wenders made cleaning Tokyo toilets feel like the highest spiritual calling.",
                watched_at="3 days ago"
            )
        }

        self.github_streams = {
            "badri": GitHubExhaust(
                repo="badri/the-den-spatial",
                commit_msg="feat: 3D corner booth whisper nook & tangent cartographer",
                branch="main",
                timestamp="14m ago"
            ),
            "sam": GitHubExhaust(
                repo="sam/firmware-driver",
                commit_msg="fix: SPI clock jitter on ESP32-S3",
                branch="master",
                timestamp="2h ago"
            )
        }

        # 3. Pre-seeded Inside Jokes
        self.lore_service.inside_jokes = [
            LoreItem(
                author="Dave",
                quote="It’s not tech debt, it’s architectural heritage.",
                context="Said during the 3 AM Postgres migration outage of 2024",
                consecrated_by=["Dave", "Badri"],
                is_consecrated=True
            ),
            LoreItem(
                author="Priya",
                quote="I didn't overfit the model, reality just underfit my weights.",
                context="NeurIPS deadline sprint 2025",
                consecrated_by=["Priya"],
                is_consecrated=False
            ),
            LoreItem(
                author="Badri",
                quote="We can rewrite the whole front-end in pure Three.js over the weekend.",
                context="Famous last words before 48-hour caffeine blur",
                consecrated_by=["Badri", "Sam"],
                is_consecrated=True
            )
        ]

        # 4. Micro-Poll
        self.active_poll = MicroPoll(
            title="What's our Saturday night ritual?",
            context="Dave is in town for 48 hours before flying to Tokyo.",
            options=[
                MicroPollOption(id="opt1", text="Late night Korean BBQ & Soju", votes=["badri", "priya"]),
                MicroPollOption(id="opt2", text="Board game marathon + slow tea", votes=["dave"]),
                MicroPollOption(id="opt3", text="Hacking on retro synthesizers", votes=[])
            ]
        )

        # 5. Dog Park Familiars
        self.dog_park_familiars = [
            DogParkFamiliar(
                id="f1",
                owner_id="badri",
                owner_name="Badri",
                name="Byte",
                species="Golden Retriever",
                avatar="🐕",
                current_action="Sleeping soundly on the Persian rug by the fireplace",
                toy="Worn tennis ball"
            ),
            DogParkFamiliar(
                id="f2",
                owner_id="dave",
                owner_name="Dave",
                name="Pixel",
                species="Welsh Corgi",
                avatar="🦊",
                current_action="Gnawing peacefully on a cedar wood chip",
                toy="Squeaky plush bone"
            ),
            DogParkFamiliar(
                id="f3",
                owner_id="priya",
                owner_name="Priya",
                name="Kumo",
                species="Akita",
                avatar="🐺",
                current_action="Watching the rain streaks through the bay window",
                toy="Rope knot"
            )
        ]

        self.dog_park_events = [
            DogParkEvent(
                familiar_names=["Byte", "Pixel"],
                description="Byte nudged his tennis ball over to Pixel's paws. Pixel wagged once and curled back up."
            )
        ]

        # 6. Active Embers & Dispatches
        self.active_embers = [
            {"from": "Dave", "to": "Badri", "timestamp": "12m ago", "message": "🔥 Warm Ember from Dave to Badri's coffee mug."}
        ]

        self.recent_dispatches = [
            {"platform": "WhatsApp Bridge", "channel": "#the-den-living-room", "timestamp": "5m ago", "snippet": "Dave clinked glasses with Badri."}
        ]

        # 7. Corner Booth Initial Tangents
        self.corner_booth = CornerBoothState(
            booth_id="corner-booth-whisper",
            participants=["badri", "dave"],
            active_tangents=[
                TangentCard(
                    title="The Great Monolith vs Microservices Debate",
                    category="unfinished_debate",
                    last_discussed="Imported from WhatsApp (Oct 1)",
                    summary="Dave argued that microservices introduce unwarranted network latency for small teams. Badri defended domain boundary decoupling.",
                    key_quotes=[
                        "Dave: At what operational overhead though?",
                        "Badri: Domain isolation prevents spaghetti migrations later!"
                    ],
                    starter_prompt="Hey Dave, we never settled that argument about monoliths vs microservices from last week...",
                    is_active=True
                ),
                TangentCard(
                    title="Dave's Tokyo Relocation Crossroads",
                    category="unresolved_decision",
                    last_discussed="Imported from Signal (Sep 28)",
                    summary="Dave received an engineering leadership offer based in Shibuya, weighing the 9-hour timezone delta from London friends.",
                    key_quotes=[
                        "Dave: Shibuya office looks incredible, but the timezone lag will be brutal.",
                        "Badri: We can make the Den async grace mode work regardless."
                    ],
                    starter_prompt="Dave, whatever happened with that Tokyo offer you were weighing?",
                    is_active=True
                ),
                TangentCard(
                    title="70s Japanese City Pop Vinyl Hunting",
                    category="deep_rabbit_hole",
                    last_discussed="Imported from Voice Call (Sep 22)",
                    summary="Shared rabbit hole exploring Tatsuro Yamashita, Taeko Onuki, and early analog synthesizer mixing chains.",
                    key_quotes=[
                        "Dave: 'Spacy' on original acetate pressing hits different.",
                        "Badri: The bassline on 'Love Space' is impossible on modern digital."
                    ],
                    starter_prompt="I was just spinning that Tatsuro Yamashita album we talked about...",
                    is_active=True
                )
            ],
            history_imports=[
                ConversationImport(
                    source="WhatsApp",
                    partner_id="dave",
                    partner_name="Dave",
                    raw_snippet="Dave: bro did you check the benchmark?\nBadri: yeah sqlite choked on 500 writes/sec\nDave: let's test WAL mode next week"
                )
            ],
            active_challenges=[
                SparringChallenge(
                    author="Dave",
                    target_user="badri",
                    topic="SQLite WAL mode vs RocksDB on NVMe",
                    raw_argument="Read amplification on RocksDB isn't worth the write throughput gain for our dataset size. We should stay on SQLite WAL.",
                    citation_link="https://sqlite.org/wal.html",
                    status="staged"
                )
            ]
        )

        # 8. Room Residues (Temporal Echo) & Sovereign Acoustic Hearth
        self.room_residues = [
            RoomResidue(
                friend_id="priya",
                friend_name="Priya",
                departed_at_label="2 hours ago",
                last_action="Closed laptop after NeurIPS test run",
                left_note="Checkpointed model weights to modal.com. Heading to dinner in SF.",
                drink_status="cold_tea"
            ),
            RoomResidue(
                friend_id="dave",
                friend_name="Dave",
                departed_at_label="4 hours ago",
                last_action="Signed off after midnight London sprint",
                left_note="Benchmark sqlite WAL mode tomorrow morning.",
                drink_status="melted_ice"
            )
        ]
        self.hearth_session = HearthFocusSession(
            user_id="badri",
            duration_minutes=45,
            logs_added=1,
            is_active=True,
            flame_intensity=0.85
        )

    def get_state(self) -> DenState:
        """Returns the complete immutable DenState snapshot for client rendering."""
        name_map = {
            "buddies": "College Buddies Den 🍻",
            "personal": "Badri's Sovereign Hearth 🛋️",
            "family": "Family Sanctum 🏡"
        }
        return DenState(
            den_id=self.den_id,
            name=name_map.get(self.den_type, "The Den Sanctuary"),
            den_type=self.den_type,
            host_id="badri",
            dunbar_cap=self.dunbar_cap,
            active_friends_count=len(self.users),
            users=list(self.users.values()),
            spotify_streams=self.spotify_streams,
            letterboxd_streams=self.letterboxd_streams,
            github_streams=self.github_streams,
            inside_jokes=self.inside_jokes,
            active_poll=self.active_poll,
            dog_park_familiars=self.dog_park_familiars,
            dog_park_events=self.dog_park_events,
            slow_game=self.slow_game,
            current_theme=self.current_theme,
            recent_dispatches=self.recent_dispatches,
            active_embers=self.active_embers,
            corner_booth=self.corner_booth,
            room_residues=self.room_residues,
            hearth_session=self.hearth_session,
            current_custom_layout=self.current_custom_layout,
            available_custom_layouts=self.layout_service.list_layouts()
        )

    def send_ember(self, from_user: str, to_user: str) -> Dict[str, Any]:
        """Dispatches an asynchronous zero-interaction-debt presence Ember."""
        fallback = UserProfile(id="", name="Friend", handle="", avatar="", status_text="", location="", timezone="")
        target_name = self.users.get(to_user, fallback).name
        sender_name = self.users.get(from_user, fallback).name

        ember = {
            "from": sender_name,
            "to": target_name,
            "timestamp": "Just now",
            "message": f"🔥 Warm Ember from {sender_name} to {target_name} (Zero-Debt Presence)"
        }
        self.active_embers.insert(0, ember)
        if len(self.active_embers) > 5:
            self.active_embers.pop()
        self._notify_subscribers()
        return {"success": True, "ember": ember}

    def switch_den(self, den_id: str) -> DenState:
        """Switches context between Personal, Buddies, and Family Dens."""
        if den_id in ["personal", "buddies", "family"]:
            self.den_type = den_id
            self._notify_subscribers()
        return self.get_state()

    def consecrate_lore(self, joke_id: str, user_name: str) -> Dict[str, Any]:
        """Delegates lore consecration to LoreService with 2-party mutual consent."""
        res = self.lore_service.consecrate_lore(joke_id, user_name)
        if res.get("success"):
            self._notify_subscribers()
        return res

    def take_slow_game_turn(self, player_name: str) -> SlowGameState:
        """Delegates turn advancement to GameService."""
        game = self.game_service.take_turn(player_name)
        self._notify_subscribers()
        return game

    def add_friend(self, user: UserProfile) -> Dict[str, Any]:
        """Strict Dunbar limit enforcement (max 15 seats)."""
        # If updating existing friend, allow update
        if user.id in self.users:
            self.users[user.id] = user
            self._notify_subscribers()
            return {"success": True, "remaining_slots": self.dunbar_cap - len(self.users)}

        # New friend: check cap
        if len(self.users) >= self.dunbar_cap:
            return {
                "success": False,
                "error": (
                    f"Dunbar Limit Reached! The Den strictly caps members at {self.dunbar_cap} "
                    f"to preserve authentic intimacy and eliminate performative masks."
                )
            }
        self.users[user.id] = user
        self._notify_subscribers()
        return {"success": True, "remaining_slots": self.dunbar_cap - len(self.users)}

    def vote_poll(self, option_id: str, user_id: str) -> bool:
        """Casts or updates a micro-poll vote."""
        if not self.active_poll:
            return False

        option_found = any(opt.id == option_id for opt in self.active_poll.options)
        if not option_found:
            return False

        for opt in self.active_poll.options:
            if user_id in opt.votes:
                opt.votes.remove(user_id)
            if opt.id == option_id:
                opt.votes.append(user_id)

        self._notify_subscribers()
        return True

    def add_inside_joke(self, author: str, quote: str, context: str) -> LoreItem:
        """Adds a candidate inside joke to the lore service."""
        joke = self.lore_service.add_inside_joke(author, quote, context)
        self._notify_subscribers()
        return joke

    def trigger_roast(self, from_user: str, target_user: str, message: str) -> Dict[str, Any]:
        """Dispatches an impromptu roast to the recent dispatches feed."""
        fallback = UserProfile(id="", name="Friend", handle="", avatar="", status_text="", location="", timezone="")
        target_name = self.users.get(target_user, fallback).name
        sender_name = self.users.get(from_user, fallback).name

        dispatch = {
            "platform": "WhatsApp & Discord Bridge",
            "channel": "#the-den-living-room",
            "timestamp": "Just now",
            "snippet": f"🔥 Roast from {sender_name} to {target_name}: '{message}'"
        }
        self.recent_dispatches.insert(0, dispatch)
        if len(self.recent_dispatches) > 6:
            self.recent_dispatches.pop()
        self._notify_subscribers()
        return {"success": True, "dispatch": dispatch}

    def generate_theme(self, prompt: str) -> ThemeConfig:
        """Generates dynamic ambient styling via ThemeService."""
        theme = self.theme_service.generate_theme(prompt)
        self._notify_subscribers()
        return theme

    def update_user_avatar(self, user_id: str, config: AvatarConfig) -> Dict[str, Any]:
        """Updates the 3D visual configuration for an avatar."""
        if user_id not in self.users:
            return {"success": False, "error": f"User '{user_id}' not found in Den."}
        self.users[user_id].avatar_config = config
        self._notify_subscribers()
        return {"success": True, "user_id": user_id, "avatar_config": config.model_dump()}

    def update_user_feed(self, config: FeedConfig) -> Dict[str, Any]:
        """Updates ambient exhaust feeds (Spotify, Letterboxd, GitHub, status) for a user."""
        user_id = config.user_id
        if user_id not in self.users:
            return {"success": False, "error": f"User '{user_id}' not found in Den."}

        if config.custom_status:
            self.users[user_id].status_text = config.custom_status

        if config.spotify_track:
            self.spotify_streams[user_id] = SpotifyExhaust(
                is_playing=config.spotify_playing,
                track_name=config.spotify_track,
                artist=config.spotify_artist or "Unknown Artist",
                album="Live Exhaust Stream",
                cover_url="https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17?w=100"
            )

        if config.letterboxd_title:
            self.letterboxd_streams[user_id] = LetterboxdExhaust(
                title=config.letterboxd_title,
                year=2024,
                rating=config.letterboxd_rating,
                poster_url="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=100",
                review_snippet=config.letterboxd_review or "Logged via Den Feed Manager",
                watched_at="Just now"
            )

        if config.github_repo:
            self.github_streams[user_id] = GitHubExhaust(
                repo=config.github_repo,
                commit_msg=config.github_commit or "Manual commit sync",
                branch="main",
                timestamp="Just now"
            )

        self._notify_subscribers()
        return {"success": True, "user_id": user_id, "feed": config.model_dump()}

    def import_thread_and_extract_tangents(
        self,
        user_id: str,
        partner_id: str,
        source: str,
        raw_text: str
    ) -> Dict[str, Any]:
        """Parses chat transcripts and extracts continuity tangents via TangentService."""
        fallback = UserProfile(id="", name="Friend", handle="", avatar="", status_text="", location="", timezone="")
        partner_name = self.users.get(partner_id, fallback).name
        user_name = self.users.get(user_id, fallback).name

        new_tangent = self.tangent_service.extract_tangent(
            user_name=user_name,
            partner_name=partner_name,
            source=source,
            raw_text=raw_text
        )

        if not self.corner_booth:
            self.corner_booth = CornerBoothState()

        self.corner_booth.active_tangents.insert(0, new_tangent)
        self.corner_booth.history_imports.insert(
            0,
            ConversationImport(
                source=source,
                partner_id=partner_id,
                partner_name=partner_name,
                raw_snippet=raw_text[:280] if raw_text else "",
                extracted_tangents=[new_tangent]
            )
        )

        self._notify_subscribers()
        return {"success": True, "tangent": new_tangent.model_dump()}

    def feed_hearth_log(self, user_id: str = "badri", minutes: int = 45) -> HearthFocusSession:
        """Adds a wood log to the acoustic fireplace timer for focused deep work."""
        if not self.hearth_session or not self.hearth_session.is_active:
            self.hearth_session = HearthFocusSession(
                user_id=user_id,
                duration_minutes=minutes,
                logs_added=1,
                is_active=True,
                flame_intensity=1.0
            )
        else:
            self.hearth_session.duration_minutes += minutes
            self.hearth_session.logs_added += 1
            self.hearth_session.flame_intensity = 1.0

        self._notify_subscribers()
        return self.hearth_session

    def stage_sparring_challenge(
        self,
        author: str,
        target_user: str,
        topic: str,
        raw_argument: str,
        citation_link: str = ""
    ) -> SparringChallenge:
        """Stages an asynchronous intellectual sparring challenge (ammunition for reunion)."""
        challenge = self.tangent_service.stage_sparring_challenge(
            author=author,
            target_user=target_user,
            topic=topic,
            argument=raw_argument,
            citation_link=citation_link
        )
        if not self.corner_booth:
            self.corner_booth = CornerBoothState()
        self.corner_booth.active_challenges.insert(0, challenge)
        self._notify_subscribers()
        return challenge

    def get_artifacts_content(self) -> Dict[str, str]:
        """Delegates strategy artifact fetching to ArtifactsService."""
        return self.artifacts_service.get_artifacts()

    # Custom Den Layout Engine
    def generate_layout_from_prompt(self, prompt: str) -> CustomRoomLayout:
        """Synthesizes a 3D procedural layout from text prompt and activates it."""
        layout = self.layout_service.generate_from_prompt(prompt)
        self.current_custom_layout = layout
        self._notify_subscribers()
        return layout

    def generate_layout_from_image(self, image_bytes: bytes, filename: str, user_hint: str = "") -> CustomRoomLayout:
        """Synthesizes a 3D procedural layout from uploaded photo and activates it."""
        layout = self.layout_service.generate_from_image(image_bytes, filename, user_hint)
        self.current_custom_layout = layout
        self._notify_subscribers()
        return layout

    def set_custom_layout(self, layout_id: str) -> Optional[CustomRoomLayout]:
        """Selects and broadcasts an existing custom layout."""
        layout = self.layout_service.get_layout(layout_id)
        if layout:
            self.current_custom_layout = layout
            self._notify_subscribers()
        return layout

    def list_custom_layouts(self) -> List[CustomRoomLayout]:
        """Returns all pre-seeded and synthesized custom layouts."""
        return self.layout_service.list_layouts()

    # WebSocket Real-Time Synchronization
    def subscribe(self, queue: asyncio.Queue):
        self.subscribers.append(queue)

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self.subscribers:
            self.subscribers.remove(queue)

    def _notify_subscribers(self):
        state = self.get_state().model_dump()
        for q in list(self.subscribers):
            try:
                q.put_nowait(state)
            except Exception:
                pass
