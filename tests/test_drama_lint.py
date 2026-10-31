from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "drama_lint", ROOT / "scripts" / "drama_lint.py"
)
assert SPEC and SPEC.loader
DRAMA_LINT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DRAMA_LINT
SPEC.loader.exec_module(DRAMA_LINT)


def valid_pack() -> dict:
    return {
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
                "id": "ep_001",
                "hook": "Delivery late",
                "turn": "Gets hit by car",
                "cliffhanger": "Wakes up 5 seconds ago",
                "payoff": "He survives",
                "characters": ["char_01"],
                "locations": ["loc_01"],
                "state_delta": ["Discovers time power"],
                "debts_opened": [
                    {
                        "id": "save_cat",
                        "due_episode": 2
                    }
                ],
                "debts_paid": []
            },
            {
                "id": "ep_002",
                "hook": "Needs to cross street",
                "turn": "Sees cat on road",
                "cliffhanger": "He runs out",
                "payoff": "Saves cat but forgets his name",
                "characters": ["char_01"],
                "locations": ["loc_01"],
                "state_delta": ["Loses his memory"],
                "debts_opened": [],
                "debts_paid": ["save_cat"]
            },
            {
                "id": "ep_003",
                "hook": "Who am I?",
                "turn": "Finds his name tag",
                "cliffhanger": "Meets mysterious stranger",
                "payoff": "Realizes he is a time traveler",
                "characters": ["char_01"],
                "locations": ["loc_01"],
                "state_delta": ["Accepts his fate"],
                "debts_opened": [],
                "debts_paid": []
            }
        ]
    }


class DramaLintTests(unittest.TestCase):
    def test_valid_production_ready_pack(self) -> None:
        report = DRAMA_LINT.lint(valid_pack(), production_ready=True)
        self.assertEqual([], report.errors)

    def test_rejects_non_consecutive_episodes(self) -> None:
        pack = valid_pack()
        pack["episodes"][1]["id"] = "ep_004"
        report = DRAMA_LINT.lint(pack, production_ready=True)
        self.assertTrue(any("episode ids must be consecutive" in item.message for item in report.errors))

    def test_rejects_missing_state_delta(self) -> None:
        pack = valid_pack()
        pack["episodes"][0]["state_delta"] = []
        report = DRAMA_LINT.lint(pack, production_ready=True)
        self.assertTrue(any("must not be empty in --production-ready mode" in item.message for item in report.errors))

    def test_rejects_early_debt_payment(self) -> None:
        pack = valid_pack()
        pack["episodes"][0]["debts_opened"] = []
        pack["episodes"][1]["debts_opened"] = [{"id": "save_cat", "due_episode": 3}]
        pack["episodes"][0]["debts_paid"] = ["save_cat"]
        pack["episodes"][1]["debts_paid"] = []
        report = DRAMA_LINT.lint(pack, production_ready=True)
        self.assertTrue(any("pays debt before it opens in ep_002" in item.message for item in report.errors))

    def test_rejects_unpaid_due_debt_warning(self) -> None:
        pack = valid_pack()
        pack["episodes"][1]["debts_paid"] = []
        report = DRAMA_LINT.lint(pack, production_ready=True)
        self.assertTrue(any("is unpaid in this pack" in item.message for item in report.warnings))

    def test_rejects_missing_visual_anchor_in_production(self) -> None:
        pack = valid_pack()
        del pack["characters"][0]["visual_anchor"]
        report = DRAMA_LINT.lint(pack, production_ready=True)
        self.assertTrue(any("required in --production-ready mode" in item.message for item in report.errors))

    def test_lint_does_not_mutate_input(self) -> None:
        pack = valid_pack()
        original = copy.deepcopy(pack)
        DRAMA_LINT.lint(pack, production_ready=True)
        self.assertEqual(original, pack)


if __name__ == "__main__":
    unittest.main()
