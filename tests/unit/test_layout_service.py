"""Unit tests for LayoutService and procedural 3D layout synthesis."""

import io
import unittest
from den_prototype.services.layout_service import LayoutService
from den_prototype.models.layout import CustomRoomLayout

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class TestLayoutService(unittest.TestCase):
    """Verifies prompt parsing, median-cut palette extraction, and spatial compilation."""

    def setUp(self):
        self.service = LayoutService()

    def test_default_presets_seeded(self):
        layouts = self.service.list_layouts()
        self.assertGreaterEqual(len(layouts), 3)
        layout_ids = [l.id for l in layouts]
        self.assertIn("preset-grunge-garage", layout_ids)
        self.assertIn("preset-rainy-greenhouse", layout_ids)
        self.assertIn("preset-rooftop-sunset", layout_ids)

    def test_generate_from_prompt_garage(self):
        prompt = "90s grunge garage band rehearsal space with amps and couch"
        layout = self.service.generate_from_prompt(prompt)
        self.assertIsInstance(layout, CustomRoomLayout)
        self.assertEqual(layout.source_mode, "prompt")
        self.assertEqual(layout.palette.floor_type, "concrete")
        self.assertEqual(layout.soundscape, "tape_hum")
        prop_types = [p.type for p in layout.props]
        self.assertIn("amp_stack", prop_types)
        self.assertIn("neon_sign", prop_types)

    def test_generate_from_prompt_greenhouse(self):
        prompt = "Rainy botanical greenhouse sanctuary with potted monsteras and glass roof"
        layout = self.service.generate_from_prompt(prompt)
        self.assertEqual(layout.palette.wall_type, "glass_greenhouse")
        self.assertEqual(layout.palette.floor_type, "slate_tile")
        self.assertEqual(layout.soundscape, "rain")
        prop_types = [p.type for p in layout.props]
        self.assertIn("plants", prop_types)

    def test_generate_from_prompt_rooftop(self):
        prompt = "Sunset rooftop porch with city skyline view and string lights"
        layout = self.service.generate_from_prompt(prompt)
        self.assertEqual(layout.palette.floor_type, "wood_plank")
        self.assertEqual(layout.soundscape, "night_crickets")

    def test_generate_from_prompt_fallback_hash(self):
        prompt = "A cozy mysterious underground library hidden inside a cave"
        layout = self.service.generate_from_prompt(prompt)
        self.assertIsInstance(layout, CustomRoomLayout)
        self.assertIsNotNone(layout.palette.floor_type)
        self.assertGreater(len(layout.props), 0)
        self.assertGreater(len(layout.seats), 0)

    def test_generate_from_image_palette_extraction(self):
        # Create a small in-memory 64x64 test image with known warm amber tones
        if HAS_PIL:
            img = Image.new("RGB", (64, 64), color=(217, 119, 6))
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            img_bytes = buf.getvalue()
        else:
            img_bytes = b"fake-jpeg-binary-header-bytes-data-stream"

        layout = self.service.generate_from_image(
            image_bytes=img_bytes,
            filename="my_college_den.jpg",
            user_hint="Cozy living room with brick fireplace and amps"
        )
        self.assertIsInstance(layout, CustomRoomLayout)
        self.assertEqual(layout.source_mode, "image")
        self.assertEqual(layout.source_input, "my_college_den.jpg")
        self.assertGreaterEqual(len(layout.extracted_palette), 3)
        self.assertEqual(layout.palette.wall_type, "exposed_brick")
        self.assertEqual(layout.soundscape, "cedar_fire")

    def test_layout_persistence_and_retrieval(self):
        prompt = "Neon cyberpunk tea room with tatami mats"
        layout = self.service.generate_from_prompt(prompt)
        saved = self.service.get_layout(layout.id)
        self.assertIsNotNone(saved)
        self.assertEqual(saved.id, layout.id)
        self.assertEqual(saved.name, layout.name)


if __name__ == "__main__":
    unittest.main()
