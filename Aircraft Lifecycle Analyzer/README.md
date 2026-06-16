# AM4user – Aircraft Lifecycle Analyzer (MVP v0.1.0)

## Project Overview
AM4user is a lightweight web dashboard that helps *Airline Manager 4* players evaluate aircraft upgrade decisions. The tool compares the yearly profit, capital cost, fuel consumption, and CO₂ emissions of a current fleet versus a candidate new aircraft on a given route, providing a simple pay‑back period analysis.

The project stabilizes the initially prototyped analysis by removing the unstable `am4` runtime package (which segfaults on `db.init()`) and instead reading the official Parquet datasets directly through a dedicated **Dataset Service** layer.

## Features
- **Aircraft Lifecycle Analyzer**: Input current/target aircraft (by shortname), quantities, route (origin & destination IATA), and utilization assumptions.
- **ROI Comparison**: Yearly profit, additional investment, and pay‑back period.
- **Fuel Analysis**: Fuel consumption per flight for both options (lbs).
- **CO₂ Analysis**: CO₂ emissions per flight for both options (kg).
- **Architecture**: Clean separation of data access, analysis, and UI.
- **Mock‑Data Fallback**: If the Parquet files cannot be read, the UI still works with realistic placeholder data.

## Architecture Diagram (ASCII)
```
Parquet Datasets
   (aircraft.parquet, airports.parquet, route.parquet)
            ↓
Dataset Service (analysis/datasets.py)
   • Lazy loads + caches DataFrames
   • Provides typed getters & fallbacks
            ↓
Analysis Layer (analysis/lifecycle.py)
   • Computes profit, flight time, fuel, CO₂
   • Implements lifecycle_analysis()
            ↓
Streamlit UI (ui/lifecycle_app.py)
   • Interactive form
   • Metrics display (profit, investment, payback, fuel, CO₂)
```

### Why the am4 Runtime Package Is NOT Used
During technical validation, installing `am4==0.1.8a1` led to a segmentation fault in `am4.utils.db.init()` due to incompatibilities between its C‑extension, DuckDB, and PyArrow. To ensure reliability, we treat the Parquet files as the stable source of truth and access them directly with pandas.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AM4user.git
   cd AM4user
   ```
2. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   (`requirements.txt` contains `streamlit>=1.28.0` and `pandas>=2.0.0`; a Parquet engine—`pyarrow` or `fastparquet`—is also required.)

## Quick Start
```bash
# Ensure you are in the project root
streamlit run ui/lifecycle_app.py
```
The app will be available at `http://localhost:8501`.  
Use `--server.headless true` to run without a browser (e.g., on a server).

## Known Limitations
- **Route Data Sparsity**: Not every aircraft‑origin‑destination triplet exists in the route table. The analyzer will show an error if no matching route is found.
- **Mock Data Simplicity**: The fallback mock datasets are minimal and not calibrated to real AM4 economics.
- **No Live API Integration**: The tool does not connect to the airline4.net API; it relies solely on the bundled Parquet datasets.
- **Deferred Features**: Hub analysis, stock‑market simulation, and machine‑learning predictions are planned for future versions.

## Future Roadmap
- **v0.2.0**: Add Hub Analysis (airport utilization, connecting traffic).
- **v0.3.0**: Add Stock Market Analysis (simulated in‑game trading).
- **v0.4.0**: Optional airline4.net API integration (requires API key).
- **v0.5.0**: Machine‑learning upgrade‑recommendation model.
- **Continuous**: Refine profit model if the meaning of the `d` field is clarified.

## License
MIT License – see `LICENSE` file for details.

## Acknowledgments
- The Parquet datasets are sourced from the open‑source `abc8747/am4` Python package.
- Built with Streamlit and pandas.
