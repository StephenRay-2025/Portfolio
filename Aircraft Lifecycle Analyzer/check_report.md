# AM4user Project Check Report

## Date: 2026-06-12

## Accomplished Tasks

1. **Created repository structure** under `/home/ubuntu/AM4user/`:
   - collector/
   - repository/
   - analysis/
   - models/
   - ui/
   - tests/
   - docs/

2. **Verified data files** after installing `am4` package:
   - Located in `/home/ubuntu/AM4user/venv_spike/lib/python3.11/site-packages/am4/data/`
   - Files present: `aircraft.parquet`, `aircrafts.parquet`, `airport.parquet`, `airports.parquet`, `route.parquet`, `routes.parquet`
   - File sizes indicate substantial data (e.g., route.parquet ~84MB).

3. **Attempted to test core functionality** (AircraftRoute and RoutesSearch):
   - Wrote test script `test_am4.py` in `/home/ubuntu/AM4user/technical_spike/`.
   - Attempted to initialize DB via `am4.utils.db.init()`.
   - Encountered segmentation faults (exit code 139) when running the test with both system python and virtual environment python.
   - Simpler import tests showed that `am4` module can be imported but accessing `__version__` fails (attribute missing).
   - Direct call to `am4.utils.db.init()` also leads to segfault.

## Issues Encountered

- **Segmentation Fault**: The `am4.utils.db.init()` function appears to cause a segfault, preventing further use of AircraftRoute, RoutesSearch, etc.
- **Possible Causes**:
  - Incompatibility between the packaged `am4` version (0.1.8a1) and the underlying dependencies (e.g., numpy, pandas, pyarrow) in the environment.
  - The parquet files might be corrupted or in an unexpected format.
  - The `am4` package may have native extensions that are not compatible with the current Python/OS version.

## Next Steps

1. **Investigate the segfault**:
   - Run `am4.utils.db.init()` under `gdb` or with `faulthandler` to obtain a traceback.
   - Check the exact version of dependencies in the virtual environment.
   - Consider installing `am4` from source (clone the repository) to ensure compatibility.

2. **Alternative approach**:
   - If the segfault cannot be resolved quickly, consider bypassing the `am4` provided DB layer and directly read the parquet files using `pandas` or `pyarrow` to construct the needed objects (Aircraft, Airport, Route) manually for the proof-of-concept Dashboard.
   - This would still fulfill the goal of demonstrating the dashboard using the same data.

3. **Proceed with Aircraft Lifecycle Analyzer**:
   - Once data access is reliable (either via fixed `am4` or direct parquet reads), implement the analyzer in `analysis/lifecycle.py`.
   - Create a Streamlit UI in `ui/lifecycle_app.py` that allows input of current fleet, target aircraft, and quantity, and outputs profit change, payback period, etc.

4. **Documentation**:
   - Update `docs/` with architecture diagrams, ER diagram (based on the parquet schema or inferred SQLite schema), and usage instructions.

## Conclusion

The repository structure is set up and the necessary data files are present. However, the `am4` package's initialization leads to a segmentation fault, blocking direct use of its high-level APIs. Resolution of this issue is required before proceeding to test AircraftRoute and RoutesSearch as planned. Once resolved, the remaining steps (testing, implementing the first module) can be completed swiftly.

## Attachments

- Directory listing of `/home/ubuntu/AM4user/` and subdirectories.
- Contents of `/home/ubuntu/AM4user/technical_spike/` (test scripts).
- Output of dependency checks (to be added after investigation).
