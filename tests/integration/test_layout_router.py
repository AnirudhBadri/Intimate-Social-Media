"""Integration tests for Custom Den Layout endpoints."""

import io
import unittest
from fastapi.testclient import TestClient
from den_prototype.app import create_app
from den_prototype.dependencies import engine

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class TestLayoutRouter(unittest.TestCase):
    """Verifies REST endpoints for layout listing, synthesis, uploading, and activation."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = TestClient(cls.app)

    def test_list_layouts(self):
        resp = self.client.get("/api/layouts")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("layouts", data)
        self.assertGreaterEqual(len(data["layouts"]), 3)

    def test_get_layout_success(self):
        resp = self.client.get("/api/layouts/preset-grunge-garage")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("layout", data)
        self.assertEqual(data["layout"]["id"], "preset-grunge-garage")

    def test_get_layout_not_found(self):
        resp = self.client.get("/api/layouts/non-existent-layout-xyz")
        self.assertEqual(resp.status_code, 404)

    def test_generate_from_prompt_success(self):
        payload = {"prompt": "90s grunge garage band rehearsal space with amps and couch"}
        resp = self.client.post("/api/layouts/prompt", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertIn("layout", data)
        self.assertEqual(data["layout"]["source_mode"], "prompt")
        self.assertEqual(data["layout"]["palette"]["floor_type"], "concrete")

    def test_generate_from_prompt_empty_error(self):
        payload = {"prompt": "   "}
        resp = self.client.post("/api/layouts/prompt", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_generate_from_image_upload(self):
        if HAS_PIL:
            img = Image.new("RGB", (64, 64), color=(34, 197, 94))
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            img_bytes = buf.getvalue()
        else:
            img_bytes = b"sample-jpeg-bytes-content"

        files = {"file": ("my_greenhouse.jpg", img_bytes, "image/jpeg")}
        data = {"hint": "A rainy greenhouse nook"}
        resp = self.client.post("/api/layouts/upload", files=files, data=data)
        self.assertEqual(resp.status_code, 200)
        res_data = resp.json()
        self.assertTrue(res_data["success"])
        self.assertIn("layout", res_data)
        self.assertEqual(res_data["layout"]["source_mode"], "image")
        self.assertGreaterEqual(len(res_data["layout"]["extracted_palette"]), 3)

    def test_select_layout_success(self):
        payload = {"layout_id": "preset-rooftop-sunset"}
        resp = self.client.post("/api/layouts/select", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["layout"]["id"], "preset-rooftop-sunset")

    def test_select_layout_not_found(self):
        payload = {"layout_id": "non-existent-layout-xyz"}
        resp = self.client.post("/api/layouts/select", json=payload)
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
