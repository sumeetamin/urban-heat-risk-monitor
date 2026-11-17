"""Evaluate relative hot-day exposure against a frozen city baseline."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--date", default="date")
    parser.add_argument("--location", default="location")
    parser.add_argument("--tmax", default="tmax_c")
    parser.add_argument("--baseline-end", default="2010-12-31")
    parser.add_argument("--percentile", type=float, default=0.95)
    parser.add_argument("--out", default="outputs")
    args = parser.parse_args()

    source = Path(args.input)
    data = pd.read_csv(source)
    data[args.date] = pd.to_datetime(data[args.date], errors="coerce")
    data[args.tmax] = pd.to_numeric(data[args.tmax], errors="coerce")
    data = data.dropna(subset=[args.date, args.location, args.tmax]).sort_values(args.date)
    cutoff = pd.Timestamp(args.baseline_end)
    reference = data[data[args.date] <= cutoff]
    evaluation = data[data[args.date] > cutoff].copy()
    if reference.empty or evaluation.empty:
        raise SystemExit("Input must contain observations both before and after --baseline-end.")

    threshold = reference.groupby(args.location)[args.tmax].quantile(args.percentile)
    evaluation["local_threshold_c"] = evaluation[args.location].map(threshold)
    evaluation = evaluation.dropna(subset=["local_threshold_c"])
    evaluation["heat_day"] = evaluation[args.tmax] >= evaluation["local_threshold_c"]
    evaluation["three_day_heatwave_end"] = evaluation.groupby(args.location)["heat_day"].transform(
        lambda values: values.astype(int).rolling(3, min_periods=3).sum().eq(3)
    )
    evaluation["month"] = evaluation[args.date].dt.to_period("M").astype(str)
    monthly = evaluation.groupby([args.location, "month"]).agg(
        heat_days=("heat_day", "sum"),
        three_day_heatwave_ends=("three_day_heatwave_end", "sum"),
        max_tmax_c=(args.tmax, "max"),
        baseline_threshold_c=("local_threshold_c", "first"),
    ).reset_index()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(out / "monthly_heat_exposure.csv", index=False)
    report = {
        "dataset": "Open-Meteo Historical Weather API, ERA5 daily maximum temperature",
        "source_url": "https://open-meteo.com/en/docs/historical-weather-api",
        "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "records": int(len(data)),
        "locations": int(data[args.location].nunique()),
        "date_range": [data[args.date].min().date().isoformat(), data[args.date].max().date().isoformat()],
        "baseline_end": cutoff.date().isoformat(),
        "evaluation_start": evaluation[args.date].min().date().isoformat(),
        "evaluation_end": evaluation[args.date].max().date().isoformat(),
        "baseline_percentile": args.percentile,
        "evaluation_days": int(len(evaluation)),
        "relative_heat_days": int(evaluation["heat_day"].sum()),
        "relative_heat_day_rate": float(evaluation["heat_day"].mean()),
        "three_day_heatwave_ends": int(evaluation["three_day_heatwave_end"].sum()),
        "mean_city_threshold_c": float(threshold.mean()),
        "method": "Per-location 95th-percentile daily maximum temperature fitted on 1991-2010; fixed threshold evaluated on 2011-2020; heatwave end requires three consecutive days at/above threshold.",
        "limitations": "ERA5 is gridded reanalysis, not a local station observation. Relative historical heat exposure is not an individual health-risk estimate; humidity, built environment, vulnerability, cooling access, and official warnings are not modeled.",
    }
    (out / "benchmark.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
