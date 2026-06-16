# Architecture Overview

## Current Architecture

```
Parquet Datasets (aircraft.parquet, airports.parquet, route.parquet)
          ↓
Dataset Service Layer (analysis/datasets.py)
          ↓
Analysis Layer (analysis/lifecycle.py, etc.)
          ↓
Streamlit UI (ui/lifecycle_app.py)
```

### Data Sources
The official AM4 datasets are distributed as Parquet files within the `am4` Python package.
These files contain the core entities:
- **aircraft.parquet**: aircraft specifications (cost, fuel, speed, etc.)
- **airports.parquet**: airport locations and attributes
- **route.parquet**: route performance metric `d` (interpreted as profit per flight)

### Dataset Service Layer
A singleton service (`DatasetService`) provides a unified, cached interface to the datasets.
Features:
- Lazy loading of Parquet files
- In‑memory caching of `DataFrame` objects
- Graceful fallback to mock data if files are missing or unreadable
- Methods to query by ID, name, IATA code, and to filter routes

The service guarantees that **no analysis module reads Parquet files directly**; all data access goes through the service.

### Analysis Layer
Contains domain‑specific business logic, currently:
- **Aircraft Lifecycle Analyzer** (`analysis/lifecycle.py`): computes profit, fuel, CO₂, and payback period for fleet upgrade decisions.

### UI Layer
A Streamlit web application (`ui/lifecycle_app.py`) that presents the analyzer as an interactive form.
Users input current/target aircraft, quantities, route, and utilization assumptions;
the app displays yearly profit, capital investment, payback period, and environmental impact.

## Why the am4 Runtime Package is NOT Used

During the technical spike we discovered that installing the published `am4==0.1.8a1` package leads to a **segmentation fault** when calling `am4.utils.db.init()`. The fault trace points to the interaction between the package’s C‑extension, DuckDB, and PyArrow.

Investigation showed:
- The `am4` package installs as a namespace package containing a compiled `utils.cpython-*.so` and a bundled `libduckdb.so`.
- In the Hermes‑Agent managed Python environment, initializing the internal DuckDB database (`db.init()`) consistently crashes with `exit code 139` (segfault).
- Dependency checks (numpy, pandas, pyarrow/fastparquet) are satisfied, indicating the crash is not due to missing libraries but to an incompatibility between the bundled DuckDB build and the runtime environment.

Because the runtime package is unstable, we treat the **Parquet files as the stable source of truth** and bypass the am4 DB layer entirely.
The Dataset Service reads the Parquet files directly with `pandas` (using pyarrow/fastparquet), which is reliable and performant.

## Data Flow Summary
1. Dataset Service loads (or mocks) the three Parquet tables once per process.
2. Analysis modules request specific entities or filtered routes via the service API.
3. The lifecycle analyzer computes metrics using the retrieved data.
4. The Streamlit UI calls the analyzer and renders the results.

This architecture isolates the volatile runtime dependency, providing a deterministic, testable foundation for the MVP.

