"""Tangent cartography and conversation continuity models for The Den."""

from typing import List
from pydantic import BaseModel, Field
import time
import uuid

class TangentCard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    category: str = "unfinished_debate"  # 'unfinished_debate', 'unresolved_decision', 'deep_rabbit_hole'
    last_discussed: str = "2 weeks ago"
    summary: str
    key_quotes: List[str] = Field(default_factory=list)
    starter_prompt: str
    is_active: bool = True

class ConversationImport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    source: str = "WhatsApp"  # 'WhatsApp', 'Signal', 'Voice Call', 'Telegram'
    partner_id: str
    partner_name: str
    imported_at: float = Field(default_factory=time.time)
    raw_snippet: str
    extracted_tangents: List[TangentCard] = Field(default_factory=list)

class SparringChallenge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    author: str
    target_user: str
    topic: str
    raw_argument: str
    citation_link: str = ""
    created_at: float = Field(default_factory=time.time)
    status: str = "staged"  # 'staged', 'accepted', 'consecrated'

class CornerBoothState(BaseModel):
    booth_id: str = "corner-booth-whisper"
    participants: List[str] = Field(default_factory=lambda: ["badri", "dave"])
    active_tangents: List[TangentCard] = Field(default_factory=list)
    history_imports: List[ConversationImport] = Field(default_factory=list)
    active_challenges: List[SparringChallenge] = Field(default_factory=list)
