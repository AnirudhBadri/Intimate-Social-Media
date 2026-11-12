"""User avatar customization and ambient exhaust stream endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..dependencies import get_engine
from ..engine import DenEngine
from ..models.user import AvatarConfig, FeedConfig
from ..models.exhaust import LetterboxdExhaust

router = APIRouter(tags=["User & Ambient Exhaust"])

class AvatarUpdateRequest(BaseModel):
    user_id: str = "badri"
    avatar_config: AvatarConfig

@router.post("/api/user/avatar")
async def update_avatar_api(req: AvatarUpdateRequest, engine: DenEngine = Depends(get_engine)):
    """Updates the 3D visual configuration for an avatar."""
    res = engine.update_user_avatar(req.user_id, req.avatar_config)
    return res

@router.post("/api/user/feeds")
async def update_feeds_api(req: FeedConfig, engine: DenEngine = Depends(get_engine)):
    """Updates ambient exhaust feeds (Spotify, Letterboxd, GitHub, status)."""
    res = engine.update_user_feed(req)
    return res

class SimulateRequest(BaseModel):
    action: str  # 'spotify_change', 'letterboxd_log', 'github_commit'
    user_id: str = "dave"

@router.post("/api/ambient/simulate")
async def simulate_ambient(req: SimulateRequest, engine: DenEngine = Depends(get_engine)):
    """Developer test harness for triggering immediate simulated feed changes."""
    if req.action == "spotify_change":
        if req.user_id in engine.spotify_streams:
            engine.spotify_streams[req.user_id].track_name = "Fake Plastic Trees"
            engine.spotify_streams[req.user_id].artist = "Radiohead"
            engine.spotify_streams[req.user_id].progress_ms = 12000
    elif req.action == "letterboxd_log":
        engine.letterboxd_streams[req.user_id] = LetterboxdExhaust(
            title="Everything Everywhere All at Once",
            year=2022,
            rating=5.0,
            poster_url="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=150&auto=format&fit=crop&q=80",
            review_snippet="Rewatched with hot dog fingers. Still crying.",
            watched_at="Just now"
        )
    elif req.action == "github_commit":
        if req.user_id in engine.github_streams:
            engine.github_streams[req.user_id].commit_msg = (
                "refactor: replace infinite feed with bounded Dunbar living room"
            )
            engine.github_streams[req.user_id].timestamp = "Just now"

    engine._notify_subscribers()
    return {"success": True, "state": engine.get_state().model_dump()}
