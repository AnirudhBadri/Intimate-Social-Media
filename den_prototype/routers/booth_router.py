"""Corner Booth thread import, tangent cartography, and strategy blueprints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..dependencies import get_engine
from ..engine import DenEngine

router = APIRouter(tags=["Corner Booth & Tangents"])

class BoothImportRequest(BaseModel):
    user_id: str = "badri"
    partner_id: str = "dave"
    source: str = "WhatsApp Export"
    raw_text: str

@router.post("/api/booth/import")
async def import_booth_thread(req: BoothImportRequest, engine: DenEngine = Depends(get_engine)):
    """Ingests raw chat transcript and extracts conversation continuity tangents."""
    res = engine.import_thread_and_extract_tangents(
        user_id=req.user_id,
        partner_id=req.partner_id,
        source=req.source,
        raw_text=req.raw_text
    )
    return res

class SparringChallengeRequest(BaseModel):
    author: str = "badri"
    target_user: str = "dave"
    topic: str
    argument: str
    citation_link: str = ""

@router.post("/api/booth/challenge")
async def stage_sparring_challenge_api(req: SparringChallengeRequest, engine: DenEngine = Depends(get_engine)):
    """Stages an asynchronous intellectual sparring challenge on a buddy's coaster."""
    challenge = engine.stage_sparring_challenge(
        author=req.author,
        target_user=req.target_user,
        topic=req.topic,
        raw_argument=req.argument,
        citation_link=req.citation_link
    )
    return {"success": True, "challenge": challenge.model_dump()}

@router.get("/api/artifacts")
async def get_artifacts_api(engine: DenEngine = Depends(get_engine)):
    """Returns markdown strategy blueprint documents for in-browser inspection."""
    return engine.get_artifacts_content()
