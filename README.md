# Namaz Times Tracker

Namaz Times Tracker is a beginner-friendly Python command-line app that fetches live Islamic prayer timings and Hijri dates from the free Aladhan Prayer Times API. It helps users view today's schedule, calculate the next prayer, look up timings by custom coordinates and date, and save favorite schedules locally in `saved_timings.json`.

## Features

- Fetch live prayer times for a city and country
- Look up timings by latitude/longitude and custom date
- Show next prayer countdown based on the current local time
- Display Gregorian and Hijri dates in a readable table
- Save favorite locations or schedules to `saved_timings.json`
- Support different calculation methods and schools

## Setup

1. Open a terminal in the project folder.
2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the environment:

On Windows:

```bash
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

4. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

5. Run the program:

```bash
python main.py
```

## Optional Environment Settings

You can create a `.env` file in the project root to set default values:

```env
DEFAULT_CITY=Karachi
DEFAULT_COUNTRY=Pakistan
DEFAULT_METHOD=1
DEFAULT_SCHOOL=1
```

A sample file is included as `.env.example`.

## Calculation Methods and Schools

- Method values include common choices such as:
  - `1` = University of Islamic Sciences, Karachi
  - `2` = ISNA
  - `3` = Muslim World League
- School values:
  - `0` = Shafi
  - `1` = Hanafi

## Sample Output

```text
=== Namaz Times Tracker ===
1. Today's Namaz Times (City or Coordinates)
2. Next Prayer Countdown
3. Search by Coordinates & Custom Date
4. Save / View Schedules
5. Exit

Location: Karachi, Pakistan
Gregorian Date: 13-11-2026 (Friday)
Hijri Date: 15 Jumada al-Awwal 1448
Timezone: Asia/Karachi
Calculation Method: University of Islamic Sciences, Karachi

Prayer          24h Time    12h Time
--------------------------------------
Fajr            04:58       4:58 AM
Sunrise         06:18       6:18 AM
Dhuhr           12:30       12:30 PM
Asr             15:52       3:52 PM
Maghrib         17:57       5:57 PM
Isha            19:48       7:48 PM

Next prayer: Asr in 1h 16m
```

## Notes

- The app uses the public Aladhan API and requires an internet connection.
- If the city is invalid or the API fails, the app prints a clear error instead of crashing.
- Saved data is stored in `saved_timings.json` in the project root.
