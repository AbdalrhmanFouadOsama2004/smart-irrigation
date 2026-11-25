import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from rules import evaluate, validate


def reading(**changes):
    base = {"field_id": "field-1", "crop": "wheat", "soil_moisture": 45,
            "temperature_c": 25, "timestamp": "2026-01-01T00:00:00+00:00"}
    return {**base, **changes}


class RulesTest(unittest.TestCase):
    def status(self, **changes):
        return evaluate(validate(reading(**changes)))[0]

    def test_statuses(self):
        self.assertEqual(self.status(), "OK")
        self.assertEqual(self.status(soil_moisture=20), "IRRIGATE")
        self.assertEqual(self.status(soil_moisture=80), "TOO_WET")
        self.assertEqual(self.status(temperature_c=40), "HEAT_STRESS")

    def test_boundaries_are_ok(self):
        self.assertEqual(self.status(soil_moisture=30), "OK")
        self.assertEqual(self.status(soil_moisture=60), "OK")

    def test_dry_and_hot_gives_two_messages(self):
        status, advice = evaluate(validate(reading(soil_moisture=10, temperature_c=41)))
        self.assertEqual((status, len(advice)), ("IRRIGATE", 2))

    def test_invalid_readings(self):
        for bad in ({"crop": "banana"}, {"soil_moisture": 120},
                    {"soil_moisture": "wet"}, {"temperature_c": None}):
            with self.assertRaises(ValueError):
                validate(reading(**bad))
        with self.assertRaises(ValueError):
            validate({})


if __name__ == "__main__":
    unittest.main()
