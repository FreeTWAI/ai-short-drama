from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "studio_lint", ROOT / "scripts" / "studio_lint.py"
)
assert SPEC and SPEC.loader
STUDIO_LINT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = STUDIO_LINT
SPEC.loader.exec_module(STUDIO_LINT)


def valid_plan() -> dict:
    return {
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
                "id": "char_lead_01",
                "kind": "character",
                "name": "lead",
                "recurrence": "recurring",
                "visual_anchor": "approved character sheet v1",
                "voice_anchor": "licensed voice profile v1",
                "consent_status": "verified",
                "identity_views": ["front_closeup", "front_full", "side_full"],
                "reference_files": ["lead_close.png", "lead_front.png", "lead_side.png"],
            },
            {
                "id": "loc_hall_01",
                "kind": "location",
                "name": "hallway",
                "recurrence": "recurring",
                "visual_anchor": "approved location sheet v1",
                "consent_status": "not_applicable",
                "identity_views": [],
                "reference_files": ["hall.png"],
            },
        ],
        "timeline": [
            {
                "id": "beat_001",
                "start_seconds": 0,
                "duration_seconds": 4,
                "shot_size": "medium",
                "camera_move": "slow_track_back",
                "angle": "eye_level",
                "location_id": "loc_hall_01",
                "emotion": "contained_panic",
                "transition": "none",
                "entity_ids": ["char_lead_01"],
                "observable_action": "The lead backs toward the locked door.",
                "dialogue": [],
                "sound": "Footsteps approach through the hallway.",
            },
            {
                "id": "beat_002",
                "start_seconds": 4,
                "duration_seconds": 6,
                "shot_size": "closeup",
                "camera_move": "continuous_orbit",
                "angle": "slightly_low",
                "location_id": "loc_hall_01",
                "emotion": "shock",
                "transition": "continuous",
                "entity_ids": ["char_lead_01"],
                "observable_action": "The door opens inward and the lead stops mid-step.",
                "dialogue": [
                    {
                        "speaker_id": "char_lead_01",
                        "text": "You were inside?",
                        "performance": "barely audible",
                    }
                ],
                "sound": "The latch clicks under the approaching footsteps.",
            },
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


class StudioLintTests(unittest.TestCase):

    def test_rejects_top_level_not_dict(self) -> None:
        report = STUDIO_LINT.lint([], studio_ready=True)
        self.assertTrue(any("top-level JSON value must be an object" in item.message for item in report.errors))

    def test_invalid_format_profile(self) -> None:
        plan = valid_plan()
        plan["format_profile"]["id"] = "unknown_format"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("unknown format profile" in item.message for item in report.errors))

    def test_format_mismatch(self) -> None:
        plan = valid_plan()
        plan["format_profile"]["story_scope"] = "wrong_scope"
        plan["format_profile"]["shot_strategy"] = "wrong_strategy"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("requires single_high_impact_moment" in item.message for item in report.errors))
        self.assertTrue(any("requires one_take" in item.message for item in report.errors))

    def test_viral_one_take_duration_warning(self) -> None:
        plan = valid_plan()
        plan["format_profile"]["target_duration_seconds"] = 35
        plan["model_capability"]["max_duration_seconds"] = 40
        plan["timeline"][0]["duration_seconds"] = 35
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("may be carrying a full story" in item.message for item in report.warnings))

    def test_invalid_capability_status(self) -> None:
        plan = valid_plan()
        plan["model_capability"]["status"] = "invalid_status"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be verified or unverified" in item.message for item in report.errors))

    def test_invalid_asset_kind_and_recurrence(self) -> None:
        plan = valid_plan()
        plan["assets"][0]["kind"] = "invalid_kind"
        plan["assets"][0]["recurrence"] = "invalid_recurrence"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("unknown asset kind" in item.message for item in report.errors))
        self.assertTrue(any("must be recurring or one_off" in item.message for item in report.errors))

    def test_missing_voice_anchor_recurring_character(self) -> None:
        plan = valid_plan()
        del plan["assets"][0]["voice_anchor"]
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("required for a recurring character" in item.message for item in report.errors))

    def test_unverified_consent_recurring_character(self) -> None:
        plan = valid_plan()
        plan["assets"][0]["consent_status"] = "not_applicable"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be verified for a recurring character voice" in item.message for item in report.errors))

    def test_empty_timeline(self) -> None:
        plan = valid_plan()
        plan["timeline"] = []
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must contain at least one shot or beat" in item.message for item in report.errors))

    def test_invalid_grid_moment_timeline_length(self) -> None:
        plan = valid_plan()
        plan["format_profile"]["id"] = "grid_moment"
        plan["format_profile"]["shot_strategy"] = "grid"
        plan["timeline"] = plan["timeline"][:1]  # Only 1 panel
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("grid_moment must contain 2 to 24 panels" in item.message for item in report.errors))

    def test_unknown_location_asset(self) -> None:
        plan = valid_plan()
        plan["timeline"][0]["location_id"] = "loc_unknown"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("unknown location asset" in item.message for item in report.errors))

    def test_unknown_character_speaker(self) -> None:
        plan = valid_plan()
        plan["timeline"][1]["dialogue"][0]["speaker_id"] = "char_unknown"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("unknown character" in item.message for item in report.errors))

    def test_invalid_transition_one_take(self) -> None:
        plan = valid_plan()
        plan["timeline"][0]["transition"] = "continuous"  # First beat should be none
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("one-take formats require none on the first beat" in item.message for item in report.errors))

    def test_variation_policy_disabled_shuffle_bag(self) -> None:
        plan = valid_plan()
        plan["variation_policy"]["shuffle_bag"] = False
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("disabled; batch presets may repeat" in item.message for item in report.warnings))

    def test_variation_policy_zero_avoid_recent(self) -> None:
        plan = valid_plan()
        plan["variation_policy"]["avoid_recent"] = 0
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("zero allows immediate preset repetition" in item.message for item in report.warnings))


    def test_valid_studio_ready_plan(self) -> None:
        report = STUDIO_LINT.lint(valid_plan(), studio_ready=True)
        self.assertEqual([], report.errors)

    def test_rejects_reference_overflow(self) -> None:
        plan = valid_plan()
        plan["model_capability"]["max_reference_assets"] = 3
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("above model limit" in item.message for item in report.errors))

    def test_rejects_missing_identity_view_and_unverified_model(self) -> None:
        plan = valid_plan()
        plan["assets"][0]["identity_views"] = ["front_closeup"]
        plan["model_capability"]["status"] = "unverified"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        messages = [item.message for item in report.errors]
        self.assertTrue(any("missing identity views" in message for message in messages))
        self.assertTrue(any("capability probe" in message for message in messages))

    def test_rejects_non_contiguous_timeline(self) -> None:
        plan = valid_plan()
        plan["timeline"][1]["start_seconds"] = 5
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be contiguous" in item.message for item in report.errors))

    def test_rejects_path_traversal(self) -> None:
        plan = valid_plan()
        plan["outputs"]["draft_path"] = "../secret.json"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("without directory traversal" in item.message for item in report.errors))

        plan["outputs"]["draft_path"] = "valid.json"
        plan["outputs"]["asset_inbox"] = "/etc/passwd"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("without directory traversal" in item.message for item in report.errors))

    def test_rejects_infinite_bounds(self) -> None:
        plan = valid_plan()
        plan["format_profile"]["target_duration_seconds"] = float('inf')
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be a positive number" in item.message for item in report.errors))

        plan = valid_plan()
        plan["timeline"][0]["start_seconds"] = float('nan')
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be a non-negative finite number" in item.message for item in report.errors))

    def test_rejects_excessively_long_strings(self) -> None:
        plan = valid_plan()
        plan["outputs"]["editor_handoff"] = "a" * 10001
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be a non-empty string" in item.message for item in report.errors))

    def test_schema_is_valid_json(self) -> None:
        schema_path = ROOT / "scripts" / "studio_plan.schema.json"
        with schema_path.open(encoding="utf-8") as stream:
            schema = json.load(stream)
        self.assertEqual("AI Short Drama Studio Plan", schema["title"])

    def test_lint_does_not_mutate_input(self) -> None:
        plan = valid_plan()
        original = copy.deepcopy(plan)
        STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertEqual(original, plan)

    def test_invalid_format_profile_type(self) -> None:
        plan = valid_plan()
        plan["format_profile"]["target_duration_seconds"] = "not a number"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be a positive number" in item.message for item in report.errors))

    def test_invalid_model_capability_limits(self) -> None:
        plan = valid_plan()
        plan["model_capability"]["max_duration_seconds"] = "not a number"
        plan["model_capability"]["max_reference_assets"] = -1
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be a positive number" in item.message for item in report.errors))
        self.assertTrue(any("must be a non-negative integer" in item.message for item in report.errors))

    def test_missing_assets_array(self) -> None:
        plan = valid_plan()
        plan["assets"] = "not an array"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be an array" in item.message for item in report.errors))

    def test_asset_not_object(self) -> None:
        plan = valid_plan()
        plan["assets"] = ["not a dict"]
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be an object" in item.message for item in report.errors))

    def test_missing_asset_string(self) -> None:
        plan = valid_plan()
        plan["assets"][0]["id"] = ""
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be a non-empty string" in item.message for item in report.errors))

    def test_invalid_asset_reference_files(self) -> None:
        plan = valid_plan()
        plan["assets"][0]["reference_files"] = "not an array"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be an array" in item.message for item in report.errors))

    def test_invalid_asset_reference_files_item(self) -> None:
        plan = valid_plan()
        plan["assets"][0]["reference_files"] = [123]
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be a non-empty string" in item.message for item in report.errors))

    def test_missing_visual_anchor_and_refs_studio_ready(self) -> None:
        plan = valid_plan()
        del plan["assets"][0]["visual_anchor"]
        plan["assets"][0]["reference_files"] = []
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("required for a recurring asset" in item.message for item in report.errors))

    def test_missing_identity_views_studio_ready(self) -> None:
        plan = valid_plan()
        plan["assets"][0]["identity_views"] = "not an array"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be an array" in item.message for item in report.errors))

    def test_timeline_item_not_object(self) -> None:
        plan = valid_plan()
        plan["timeline"] = ["not an object"]
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be an object" in item.message for item in report.errors))

    def test_invalid_timeline_id(self) -> None:
        plan = valid_plan()
        plan["timeline"][0]["id"] = "Invalid_ID_123!"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must use lowercase ASCII" in item.message for item in report.errors))

    def test_duplicate_timeline_id(self) -> None:
        plan = valid_plan()
        plan["timeline"][1]["id"] = plan["timeline"][0]["id"]
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("duplicate timeline id" in item.message for item in report.errors))

    def test_invalid_timeline_start_and_duration_types(self) -> None:
        plan = valid_plan()
        plan["timeline"][0]["start_seconds"] = "not a number"
        plan["timeline"][0]["duration_seconds"] = "not a number"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be a non-negative number" in item.message for item in report.errors))
        self.assertTrue(any("must be a positive number" in item.message for item in report.errors))

    def test_timeline_duration_exceeds_model(self) -> None:
        plan = valid_plan()
        plan["timeline"][0]["duration_seconds"] = 15
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("exceeds model limit" in item.message for item in report.errors))

    def test_invalid_timeline_arrays(self) -> None:
        plan = valid_plan()
        plan["timeline"][0]["entity_ids"] = "not an array"
        plan["timeline"][0]["dialogue"] = "not an array"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be an array" in item.message for item in report.errors))

    def test_invalid_dialogue_item(self) -> None:
        plan = valid_plan()
        plan["timeline"][1]["dialogue"][0] = "not a dict"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be an object" in item.message for item in report.errors))

    def test_viral_one_take_duration_exceeds_max(self) -> None:
        plan = valid_plan()
        plan["format_profile"]["target_duration_seconds"] = 15
        plan["timeline"][0]["duration_seconds"] = 15
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("one-take duration 15s exceeds model limit 10s" in item.message for item in report.errors))

    def test_invalid_variation_policy_seed(self) -> None:
        plan = valid_plan()
        plan["variation_policy"]["seed"] = "not an int"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be an integer" in item.message for item in report.errors))

    def test_invalid_variation_policy_dimensions(self) -> None:
        plan = valid_plan()
        plan["variation_policy"]["dimensions"] = []
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be a non-empty array" in item.message for item in report.errors))

        plan["variation_policy"]["dimensions"] = [""]
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must contain non-empty strings" in item.message for item in report.errors))

    def test_invalid_variation_policy_shuffle_bag(self) -> None:
        plan = valid_plan()
        plan["variation_policy"]["shuffle_bag"] = "not a bool"
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be a boolean" in item.message for item in report.errors))

    def test_invalid_variation_policy_avoid_recent(self) -> None:
        plan = valid_plan()
        plan["variation_policy"]["avoid_recent"] = -1
        report = STUDIO_LINT.lint(plan, studio_ready=True)
        self.assertTrue(any("must be a non-negative integer" in item.message for item in report.errors))


if __name__ == "__main__":
    unittest.main()
