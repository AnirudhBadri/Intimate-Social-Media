"""Artifacts service for loading and serving design & strategy blueprints."""

import os
from typing import Dict

class ArtifactsService:
    """Reads and serves markdown blueprint documents from the artifact repository."""

    DEFAULT_ARTIFACT_DIRS = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "artifacts"),
        r"C:\Users\badri\.gemini\antigravity\brain\85f24069-6998-4096-a07f-9ba60ff48bcb",
    ]

    def __init__(self, custom_dir: str = None):
        self.custom_dir = custom_dir

    def get_artifacts(self) -> Dict[str, str]:
        """Scans candidate artifact directories and returns map of filename -> markdown content."""
        search_dirs = [self.custom_dir] if self.custom_dir else []
        search_dirs.extend(self.DEFAULT_ARTIFACT_DIRS)

        target_dir = None
        for d in search_dirs:
            if d and os.path.isdir(d):
                target_dir = d
                break

        artifacts: Dict[str, str] = {}
        if not target_dir:
            return artifacts

        try:
            for fname in os.listdir(target_dir):
                if fname.endswith(".md"):
                    fpath = os.path.join(target_dir, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            artifacts[fname] = f.read()
                    except Exception as err:
                        artifacts[fname] = f"Error reading artifact: {err}"
        except Exception as scan_err:
            artifacts["_error.md"] = f"Error scanning directory: {scan_err}"

        return artifacts
