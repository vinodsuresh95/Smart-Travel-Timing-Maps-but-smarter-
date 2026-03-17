# Smart Travel Timing (MVP)

A tiny prototype for your idea: **"leave at the right time so you arrive when the place opens."**

## What it does

Given:
- destination name
- opening time (`HH:MM`, 24-hour format)
- travel duration (minutes)

It returns:
- suggested departure datetime
- expected arrival datetime

## Run

```bash
python smart_travel_timing.py
```

Example input:

```text
Destination: City Mall
Opening time (HH:MM): 10:00
Travel duration in minutes: 35
```

Example output:

```text
Destination: City Mall
Opening time: 2026-01-10 10:00
Travel duration: 35 minutes
Suggested departure: 2026-01-10 09:25
Expected arrival: 2026-01-10 10:00
```

## Run tests

```bash
python -m unittest -v
```

## Next steps toward a real product

- Replace manual travel duration with map API traffic estimates.
- Handle complex opening schedules (multiple windows, weekends, holidays).
- Add user preferences (arrive early, parking buffer, etc.).
- Wrap this logic as a lightweight mobile/web plugin layer.
