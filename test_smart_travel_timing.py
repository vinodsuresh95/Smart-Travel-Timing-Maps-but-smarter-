from datetime import datetime
import unittest

from smart_travel_timing import next_opening_datetime, suggest_departure_time


class SmartTravelTimingTests(unittest.TestCase):
    def test_opening_today_when_in_future(self):
        now = datetime(2026, 1, 10, 8, 0)
        opening = next_opening_datetime("09:30", now=now)
        self.assertEqual(opening, datetime(2026, 1, 10, 9, 30))

    def test_opening_tomorrow_when_time_passed(self):
        now = datetime(2026, 1, 10, 18, 0)
        opening = next_opening_datetime("09:30", now=now)
        self.assertEqual(opening, datetime(2026, 1, 11, 9, 30))

    def test_departure_recommendation(self):
        now = datetime(2026, 1, 10, 8, 0)
        plan = suggest_departure_time(
            destination="City Mall",
            opening_time="10:00",
            travel_duration_minutes=35,
            now=now,
        )

        self.assertEqual(plan.departure_datetime, datetime(2026, 1, 10, 9, 25))
        self.assertEqual(plan.arrival_datetime, datetime(2026, 1, 10, 10, 0))

    def test_invalid_travel_duration(self):
        with self.assertRaises(ValueError):
            suggest_departure_time("Gym", "07:00", 0)


if __name__ == "__main__":
    unittest.main()
