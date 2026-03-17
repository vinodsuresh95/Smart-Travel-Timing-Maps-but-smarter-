from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class TravelPlan:
    destination: str
    opening_datetime: datetime
    travel_duration_minutes: int
    departure_datetime: datetime
    arrival_datetime: datetime


def next_opening_datetime(opening_time: str, now: datetime | None = None) -> datetime:
    """Return the next datetime the destination opens based on an HH:MM 24-hour opening time."""
    if now is None:
        now = datetime.now()

    opening_today = datetime.strptime(opening_time, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )

    if opening_today >= now:
        return opening_today

    return opening_today + timedelta(days=1)


def suggest_departure_time(
    destination: str,
    opening_time: str,
    travel_duration_minutes: int,
    now: datetime | None = None,
) -> TravelPlan:
    """Create a simple departure recommendation so arrival matches opening time."""
    if travel_duration_minutes <= 0:
        raise ValueError("travel_duration_minutes must be greater than zero")

    opening_dt = next_opening_datetime(opening_time, now=now)
    departure_dt = opening_dt - timedelta(minutes=travel_duration_minutes)

    return TravelPlan(
        destination=destination,
        opening_datetime=opening_dt,
        travel_duration_minutes=travel_duration_minutes,
        departure_datetime=departure_dt,
        arrival_datetime=departure_dt + timedelta(minutes=travel_duration_minutes),
    )


def format_plan(plan: TravelPlan) -> str:
    return (
        f"Destination: {plan.destination}\n"
        f"Opening time: {plan.opening_datetime:%Y-%m-%d %H:%M}\n"
        f"Travel duration: {plan.travel_duration_minutes} minutes\n"
        f"Suggested departure: {plan.departure_datetime:%Y-%m-%d %H:%M}\n"
        f"Expected arrival: {plan.arrival_datetime:%Y-%m-%d %H:%M}"
    )


if __name__ == "__main__":
    destination = input("Destination: ").strip()
    opening_time = input("Opening time (HH:MM): ").strip()
    travel_duration_minutes = int(input("Travel duration in minutes: ").strip())

    recommendation = suggest_departure_time(
        destination=destination,
        opening_time=opening_time,
        travel_duration_minutes=travel_duration_minutes,
    )

    print()
    print(format_plan(recommendation))
