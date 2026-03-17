from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Sequence


@dataclass(frozen=True)
class TravelPlan:
    destination: str
    opening_datetime: datetime
    travel_duration_minutes: int
    departure_datetime: datetime
    arrival_datetime: datetime


@dataclass(frozen=True)
class TimeWindowSignal:
    arrival_datetime: datetime
    predicted_travel_minutes: float
    congestion_increase: float
    reliability: float


@dataclass(frozen=True)
class SATRWeights:
    travel_time: float = 1.0
    schedule_deviation: float = 1.0
    promotion_signal: float = 1.0


@dataclass(frozen=True)
class SATRRecommendation:
    destination: str
    preferred_arrival: datetime
    chosen_arrival: datetime
    chosen_departure: datetime
    predicted_travel_minutes: float
    pis_score: float
    satr_score: float


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


def compute_pis(
    congestion_increase: float,
    reliability: float,
    alpha: float = 0.6,
    beta: float = 0.4,
) -> float:
    """Promotion Intensity Signal (PIS), normalized to [-1, 1]."""
    raw_signal = (-alpha * congestion_increase) + (beta * reliability)
    return max(-1.0, min(1.0, raw_signal))


def score_arrival_window(
    signal: TimeWindowSignal,
    preferred_arrival: datetime,
    weights: SATRWeights,
    alpha: float = 0.6,
    beta: float = 0.4,
) -> tuple[float, float]:
    """Return (SATR score, PIS score) for one candidate arrival window."""
    if signal.predicted_travel_minutes <= 0:
        raise ValueError("predicted_travel_minutes must be greater than zero")

    deviation_minutes = abs((signal.arrival_datetime - preferred_arrival).total_seconds()) / 60.0
    pis_value = compute_pis(signal.congestion_increase, signal.reliability, alpha=alpha, beta=beta)

    satr_score = -(
        (weights.travel_time * signal.predicted_travel_minutes)
        + (weights.schedule_deviation * deviation_minutes)
    ) + (weights.promotion_signal * pis_value)

    return satr_score, pis_value


def recommend_arrival_time(
    destination: str,
    preferred_arrival: datetime,
    candidate_windows: Sequence[TimeWindowSignal],
    weights: SATRWeights | None = None,
    alpha: float = 0.6,
    beta: float = 0.4,
) -> SATRRecommendation:
    """Choose the best arrival window using the SATR scoring framework."""
    if not candidate_windows:
        raise ValueError("candidate_windows cannot be empty")

    if weights is None:
        weights = SATRWeights()

    scored: list[tuple[float, TimeWindowSignal, float]] = []
    for signal in candidate_windows:
        score, pis = score_arrival_window(
            signal=signal,
            preferred_arrival=preferred_arrival,
            weights=weights,
            alpha=alpha,
            beta=beta,
        )
        scored.append((score, signal, pis))

    best_score, best_signal, best_pis = max(scored, key=lambda row: row[0])
    departure = best_signal.arrival_datetime - timedelta(minutes=best_signal.predicted_travel_minutes)

    return SATRRecommendation(
        destination=destination,
        preferred_arrival=preferred_arrival,
        chosen_arrival=best_signal.arrival_datetime,
        chosen_departure=departure,
        predicted_travel_minutes=best_signal.predicted_travel_minutes,
        pis_score=best_pis,
        satr_score=best_score,
    )


def build_candidate_windows(
    base_arrival: datetime,
    offsets_minutes: Iterable[int],
    travel_minutes: Iterable[float],
    congestion: Iterable[float],
    reliability: Iterable[float],
) -> list[TimeWindowSignal]:
    """Helper to build candidate windows from parallel lists."""
    offsets = list(offsets_minutes)
    travel = list(travel_minutes)
    congestion_vals = list(congestion)
    reliability_vals = list(reliability)

    if not (len(offsets) == len(travel) == len(congestion_vals) == len(reliability_vals)):
        raise ValueError("all candidate window inputs must have equal length")

    windows: list[TimeWindowSignal] = []
    for i in range(len(offsets)):
        windows.append(
            TimeWindowSignal(
                arrival_datetime=base_arrival + timedelta(minutes=offsets[i]),
                predicted_travel_minutes=travel[i],
                congestion_increase=congestion_vals[i],
                reliability=reliability_vals[i],
            )
        )

    return windows


def format_plan(plan: TravelPlan) -> str:
    return (
        f"Destination: {plan.destination}\n"
        f"Opening time: {plan.opening_datetime:%Y-%m-%d %H:%M}\n"
        f"Travel duration: {plan.travel_duration_minutes} minutes\n"
        f"Suggested departure: {plan.departure_datetime:%Y-%m-%d %H:%M}\n"
        f"Expected arrival: {plan.arrival_datetime:%Y-%m-%d %H:%M}"
    )


def format_satr_recommendation(reco: SATRRecommendation) -> str:
    return (
        f"Destination: {reco.destination}\n"
        f"Preferred arrival: {reco.preferred_arrival:%Y-%m-%d %H:%M}\n"
        f"Recommended arrival: {reco.chosen_arrival:%Y-%m-%d %H:%M}\n"
        f"Recommended departure: {reco.chosen_departure:%Y-%m-%d %H:%M}\n"
        f"Predicted travel time: {reco.predicted_travel_minutes:.1f} minutes\n"
        f"PIS score: {reco.pis_score:.3f}\n"
        f"SATR score: {reco.satr_score:.3f}"
    )


if __name__ == "__main__":
    destination = input("Destination: ").strip()
    preferred_arrival = datetime.strptime(
        input("Preferred arrival (YYYY-MM-DD HH:MM): ").strip(), "%Y-%m-%d %H:%M"
    )

    print("\nEnter three candidate windows as travel,congestion,reliability")
    print("Example: 28,0.2,0.9")
    candidates: list[TimeWindowSignal] = []
    for idx in range(3):
        row = input(f"Candidate {idx + 1}: ").strip()
        travel, congestion, reliability = [float(part) for part in row.split(",")]
        arrival = preferred_arrival + timedelta(minutes=(idx - 1) * 15)
        candidates.append(
            TimeWindowSignal(
                arrival_datetime=arrival,
                predicted_travel_minutes=travel,
                congestion_increase=congestion,
                reliability=reliability,
            )
        )

    recommendation = recommend_arrival_time(
        destination=destination,
        preferred_arrival=preferred_arrival,
        candidate_windows=candidates,
    )

    print()
    print(format_satr_recommendation(recommendation))
