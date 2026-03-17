# Smart Travel Timing (SATR MVP)

This project now implements a stronger prototype of your original idea using the **Smart Arrival Time Recommendation (SATR)** approach.

## Is this the same thing we built before?

**Partly.**

- Before: a basic calculator that said, “if opening is 10:00 and travel is 35 min, leave at 9:25.”
- Now: a scoring-based recommender that compares multiple candidate arrival windows and picks the best one by balancing:
  - predicted travel time,
  - schedule deviation from the user’s preferred arrival,
  - network desirability via **Promotion Intensity Signal (PIS)**.

So this version is much closer to your paper’s methodology (Section 3.2 and 3.3 style logic).

## Core model

For each candidate arrival time, we compute:

- `PIS = -alpha * congestion_increase + beta * reliability`, clamped to `[-1, 1]`
- `SATR score = -(w1 * travel_time + w2 * schedule_deviation) + w3 * PIS`

The selected recommendation is the candidate with maximum SATR score.

## Run the CLI demo

```bash
python smart_travel_timing.py
```

You will provide:

- destination
- preferred arrival datetime
- three candidate windows in `travel,congestion,reliability` format

The script outputs recommended arrival/departure plus PIS and total SATR score.

## Run tests

```bash
python -m unittest -v
```

## Next steps

- Pull candidate windows from map APIs (historical + real-time ETA).
- Add route choice alongside time choice.
- Calibrate user-specific weights automatically.
- Add compliance simulation to estimate network-level delay reduction.
