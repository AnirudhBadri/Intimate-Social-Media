"""Den management, state retrieval, and presence endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..dependencies import get_engine
from ..engine import DenEngine
from ..models.user import UserProfile

router = APIRouter(tags=["Den Management"])

@router.get("/api/state")
async def get_state(engine: DenEngine = Depends(get_engine)):
    """Returns the complete immutable DenState snapshot."""
    return engine.get_state().model_dump()

class DenSwitchRequest(BaseModel):
    den_id: str

@router.post("/api/den/switch")
async def switch_den(req: DenSwitchRequest, engine: DenEngine = Depends(get_engine)):
    """Switches active Den context (Personal, Buddies, Family)."""
    state = engine.switch_den(req.den_id)
    return {"success": True, "state": state.model_dump()}

class EmberRequest(BaseModel):
    from_user: str = "badri"
    to_user: str = "dave"

@router.post("/api/ember")
async def send_ember_api(req: EmberRequest, engine: DenEngine = Depends(get_engine)):
    """Dispatches a zero-debt presence Ember signal."""
    res = engine.send_ember(req.from_user, req.to_user)
    return res

class AddFriendTestRequest(BaseModel):
    friend_name: str
    friend_handle: str

@router.post("/api/friends/add_test")
async def add_friend_test(req: AddFriendTestRequest, engine: DenEngine = Depends(get_engine)):
    """Adds a friend seat enforcing the strict Dunbar limit (max 15)."""
    new_user = UserProfile(
        id=req.friend_handle.replace("@", "").lower(),
        name=req.friend_name,
        handle=req.friend_handle,
        avatar="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80",
        status_text="Just joined the Den!",
        location="Remote",
        timezone="UTC",
        is_online=True
    )
    result = engine.add_friend(new_user)
    return result
