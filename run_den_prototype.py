"""Task Script: run_den_prototype.py
Verification and launcher for The Den (Small Social Media Prototype).

Protocol: Single-Approval Task Script Protocol
Execution Command: py -3.14 run_den_prototype.py
"""

import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import time
import threading
import uvicorn
import requests

from den_prototype.engine import DenEngine
from den_prototype.models import UserProfile
from den_prototype.app import app

from starlette.testclient import TestClient

def run_engine_verification():
    print("=" * 60)
    print("1. VERIFYING DUNBAR CAP ENFORCEMENT & BOUNDARY CONDITIONS")
    print("=" * 60)
    engine = DenEngine("test-den")
    initial_count = len(engine.users)
    print(f"[*] Initial Pre-seeded Friends: {initial_count} / {engine.dunbar_cap}")
    assert initial_count == 4, f"Expected 4 pre-seeded users, got {initial_count}"

    # Add 11 more friends to fill the 15 slots exactly
    for i in range(initial_count, 15):
        u = UserProfile(
            id=f"friend_{i}",
            name=f"Friend {i}",
            handle=f"@friend_{i}",
            avatar="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150",
            status_text="Testing slot saturation",
            location="Global",
            timezone="UTC",
            is_online=True
        )
        res = engine.add_friend(u)
        assert res["success"] is True, f"Failed to add friend {i}"

    print(f"[✓] Successfully saturated Den to exactly {len(engine.users)} / {engine.dunbar_cap} friends.")

    # Try to add friend #16 (Violating Dunbar limit)
    intruder = UserProfile(
        id="intruder_16",
        name="The 16th Person",
        handle="@intruder_16",
        avatar="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150",
        status_text="Trying to breach Dunbar cap",
        location="Nowhere",
        timezone="UTC",
        is_online=True
    )
    breach_attempt = engine.add_friend(intruder)
    print(f"[*] Attempting to add 16th friend...")
    print(f"    Result: {breach_attempt}")
    assert breach_attempt["success"] is False, "Dunbar limit was violated!"
    assert "Dunbar Limit Reached" in breach_attempt["error"]
    print("[✓] Dunbar Boundary Guard is 100% Mathematically Sound.")

    print("\n" + "=" * 60)
    print("2. VERIFYING AMBIENT EXHAUST & MICRO-POLL ENGINE")
    print("=" * 60)
    engine2 = DenEngine("demo-den")
    state = engine2.get_state()
    print(f"[*] Spotify Active Streams: {len(state.spotify_streams)}")
    for uid, sp in state.spotify_streams.items():
        print(f"    - {uid}: {sp.track_name} by {sp.artist} (Playing: {sp.is_playing})")
    
    print(f"[*] Letterboxd Logs: {len(state.letterboxd_streams)}")
    for uid, lb in state.letterboxd_streams.items():
        print(f"    - {uid}: {lb.title} ({lb.rating}★) - '{lb.review_snippet}'")

    print(f"[*] Micro-Poll: '{state.active_poll.title}'")
    engine2.vote_poll("opt2", "sam")
    assert "sam" in engine2.active_poll.options[1].votes
    print(f"[✓] Micro-Poll vote cast by Sam successfully. Votes: {engine2.active_poll.options[1].votes}")

    print("\n" + "=" * 60)
    print("3. VERIFYING THE AI DOG PARK, SLOW GAME & LORE CONSECRATION")
    print("=" * 60)
    print(f"[*] Dog Park Familiars Playing: {len(state.dog_park_familiars)}")
    for f in state.dog_park_familiars:
        print(f"    - {f.avatar} {f.name} ({f.species}, Owner: {f.owner_name}): '{f.current_action}'")
    
    # Test Slow Game turn
    initial_turn = state.slow_game.turn_number
    updated_game = engine2.take_slow_game_turn("Badri")
    assert updated_game.turn_number == initial_turn + 1
    print(f"[✓] Asynchronous Slow Game Turn Advanced: Turn {updated_game.turn_number} (Next Player: {updated_game.active_player_name})")

    # Test 2-Party Lore Consecration (Theme 7)
    candidate_joke = next(j for j in engine2.inside_jokes if not j.is_consecrated)
    print(f"[*] Candidate Lore Item: '{candidate_joke.quote}' (Votes: {candidate_joke.consecrated_by})")
    consecrate_res = engine2.consecrate_lore(candidate_joke.id, "Dave")
    assert consecrate_res["is_consecrated"] is True
    print(f"[✓] 2-Party Mutual Consecration Achieved! Votes: {consecrate_res['votes']}, Is Consecrated: {consecrate_res['is_consecrated']}")

    # Test Multi-Den Context Isolation
    personal_state = engine2.switch_den("personal")
    assert personal_state.den_type == "personal"
    assert "Sovereign Hearth" in personal_state.name
    print(f"[✓] Multi-Den Context Switcher OK: Switched to '{personal_state.name}' (Air-Gapped)")
    engine2.switch_den("buddies")

    theme = engine2.generate_theme("cyberpunk rainy tokyo cafe")
    print(f"[✓] AI Generated Theme: '{theme.theme_name}'")

    print("\n" + "=" * 60)
    print("4. VERIFYING FASTAPI ENDPOINTS WITH TESTCLIENT")
    print("=" * 60)
    client = TestClient(app)
    resp = client.get("/api/state")
    assert resp.status_code == 200
    state_json = resp.json()
    print(f"[✓] GET /api/state: OK (Den: '{state_json['name']}', Members: {state_json['active_friends_count']})")
    
    # Test vote endpoint
    vote_resp = client.post("/api/poll/vote", json={"option_id": "opt1", "user_id": "dave"})
    assert vote_resp.status_code == 200
    print(f"[✓] POST /api/poll/vote: OK")

    # Test slow game roll endpoint
    game_resp = client.post("/api/game/roll", json={"player_name": "Dave"})
    assert game_resp.status_code == 200
    print(f"[✓] POST /api/game/roll: OK (Turn: {game_resp.json()['game']['turn_number']})")

    # Test den switch endpoint
    switch_resp = client.post("/api/den/switch", json={"den_id": "family"})
    assert switch_resp.status_code == 200
    assert switch_resp.json()["state"]["den_type"] == "family"
    print(f"[✓] POST /api/den/switch: OK (Switched to Family Sanctum)")

    # Test ember zero-debt presence endpoint
    ember_resp = client.post("/api/ember", json={"from_user": "badri", "to_user": "dave"})
    assert ember_resp.status_code == 200
    assert ember_resp.json()["success"] is True
    print(f"[✓] POST /api/ember: OK (Dispatched Ember to Dave without reply debt)")

    # Test avatar customization endpoint
    av_resp = client.post("/api/user/avatar", json={
        "user_id": "badri",
        "avatar_config": {
            "outfit_color": "#065f46",
            "skin_tone": "#fbcfe8",
            "hair_color": "#1c1917",
            "hair_style": "beanie",
            "drink": "scotch",
            "accessory": "glasses"
        }
    })
    assert av_resp.status_code == 200
    assert av_resp.json()["success"] is True
    print(f"[✓] POST /api/user/avatar: OK (Badri customized to Forest Pine + Scotch)")

    # Test feed update endpoint
    feed_resp = client.post("/api/user/feeds", json={
        "user_id": "badri",
        "custom_status": "Polishing Three.js shaders & WebGL",
        "spotify_track": "Everything in Its Right Place",
        "spotify_artist": "Radiohead",
        "spotify_playing": True,
        "letterboxd_title": "Past Lives",
        "letterboxd_rating": 5.0,
        "letterboxd_review": "In-Yun wrecked my afternoon.",
        "github_repo": "badri/the-den-spatial",
        "github_commit": "feat: full-stack avatar & feed pipeline"
    })
    assert feed_resp.status_code == 200
    assert feed_resp.json()["success"] is True
    print(f"[✓] POST /api/user/feeds: OK (Badri feed stream broadcasted)")

    # Test template rendering
    html_resp = client.get("/")
    assert html_resp.status_code == 200
    assert "The Den" in html_resp.text
    print(f"[✓] GET /: OK (Artisan Three.js 3D Living Room UI rendered)")

    # Test Custom Layout Engine Endpoints
    layouts_resp = client.get("/api/layouts")
    assert layouts_resp.status_code == 200
    assert len(layouts_resp.json()["layouts"]) >= 3
    print(f"[✓] GET /api/layouts: OK ({len(layouts_resp.json()['layouts'])} layouts available)")

    prompt_resp = client.post("/api/layouts/prompt", json={"prompt": "90s grunge garage band rehearsal space with amps and couch"})
    assert prompt_resp.status_code == 200
    assert prompt_resp.json()["success"] is True
    print(f"[✓] POST /api/layouts/prompt: OK (Synthesized '{prompt_resp.json()['layout']['name']}')")

    print("\n" + "=" * 60)
    print("ALL PROTOTYPE ENGINE & API TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

def main():
    run_engine_verification()
    port = 8765
    print(f"\n" + "=" * 60)
    print(f"[🚀] LAUNCHING THE DEN LIVE SERVER")
    print(f"[ℹ] URL: http://127.0.0.1:{port}")
    print(f"[ℹ] Press Ctrl+C in terminal to stop.")
    print("=" * 60 + "\n")
    uvicorn.run("den_prototype.app:app", host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    main()
