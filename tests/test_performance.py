import time
import unittest
from scripts.drama_lint import lint as drama_lint_func
from scripts.studio_lint import lint as studio_lint_func

def gen_large_drama_pack(num_episodes=5000):
    return {
        "project": {
            "title": "My Drama",
            "market": "Global",
            "format": "vertical",
            "episode_duration_seconds": 60.0,
            "planned_episodes": num_episodes,
        },
        "premise_contract": {
            "public_identity": "Delivery guy",
            "hidden_truth": "Time traveler",
            "engine": "Reversing time 5 seconds",
            "season_question": "Can he save her?",
            "fresh_twist": "He loses memories when reversing time",
        },
        "characters": [
            {
                "id": "char_01",
                "name": "Delivery Guy",
                "public_identity": "A poor guy",
                "hidden_truth": "A god of time",
                "visual_anchor": "design document v1",
                "voice_anchor": "voice actor sample 1"
            }
        ],
        "locations": [
            {
                "id": "loc_01",
                "name": "City street",
                "visual_anchor": "concept art"
            }
        ],
        "episodes": [
            {
                "id": f"ep_{i:03d}",
                "hook": "Delivery late",
                "turn": "Gets hit by car",
                "cliffhanger": "Wakes up 5 seconds ago",
                "payoff": "He survives",
                "characters": ["char_01"],
                "locations": ["loc_01"],
                "state_delta": ["Discovers time power"],
                "debts_opened": [],
                "debts_paid": []
            } for i in range(1, num_episodes + 1)
        ]
    }

def gen_large_studio_plan(num_timeline=5000):
    return {
        "format_profile": {
            "id": "serial_episode",
            "story_scope": "episode",
            "shot_strategy": "timeline",
            "dominant_turn": "reversal",
            "target_duration_seconds": num_timeline * 5.0
        },
        "model_capability": {
            "model_id": "gen-x-fast",
            "status": "verified",
            "verified_at": "2024-05-15T12:00:00Z",
            "max_duration_seconds": 10.0,
            "max_reference_assets": 5,
            "supported_reference_types": ["image", "video"],
            "evidence": "Internal CI test pass"
        },
        "global_settings": {
            "aspect_ratio": "9:16",
            "visual_style": "cinematic_realism",
            "lighting": "neon_noir",
            "color_tone": "cool_blue",
            "language": "en",
            "audio_baseline": "ambient_city"
        },
        "assets": [
            {
                "id": "char_01",
                "kind": "character",
                "name": "Alex",
                "recurrence": "recurring",
                "visual_anchor": "S3 bucket URL",
                "reference_files": ["alex_front.jpg"],
                "identity_views": ["front_closeup", "front_full", "side_full"],
                "voice_anchor": "elevenlabs_id_xyz",
                "consent_status": "verified"
            },
            {
                "id": "loc_01",
                "kind": "location",
                "name": "Alley",
                "recurrence": "one_off",
                "reference_files": []
            }
        ],
        "timeline": [
            {
                "id": f"shot_{i:03d}",
                "start_seconds": i * 5.0,
                "duration_seconds": 5.0,
                "shot_size": "medium",
                "camera_move": "pan_right",
                "angle": "eye_level",
                "location_id": "loc_01",
                "entity_ids": ["char_01"],
                "emotion": "suspicious",
                "transition": "cut",
                "observable_action": "Alex looks around",
                "sound": "footsteps",
                "dialogue": [
                    {
                        "speaker_id": "char_01",
                        "text": "Who's there?",
                        "performance": "whispered"
                    }
                ]
            } for i in range(num_timeline)
        ],
        "variation_policy": {
            "seed": 42,
            "dimensions": ["lighting_intensity", "camera_speed"],
            "shuffle_bag": True,
            "avoid_recent": 2
        },
        "outputs": {
            "prompt_mode": "shot_by_shot",
            "draft_path": "out/draft_01",
            "asset_inbox": "inbox/ep_01",
            "editor_handoff": "handoff.xml"
        }
    }

class PerformanceTests(unittest.TestCase):
    def test_drama_lint_performance(self):
        pack = gen_large_drama_pack(5000)
        start = time.perf_counter()
        report = drama_lint_func(pack, production_ready=True)
        duration = time.perf_counter() - start

        self.assertEqual(len(report.errors), 0, f"Expected 0 errors, got {len(report.errors)}")
        self.assertLess(duration, 2.0, f"drama_lint took {duration:.2f}s, exceeding 2.0s limit")

    def test_studio_lint_performance(self):
        plan = gen_large_studio_plan(5000)
        start = time.perf_counter()
        report = studio_lint_func(plan, studio_ready=True)
        duration = time.perf_counter() - start

        self.assertEqual(len(report.errors), 0, f"Expected 0 errors, got {len(report.errors)}")
        self.assertLess(duration, 2.0, f"studio_lint took {duration:.2f}s, exceeding 2.0s limit")

if __name__ == '__main__':
    unittest.main()
