# AM4user Project

## Overview
This project assists in analyzing Aircraft Manager 4 (AM4) game data to support upgrade decisions. It uses the official AM4 data (via the abc8747/am4 Python package) and provides a Streamlit dashboard for evaluating aircraft lifecycle economics.

## Architecture
- **collector/**: Scripts to fetch data from official API (if available) and update local cache.
- **repository/**: Data access layer (SQLite or direct Parquet reads).
- **analysis/**: Business logic, including Aircraft Lifecycle Analyzer.
- **models/**: Internal data models (if any).
- **ui/**: Streamlit web interface.
- **tests/**: Unit and integration tests.
- **docs/**: Documentation, diagrams, and usage guides.

## Key Features
- Account overview (placeholder)
- Financial analysis
- Fuel & CO₂ price trends
- Upgrade recommendations
- Hub analysis
- Stock market analysis (simulated)

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Ensure AM4 data is available (the am4 package includes Parquet files).
3. Run the Streamlit app: `streamlit run ui/lifecycle_app.py`

## Data Sources
- Official AM4 data bundled with the `am4` Python package (Parquet files).
- Optional: Live data from airline4.net API (requires API key).

## Notes
Due to a segmentation fault in the am4 package's database initialization, this version bypasses the am4 DB layer and reads Parquet files directly using pandas.

## Future Work
- Fix am4 segfault or use official API with API key.
- Implement remaining dashboard modules.
- Add authentication and caching.
EOF