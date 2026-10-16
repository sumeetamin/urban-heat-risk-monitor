# Urban Heat Risk Monitor

Summarize unusually hot days by location against a transparent local historical percentile baseline.

> **Portfolio prototype.** Source code is provided; no benchmark results are claimed until you run it on the cited data and record the output.

## Use case

Summarize unusually hot days by location against a transparent local historical percentile baseline. The CLI consumes local files, emits reproducible reports, and keeps data out of the repository.

## Data and provenance

[NOAA NCEI Daily Summaries (token may be required)](https://www.ncei.noaa.gov/cdo-web/datasets). A joined daily-weather and location CSV with date, location, and maximum temperature in Celsius. Use a declared historical baseline in operational work. Source files are not bundled. Respect source terms and cite the dataset when publishing results.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Download/prepare the source data locally, then run:
python main.py --input data/daily_weather.csv --date date --location county --tmax tmax_c --out outputs
```

## Outputs

Generated results are saved under `outputs/`; file names and metrics are printed or documented by the CLI. The repository excludes downloaded data and artifacts.

## Evaluation and operating notes

The prototype compares locations with their own temperature history; it does not estimate individual health risk or account for humidity, housing, age, or access to cooling.

For production use, add a frozen reference period, out-of-time evaluation, monitoring ownership, and a documented rollback or escalation path. This project is a local baseline, not a deployed service.

## License

No code license file is included yet. Third-party data remains subject to its source terms.
