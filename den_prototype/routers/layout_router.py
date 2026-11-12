"""Custom 3D Room Layout router for prompt-based and image-based spatial generation."""

import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from ..dependencies import get_engine
from ..engine import DenEngine

router = APIRouter(tags=["Custom Room Layouts"])


class PromptLayoutRequest(BaseModel):
    prompt: str


class SelectLayoutRequest(BaseModel):
    layout_id: str


@router.get("/api/layouts")
async def list_layouts(engine: DenEngine = Depends(get_engine)):
    """Returns all available custom room layouts (presets and generated)."""
    layouts = engine.list_custom_layouts()
    return {"layouts": [l.model_dump() for l in layouts]}


@router.get("/api/layouts/{layout_id}")
async def get_layout(layout_id: str, engine: DenEngine = Depends(get_engine)):
    """Fetches a specific custom room layout specification."""
    layout = engine.layout_service.get_layout(layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail=f"Layout '{layout_id}' not found")
    return {"layout": layout.model_dump()}


@router.post("/api/layouts/prompt")
async def generate_from_prompt_endpoint(
    req: PromptLayoutRequest,
    engine: DenEngine = Depends(get_engine)
):
    """Synthesizes a 3D procedural room layout from a natural language vibe prompt."""
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt must not be empty")
    layout = engine.generate_layout_from_prompt(req.prompt.strip())
    return {
        "success": True,
        "message": f"Successfully synthesized '{layout.name}'",
        "layout": layout.model_dump()
    }


@router.post("/api/layouts/upload")
async def generate_from_image_endpoint(
    file: UploadFile = File(...),
    hint: Optional[str] = Form(""),
    engine: DenEngine = Depends(get_engine)
):
    """Synthesizes a 3D procedural room layout from an uploaded photo of a familiar space."""
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    
    layout = engine.generate_layout_from_image(
        image_bytes=image_bytes,
        filename=file.filename or "uploaded_room.jpg",
        user_hint=hint or ""
    )
    return {
        "success": True,
        "message": f"Successfully synthesized '{layout.name}' from photo",
        "layout": layout.model_dump()
    }


@router.post("/api/layouts/select")
async def select_layout_endpoint(
    req: SelectLayoutRequest,
    engine: DenEngine = Depends(get_engine)
):
    """Selects and broadcasts an active custom layout across connected clients."""
    layout = engine.set_custom_layout(req.layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail=f"Layout '{req.layout_id}' not found")
    return {
        "success": True,
        "message": f"Switched to layout '{layout.name}'",
        "layout": layout.model_dump()
    }
