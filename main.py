"""Interactive CLI for viewing live Namaz timings and countdowns."""

from __future__ import annotations

import os
from datetime import datetime

from dotenv import load_dotenv

from api_client import fetch_timings_by_city, fetch_timings_by_coords
from storage import load_saved_timings, save_timing_record

load_dotenv()

PRAYER_ORDER = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]


def _to_12_hour_clock(time_value: str) -> str:
    """Convert HH:MM time strings into AM/PM format."""
    try:
        hour_str, minute_str = time_value.split(":")
        hour = int(hour_str)
        minute = int(minute_str)
        suffix = "AM" if hour < 12 else "PM"
        normalized_hour = hour % 12
        if normalized_hour == 0:
            normalized_hour = 12
        return f"{normalized_hour}:{minute:02d} {suffix}"
    except (ValueError, AttributeError):
        return "N/A"


def _time_to_minutes(time_value: str) -> int:
    """Convert an HH:MM string to minutes since midnight."""
    try:
        hour_str, minute_str = time_value.split(":")
        return int(hour_str) * 60 + int(minute_str)
    except (ValueError, AttributeError):
        return 24 * 60


def display_timings_table(data: dict, location_label: str) -> None:
    """Display a formatted prayer table with Gregorian and Hijri dates."""
    timings = data.get("timings", {})
    date_info = data.get("date", {})
    gregorian = date_info.get("gregorian", {})
    hijri = date_info.get("hijri", {})
    meta = data.get("meta", {})
    method_info = meta.get("method", {})

    print("\n=== Namaz Timings ===")
    print(f"Location: {location_label}")
    print(f"Gregorian Date: {gregorian.get('date', 'N/A')} ({gregorian.get('weekday', {}).get('en', 'N/A')})")
    print(f"Hijri Date: {hijri.get('date', 'N/A')} ({hijri.get('day', 'N/A')})")
    print(f"Timezone: {meta.get('timezone', 'N/A')}")
    print(f"Calculation Method: {method_info.get('name', 'N/A')}")

    print("\nPrayer          24h Time    12h Time")
    print("--------------------------------------")
    for prayer in PRAYER_ORDER:
        prayer_time = timings.get(prayer, "N/A")
        print(f"{prayer:<14} {prayer_time:<10} {_to_12_hour_clock(prayer_time)}")


def get_next_prayer(timings: dict) -> tuple[str, str]:
    """Return the next prayer and the time remaining until it begins."""
    now = datetime.now()
    now_minutes = now.hour * 60 + now.minute

    upcoming_prayer = None
    remaining_minutes = None

    for prayer in PRAYER_ORDER:
        prayer_time = timings.get(prayer, "00:00")
        prayer_minutes = _time_to_minutes(prayer_time)
        if prayer_minutes >= now_minutes:
            upcoming_prayer = prayer
            remaining_minutes = prayer_minutes - now_minutes
            break

    if upcoming_prayer is None:
        next_day_fajr = _time_to_minutes(timings.get("Fajr", "00:00"))
        upcoming_prayer = "Fajr"
        remaining_minutes = (24 * 60 - now_minutes) + next_day_fajr

    hours = remaining_minutes // 60
    minutes = remaining_minutes % 60
    return upcoming_prayer, f"{hours}h {minutes}m"


def ask_for_city_schedule() -> dict | None:
    """Prompt the user to fetch timings by city or country."""
    city = input("City (default Karachi): ").strip() or os.getenv("DEFAULT_CITY", "Karachi")
    country = input("Country (default Pakistan): ").strip() or os.getenv("DEFAULT_COUNTRY", "Pakistan")
    date_input = input("Date (DD-MM-YYYY, blank for today): ").strip()
    method = input("Method (default 1): ").strip() or os.getenv("DEFAULT_METHOD", "1")
    school = input("School (0=Shafi, 1=Hanafi, default 1): ").strip() or os.getenv("DEFAULT_SCHOOL", "1")

    try:
        method_value = int(method)
        school_value = int(school)
    except ValueError:
        print("Invalid method or school input. Falling back to defaults.")
        method_value = int(os.getenv("DEFAULT_METHOD", "1"))
        school_value = int(os.getenv("DEFAULT_SCHOOL", "1"))

    data = fetch_timings_by_city(city, country, date_input, method_value, school_value)
    if not data:
        print("Unable to fetch city timings. Please check your city/country or network connection.")
        return None

    display_timings_table(data, f"{city}, {country}")
    return data


def ask_for_coordinate_schedule() -> dict | None:
    """Prompt the user to fetch timings by coordinates and custom date."""
    try:
        latitude = float(input("Latitude: ").strip())
        longitude = float(input("Longitude: ").strip())
        date_input = input("Date (DD-MM-YYYY, blank for today): ").strip()
        method = int(input("Method (default 3): ").strip() or "3")
        school = int(input("School (0=Shafi, 1=Hanafi, default 0): ").strip() or "0")
    except ValueError:
        print("Invalid coordinate or numeric input.")
        return None

    data = fetch_timings_by_coords(latitude, longitude, date_input, method, school)
    if not data:
        print("Unable to fetch coordinate timings. Please check the coordinates or network connection.")
        return None

    display_timings_table(data, f"Coordinates: {latitude}, {longitude}")
    return data


def save_current_schedule(data: dict | None) -> None:
    """Save a fetched prayer schedule into the local JSON file."""
    if not data:
        print("No schedule available to save yet.")
        return

    timings = data.get("timings", {})
    date_info = data.get("date", {})
    location = input("Location label for this saved record: ").strip() or "Saved Timings"

    record = {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "location": location,
        "date": date_info.get("gregorian", {}).get("date", "N/A"),
        "timings": timings,
    }
    save_timing_record(record)
    print(f"Schedule saved to saved_timings.json under '{location}'.")


def view_saved_schedules() -> None:
    """Display saved prayer records from the JSON file."""
    records = load_saved_timings()
    if not records:
        print("No saved schedules found.")
        return

    print("\nSaved Namaz Schedules:")
    for index, item in enumerate(records, start=1):
        location = item.get("location", "Unknown")
        saved_date = item.get("date", "N/A")
        saved_at = item.get("saved_at", "N/A")
        print(f"{index}. {location} | Date: {saved_date} | Saved: {saved_at}")
        timings = item.get("timings", {})
        for prayer in PRAYER_ORDER:
            print(f"   {prayer}: {timings.get(prayer, 'N/A')}")
        print()


def main_menu() -> None:
    """Display and manage the interactive menu options."""
    last_data = None

    while True:
        print("\n=== Namaz Times Tracker ===")
        print("1. Today's Namaz Times (City or Coordinates)")
        print("2. Next Prayer Countdown")
        print("3. Search by Coordinates & Custom Date")
        print("4. Save / View Schedules")
        print("5. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            lookup_type = input("Lookup by city or coordinates? [city/coords]: ").strip().lower()
            if lookup_type in {"coords", "coordinate", "coordinates"}:
                last_data = ask_for_coordinate_schedule()
            else:
                last_data = ask_for_city_schedule()

        elif choice == "2":
            if last_data is None:
                print("No timings loaded yet. Fetching default city timings...")
                last_data = ask_for_city_schedule()
            if not last_data:
                continue
            prayer_name, remaining = get_next_prayer(last_data.get("timings", {}))
            print(f"Next prayer: {prayer_name} in {remaining}")

        elif choice == "3":
            last_data = ask_for_coordinate_schedule()

        elif choice == "4":
            sub_choice = input("1) Save current schedule  2) View saved schedules  3) Back: ").strip()
            if sub_choice == "1":
                save_current_schedule(last_data)
            elif sub_choice == "2":
                view_saved_schedules()
            else:
                continue

        elif choice == "5":
            print("Assalamu Alaikum! Goodbye.")
            break

        else:
            print("Please enter a valid option from 1 to 5.")


if __name__ == "__main__":
    main_menu()
