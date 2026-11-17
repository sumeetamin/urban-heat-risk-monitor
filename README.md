# Urban Heat Risk Monitor

A city-level historical heat exposure monitor with a frozen reference period. It estimates a local high-temperature threshold, then summarizes later heat days and three-day runs.

## Data and reproducibility

The benchmark uses Open-Meteo's Historical Weather API with ERA5 daily maximum 2 m temperature for five US city grid points (Chicago, Houston, Miami, New York, Phoenix), 1991–2020. Open-Meteo documents ERA5 reanalysis as gridded historical weather and licenses its API data under CC BY 4.0; attribution is required. This CSV snapshot has SHA-256 \`49ef3e44f7a1efcbd0c9cb760c977f8e02e7d785880b677c94c27c6de97ab783\`.

\`\`\`bash
python -m pip install -r requirements.txt
python fetch_data.py
python main.py --input data/openmeteo_era5_daily_tmax.csv --baseline-end 2010-12-31 --percentile 0.95 --out outputs
\`\`\`

## Holdout summary

Each city's 95th-percentile daily maximum temperature is estimated on 1991–2010 and held fixed for 2011–2020. Across 18,265 later city-days, 1,252 (6.85%) reached or exceeded their local baseline threshold; 571 observations marked the end of a run of at least three consecutive threshold days. Full aggregate metrics are in [\`outputs/benchmark.json\`](outputs/benchmark.json) locally and the published aggregate copy in [\`reports/benchmark.json\`](reports/benchmark.json).

These are relative exposure summaries, not evidence of individual health risk. ERA5 grid estimates are not local station observations and do not account for humidity, neighborhood variation, housing, vulnerability, cooling access, or official warnings. Do not use as an emergency or medical alert.
