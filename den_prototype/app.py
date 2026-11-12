"""FastAPI web application & router hub for The Den prototype."""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .dependencies import engine
from .routers import (
    den_router,
    social_router,
    user_router,
    booth_router,
    websocket_router,
    layout_router,
)

def create_app() -> FastAPI:
    """Application factory assembling modular routers and configuration."""
    app = FastAPI(
        title="The Den — Artisan 3D Spatial Living Room",
        description="A bounded, anti-engagement farm digital sanctuary for authentic connection.",
        version="2.0.0"
    )

    # Static Assets & Uploads
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(os.path.join(static_dir, "uploads"), exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Include Modular API Routers
    app.include_router(den_router)
    app.include_router(social_router)
    app.include_router(user_router)
    app.include_router(booth_router)
    app.include_router(websocket_router)
    app.include_router(layout_router)

    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")

    @app.get("/", response_class=HTMLResponse, tags=["Frontend UI"])
    async def get_index():
        """Serves the primary Three.js 3D spatial living room client."""
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>The Den is running. Template not found.</h1>", status_code=500)

    return app

app = create_app()
