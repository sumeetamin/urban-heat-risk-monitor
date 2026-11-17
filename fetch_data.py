"""Fetch a small reproducible ERA5 reanalysis sample via Open-Meteo."""
import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd


LOCATIONS = {
    "Chicago": (41.8781, -87.6298),
    "Houston": (29.7604, -95.3698),
    "Miami": (25.7617, -80.1918),
    "New York": (40.7128, -74.0060),
    "Phoenix": (33.4484, -112.0740),
}


def main():
    rows = []
    for name, (latitude, longitude) in LOCATIONS.items():
        query = urlencode({
            "latitude": latitude,
            "longitude": longitude,
            "start_date": "1991-01-01",
            "end_date": "2020-12-31",
            "daily": "temperature_2m_max",
            "timezone": "UTC",
        })
        with urlopen("https://archive-api.open-meteo.com/v1/archive?" + query, timeout=60) as response:
            payload = json.load(response)
        daily = payload["daily"]
        rows.extend({"date": date, "location": name, "tmax_c": value} for date, value in zip(daily["time"], daily["temperature_2m_max"]))
        time.sleep(1)
    output = Path("data/openmeteo_era5_daily_tmax.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"Wrote {len(rows):,} daily rows to {output}")


if __name__ == "__main__":
    main()
