from __future__ import annotations

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from meal_schedule.cli import run
from meal_schedule.models import ValidationError, validate_plan, validate_preferences
from meal_schedule.render import render_plan_markdown
from meal_schedule.shopping import build_shopping_list
from meal_schedule.store import PlanStore


def sample_preferences() -> dict:
    return {
        "schema_version": 1,
        "household_size": 2,
        "meals": ["夕食"],
        "allergies": [],
        "dislikes": [],
        "week_starts_on": "monday",
    }


def sample_plan() -> dict:
    return {
        "schema_version": 1,
        "title": "テスト献立",
        "start_date": "2026-07-13",
        "end_date": "2026-07-14",
        "servings": 2,
        "meals": [
            {
                "date": "2026-07-13",
                "meal_type": "夕食",
                "dishes": [
                    {
                        "name": "鶏肉となすの炒め物",
                        "servings": 2,
                        "ingredients": [
                            {"name": "鶏肉", "quantity": 300, "unit": "g", "category": "肉"},
                            {"name": "なす", "quantity": 2, "unit": "本", "category": "野菜"},
                        ],
                        "steps": ["材料を切る。", "火が通るまで炒める。"],
                    }
                ],
            },
            {
                "date": "2026-07-14",
                "meal_type": "夕食",
                "dishes": [
                    {
                        "name": "鮭となすの蒸し物",
                        "servings": 2,
                        "ingredients": [
                            {"name": "鮭", "quantity": 2, "unit": "切れ", "category": "魚"},
                            {"name": "なす", "quantity": 1, "unit": "本", "category": "野菜"},
                            {"name": "塩", "quantity": "少々", "unit": "", "category": "調味料"},
                        ],
                        "steps": ["材料を包む。", "12分蒸す。"],
                    }
                ],
            },
        ],
    }


class ValidationTests(unittest.TestCase):
    def test_valid_plan_and_preferences(self) -> None:
        validate_preferences(sample_preferences())
        validate_plan(sample_plan(), sample_preferences())

    def test_rejects_missing_day(self) -> None:
        plan = sample_plan()
        plan["meals"].pop()
        with self.assertRaisesRegex(ValidationError, "献立がない日付"):
            validate_plan(plan)

    def test_rejects_serving_mismatch(self) -> None:
        plan = sample_plan()
        plan["meals"][0]["dishes"][0]["servings"] = 1
        with self.assertRaisesRegex(ValidationError, "servings"):
            validate_plan(plan)

    def test_rejects_forbidden_ingredient(self) -> None:
        preferences = sample_preferences()
        preferences["allergies"] = ["鮭"]
        with self.assertRaisesRegex(ValidationError, "禁止食材.*鮭"):
            validate_plan(sample_plan(), preferences)

    def test_rejects_invalid_json_shape(self) -> None:
        with self.assertRaisesRegex(ValidationError, "オブジェクト"):
            validate_plan([])


class ShoppingAndRenderTests(unittest.TestCase):
    def test_aggregates_same_ingredient_and_preserves_sources(self) -> None:
        items = build_shopping_list(sample_plan())
        eggplant = next(item for item in items if item["name"] == "なす")
        self.assertEqual("3", eggplant["quantity"])
        self.assertEqual(2, len(eggplant["sources"]))

    def test_renders_recipes_steps_and_shopping_list(self) -> None:
        markdown = render_plan_markdown(sample_plan())
        self.assertIn("### 鶏肉となすの炒め物", markdown)
        self.assertIn("1. 材料を切る。", markdown)
        self.assertIn("## 買い物リスト", markdown)
        self.assertIn("- [ ] なす: 3本", markdown)


class StoreAndCliTests(unittest.TestCase):
    def test_save_then_find_by_overlapping_period(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = PlanStore(directory)
            destination = store.save(sample_plan(), sample_preferences())
            self.assertTrue(destination.exists())
            found = list(
                store.iter_plans(
                    start=__import__("datetime").date(2026, 7, 14),
                    end=__import__("datetime").date(2026, 7, 14),
                    preferences=sample_preferences(),
                )
            )
            self.assertEqual(1, len(found))

    def test_does_not_overwrite_without_explicit_flag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = PlanStore(directory)
            store.save(sample_plan())
            with self.assertRaisesRegex(ValidationError, "--overwrite"):
                store.save(sample_plan())

    def test_corrupt_history_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "2026-07-13.json"
            path.write_text("not json", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "読み込めません"):
                list(PlanStore(directory).iter_plans())

    def test_cli_validate_save_show_and_recent_dishes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan_path = root / "proposal.json"
            preferences_path = root / "preferences.json"
            data_dir = root / "plans"
            plan_path.write_text(json.dumps(sample_plan(), ensure_ascii=False), encoding="utf-8")
            preferences_path.write_text(
                json.dumps(sample_preferences(), ensure_ascii=False), encoding="utf-8"
            )
            common = ["--data-dir", str(data_dir), "--preferences", str(preferences_path)]
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(0, run([*common, "validate", str(plan_path)]))
                self.assertEqual(0, run([*common, "save", str(plan_path)]))
                self.assertEqual(
                    0,
                    run(
                        [
                            *common,
                            "show",
                            "--from",
                            "2026-07-14",
                            "--to",
                            "2026-07-14",
                        ]
                    ),
                )
                self.assertEqual(
                    0,
                    run(
                        [
                            *common,
                            "recent-dishes",
                            "--days",
                            "28",
                            "--as-of",
                            "2026-07-14",
                        ]
                    ),
                )
            text = output.getvalue()
            self.assertIn("献立は有効です", text)
            self.assertIn("## 買い物リスト", text)
            self.assertIn("鶏肉となすの炒め物", text)

    def test_cli_returns_actionable_error_for_bad_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            invalid = copy.deepcopy(sample_plan())
            invalid["meals"] = []
            path.write_text(json.dumps(invalid, ensure_ascii=False), encoding="utf-8")
            error = io.StringIO()
            with redirect_stderr(error):
                self.assertEqual(2, run(["validate", str(path)]))
            self.assertIn("1件以上必要", error.getvalue())

    def test_show_reports_when_no_history_exists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(0, run(["--data-dir", directory, "show"]))
            self.assertEqual("指定期間の献立はありません\n", output.getvalue())


if __name__ == "__main__":
    unittest.main()
