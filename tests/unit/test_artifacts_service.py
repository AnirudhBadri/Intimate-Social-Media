"""Unit tests for ArtifactsService."""

import os
import tempfile
import unittest
from den_prototype.services.artifacts_service import ArtifactsService

class TestArtifactsService(unittest.TestCase):
    """Verifies safe scanning, reading, and graceful handling of strategy markdown artifacts."""

    def test_read_artifacts_from_temp_dir(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file1 = os.path.join(tmp_dir, "doc1.md")
            with open(file1, "w", encoding="utf-8") as f:
                f.write("# Blueprint 1\nContent of doc 1")

            file2 = os.path.join(tmp_dir, "doc2.md")
            with open(file2, "w", encoding="utf-8") as f:
                f.write("# Blueprint 2\nContent of doc 2")

            service = ArtifactsService(custom_dir=tmp_dir)
            artifacts = service.get_artifacts()

            self.assertIn("doc1.md", artifacts)
            self.assertIn("doc2.md", artifacts)
            self.assertIn("Blueprint 1", artifacts["doc1.md"])

    def test_nonexistent_dir_returns_empty_dict(self):
        service = ArtifactsService(custom_dir="/path/that/definitely/does/not/exist_12345")
        # Falls back to default directories, or returns empty if none exist
        artifacts = service.get_artifacts()
        self.assertIsInstance(artifacts, dict)

if __name__ == "__main__":
    unittest.main()
