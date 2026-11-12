"""Real-time WebSocket state streaming endpoint."""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..dependencies import get_engine

router = APIRouter(tags=["WebSocket Real-Time"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Establishes bidirectional state stream pushing state deltas on any room event."""
    engine = get_engine()
    await websocket.accept()
    queue = asyncio.Queue()
    engine.subscribe(queue)

    # Immediately push initial state snapshot
    await websocket.send_text(json.dumps(engine.get_state().model_dump()))
    try:
        while True:
            # Wait for reactive broadcast from engine
            state = await queue.get()
            await websocket.send_text(json.dumps(state))
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    finally:
        engine.unsubscribe(queue)
