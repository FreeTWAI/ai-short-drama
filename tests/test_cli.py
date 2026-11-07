import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestCLIE2E(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.drama_lint = self.root / "scripts" / "drama_lint.py"
        self.studio_lint = self.root / "scripts" / "studio_lint.py"

        self.valid_drama_pack = {
            "project": {
                "title": "My Drama",
                "market": "Global",
                "format": "vertical",
                "episode_duration_seconds": 60.0,
                "planned_episodes": 3,
            },
            "premise_contract": {
                "public_identity": "Delivery guy",
                "hidden_truth": "Time traveler",
                "engine": "Reversing time 5 seconds",
                "season_question": "Can he save her?",
                "fresh_twist": "He loses memories when reversing time",
            },
            "characters": [],
            "locations": [],
            "episodes": [
                {
                    "id": "ep_001",
                    "hook": "Delivery late",
                    "turn": "Gets hit by car",
                    "cliffhanger": "Wakes up 5 seconds ago",
                    "payoff": "He survives",
                    "characters": [],
                    "locations": [],
                    "state_delta": ["Discovers time power"],
                    "debts_opened": [],
                    "debts_paid": []
                }
            ]
        }

        self.valid_studio_plan = {
            "format_profile": {
                "id": "viral_one_take",
                "story_scope": "single_high_impact_moment",
                "target_duration_seconds": 10,
                "shot_strategy": "one_take",
                "dominant_turn": "The locked door opens from the inside.",
            },
            "model_capability": {
                "model_id": "example/video/v1",
                "status": "verified",
                "max_duration_seconds": 10,
                "max_reference_assets": 4,
                "supported_reference_types": ["image"],
                "verified_at": "2026-08-13",
                "evidence": "official documentation checked for this run",
            },
            "global_settings": {
                "aspect_ratio": "9:16",
                "visual_style": "cinematic grounded realism",
                "lighting": "motivated practical lighting",
                "color_tone": "warm skin and cool shadows",
                "language": "zh-TW",
                "audio_baseline": "dialogue-forward controlled room tone",
            },
            "assets": [
                {
                    "id": "loc_hall_01",
                    "kind": "location",
                    "name": "hallway",
                    "recurrence": "recurring",
                    "visual_anchor": "approved location sheet v1",
                    "consent_status": "not_applicable",
                    "identity_views": [],
                    "reference_files": ["hall.png"],
                }
            ],
            "timeline": [
                {
                    "id": "beat_001",
                    "start_seconds": 0,
                    "duration_seconds": 10,
                    "shot_size": "medium",
                    "camera_move": "slow_track_back",
                    "angle": "eye_level",
                    "location_id": "loc_hall_01",
                    "emotion": "contained_panic",
                    "transition": "none",
                    "entity_ids": [],
                    "observable_action": "The lead backs toward the locked door.",
                    "dialogue": [],
                    "sound": "Footsteps approach through the hallway.",
                }
            ],
            "variation_policy": {
                "seed": 1847,
                "dimensions": ["pace", "dialogue_density"],
                "shuffle_bag": True,
                "avoid_recent": 3,
            },
            "outputs": {
                "prompt_mode": "both",
                "draft_path": "projects/demo/studio-plan.json",
                "asset_inbox": "projects/demo/assets/inbox",
                "editor_handoff": "9:16 timeline with captions, dialogue, SFX, and QA notes",
            },
        }

    def _run_script(self, script, args, stdin=None):
        cmd = [sys.executable, str(script)] + args
        kwargs = {"capture_output": True, "text": True}
        if stdin is not None:
            kwargs["input"] = stdin
        return subprocess.run(cmd, **kwargs)

    def test_drama_lint_valid_file(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            json.dump(self.valid_drama_pack, f)
            temp_path = f.name

        try:
            result = self._run_script(self.drama_lint, [temp_path])
            self.assertEqual(result.returncode, 0)
            self.assertIn("VALID", result.stdout)
        finally:
            Path(temp_path).unlink()

    def test_drama_lint_stdin(self):
        stdin_data = json.dumps(self.valid_drama_pack)
        result = self._run_script(self.drama_lint, ["-"], stdin=stdin_data)
        self.assertEqual(result.returncode, 0)
        self.assertIn("VALID", result.stdout)

    def test_drama_lint_invalid_json(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("{ invalid json")
            temp_path = f.name

        try:
            result = self._run_script(self.drama_lint, [temp_path])
            self.assertEqual(result.returncode, 1)
            self.assertIn("INVALID", result.stdout)
            self.assertIn("cannot read valid JSON", result.stdout)
        finally:
            Path(temp_path).unlink()

    def test_drama_lint_json_output(self):
        stdin_data = json.dumps(self.valid_drama_pack)
        result = self._run_script(self.drama_lint, ["-", "--json"], stdin=stdin_data)
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["error_count"], 0)

    def test_drama_lint_json_output_invalid(self):
        invalid_data = dict(self.valid_drama_pack)
        invalid_data["episodes"] = "not an array"
        stdin_data = json.dumps(invalid_data)
        result = self._run_script(self.drama_lint, ["-", "--json"], stdin=stdin_data)
        self.assertEqual(result.returncode, 1)
        data = json.loads(result.stdout)
        self.assertFalse(data["valid"])
        self.assertGreater(data["error_count"], 0)
        self.assertTrue(any("must be an array" in item["message"] for item in data["findings"]))

    def test_studio_lint_valid_file(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            json.dump(self.valid_studio_plan, f)
            temp_path = f.name

        try:
            result = self._run_script(self.studio_lint, [temp_path])
            self.assertEqual(result.returncode, 0)
            self.assertIn("VALID", result.stdout)
        finally:
            Path(temp_path).unlink()

    def test_studio_lint_stdin(self):
        stdin_data = json.dumps(self.valid_studio_plan)
        result = self._run_script(self.studio_lint, ["-"], stdin=stdin_data)
        self.assertEqual(result.returncode, 0)
        self.assertIn("VALID", result.stdout)

    def test_studio_lint_invalid_json(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("{ invalid json")
            temp_path = f.name

        try:
            result = self._run_script(self.studio_lint, [temp_path])
            self.assertEqual(result.returncode, 1)
            self.assertIn("INVALID", result.stdout)
            self.assertIn("cannot read valid JSON", result.stdout)
        finally:
            Path(temp_path).unlink()

    def test_studio_lint_json_output(self):
        stdin_data = json.dumps(self.valid_studio_plan)
        result = self._run_script(self.studio_lint, ["-", "--json"], stdin=stdin_data)
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertTrue(data["valid"])
        self.assertEqual(data["error_count"], 0)

    def test_studio_lint_json_output_invalid(self):
        invalid_data = dict(self.valid_studio_plan)
        invalid_data["assets"] = "not an array"
        stdin_data = json.dumps(invalid_data)
        result = self._run_script(self.studio_lint, ["-", "--json"], stdin=stdin_data)
        self.assertEqual(result.returncode, 1)
        data = json.loads(result.stdout)
        self.assertFalse(data["valid"])
        self.assertGreater(data["error_count"], 0)
        self.assertTrue(any("must be an array" in item["message"] for item in data["findings"]))


if __name__ == "__main__":
    unittest.main()
