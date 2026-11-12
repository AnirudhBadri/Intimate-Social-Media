"""Integration tests for live WebSocket state streaming."""

import json
import unittest
from starlette.testclient import TestClient
from den_prototype.app import app

class TestWebSocketStreaming(unittest.TestCase):
    """Verifies bidirectional real-time state synchronization via /ws."""

    def test_websocket_initial_state_and_reactive_push(self):
        client = TestClient(app)
        with client.websocket_connect("/ws") as websocket:
            # 1. Verify initial state snapshot received immediately
            initial_data = websocket.receive_text()
            state = json.loads(initial_data)
            self.assertIn("name", state)
            self.assertIn("users", state)
            self.assertEqual(state["dunbar_cap"], 15)

            # 2. Trigger an action via HTTP client while socket is connected
            client.post("/api/den/switch", json={"den_id": "personal"})

            # 3. Verify WebSocket receives the updated broadcast state
            updated_data = websocket.receive_text()
            updated_state = json.loads(updated_data)
            self.assertEqual(updated_state["den_type"], "personal")

            # Reset back to buddies
            client.post("/api/den/switch", json={"den_id": "buddies"})

if __name__ == "__main__":
    unittest.main()
