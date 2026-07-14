from __future__ import annotations

import tempfile
import unittest

from test_meal_schedule import sample_plan, sample_preferences
from meal_schedule.store import PlanStore


class HistoricalPreferencesTests(unittest.TestCase):
    def test_history_remains_readable_after_preferences_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = PlanStore(directory)
            store.save(sample_plan(), sample_preferences())
            changed = sample_preferences()
            changed["household_size"] = 4
            changed["allergies"] = ["鶏肉"]
            plans = list(store.iter_plans(preferences=changed))
            self.assertEqual(1, len(plans))
            self.assertEqual("テスト献立", plans[0]["title"])


if __name__ == "__main__":
    unittest.main()
