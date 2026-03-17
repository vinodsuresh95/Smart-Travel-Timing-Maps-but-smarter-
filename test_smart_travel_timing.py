from datetime import datetime
import unittest

from smart_travel_timing import (
    SATRWeights,
    build_candidate_windows,
    compute_pis,
    next_opening_datetime,
    recommend_arrival_time,
    suggest_departure_time,
)


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

    def test_compute_pis_clamps_to_range(self):
        self.assertEqual(compute_pis(congestion_increase=10, reliability=10), -1.0)
        self.assertEqual(compute_pis(congestion_increase=-10, reliability=10), 1.0)

    def test_recommend_arrival_time_chooses_best_window(self):
        preferred = datetime(2026, 1, 10, 9, 0)
        windows = build_candidate_windows(
            base_arrival=preferred,
            offsets_minutes=[-15, 0, 15],
            travel_minutes=[20, 30, 24],
            congestion=[0.9, 0.95, 0.1],
            reliability=[0.4, 0.5, 0.9],
        )

        recommendation = recommend_arrival_time(
            destination="Office",
            preferred_arrival=preferred,
            candidate_windows=windows,
            weights=SATRWeights(travel_time=1.0, schedule_deviation=0.3, promotion_signal=8.0),
        )

        self.assertEqual(recommendation.chosen_arrival, datetime(2026, 1, 10, 9, 15))
        self.assertEqual(recommendation.chosen_departure, datetime(2026, 1, 10, 8, 51))

    def test_recommend_arrival_time_requires_candidates(self):
        with self.assertRaises(ValueError):
            recommend_arrival_time("Office", datetime(2026, 1, 10, 9, 0), [])


if __name__ == "__main__":
    unittest.main()
