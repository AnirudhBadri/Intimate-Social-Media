"""Social rituals, polls, inside jokes, roasts, slow game, and themes."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..dependencies import get_engine
from ..engine import DenEngine

router = APIRouter(tags=["Social Rituals"])

class VoteRequest(BaseModel):
    option_id: str
    user_id: str = "badri"

@router.post("/api/poll/vote")
async def vote_poll(req: VoteRequest, engine: DenEngine = Depends(get_engine)):
    """Casts or updates a micro-poll vote."""
    success = engine.vote_poll(req.option_id, req.user_id)
    return {"success": success, "state": engine.get_state().model_dump()}

class JokeRequest(BaseModel):
    author: str
    quote: str
    context: str

@router.post("/api/joke")
async def add_joke(req: JokeRequest, engine: DenEngine = Depends(get_engine)):
    """Adds a candidate inside joke with initial endorsement."""
    joke = engine.add_inside_joke(req.author, req.quote, req.context)
    return {"success": True, "joke": joke.model_dump()}

class ConsecrateRequest(BaseModel):
    joke_id: str
    user_name: str = "Badri"

@router.post("/api/lore/consecrate")
async def consecrate_lore(req: ConsecrateRequest, engine: DenEngine = Depends(get_engine)):
    """Registers 2-party mutual consent to consecrate room lore."""
    res = engine.consecrate_lore(req.joke_id, req.user_name)
    return res

class RoastRequest(BaseModel):
    from_user: str = "badri"
    target_user: str
    message: str

@router.post("/api/roast")
async def trigger_roast(req: RoastRequest, engine: DenEngine = Depends(get_engine)):
    """Dispatches an impromptu roast to the recent dispatches stream."""
    res = engine.trigger_roast(req.from_user, req.target_user, req.message)
    return res

class GameRollRequest(BaseModel):
    player_name: str = "Dave"

@router.post("/api/game/roll")
async def roll_game(req: GameRollRequest, engine: DenEngine = Depends(get_engine)):
    """Advances turn in the asynchronous Slow Board Game."""
    game = engine.take_slow_game_turn(req.player_name)
    return {"success": True, "game": game.model_dump()}

class ThemeRequest(BaseModel):
    prompt: str

@router.post("/api/theme")
async def generate_theme(req: ThemeRequest, engine: DenEngine = Depends(get_engine)):
    """Generates dynamic room styling based on a natural language vibe prompt."""
    theme = engine.generate_theme(req.prompt)
    return {"success": True, "theme": theme.model_dump()}

class HearthLogRequest(BaseModel):
    user_id: str = "badri"
    minutes: int = 45

@router.post("/api/hearth/log")
async def feed_hearth_log_api(req: HearthLogRequest, engine: DenEngine = Depends(get_engine)):
    """Feeds a wood log to the acoustic fireplace timer for focused deep work."""
    session = engine.feed_hearth_log(req.user_id, req.minutes)
    return {"success": True, "hearth_session": session.model_dump()}
