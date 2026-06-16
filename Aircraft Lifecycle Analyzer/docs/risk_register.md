# Risk Register

| ID | Risk Description | Impact | Likelihood | Risk Score | Mitigation |
|----|------------------|--------|------------|------------|------------|
| R1 | **airline4.net API key unavailable** – The project may need live data from the official API for up‑to‑date figures. | Medium | Medium | 6 | Use mock data or allow CSV import of user‑provided datasets. The DatasetService abstraction makes it easy to plug in alternative sources. |
| R2 | **Parquet schema changes** – Future updates to the AM4 data could alter column names or types, breaking the analyzer. | High | Low | 6 | The DatasetService isolates schema dependencies. If a change occurs, only the service layer (or its mock fallback) needs updating. Mock data ensures the UI remains functional during transition. |
| R3 | **Missing route profitability fields** – The `d` column may not represent profit; if it is something else, the financial analysis could be misleading. | Medium | Medium | 6 | Implement a configurable profit model: allow the analyst to override the interpretation of `d` (e.g., treat as distance and compute profit via a separate formula). The service can expose the raw column, and the analysis layer can apply a user‑defined transformation. |
| R4 | **am4 runtime instability** – The segfault in `am4.utils.db.init()` makes the official package unusable as a dependency. | High | High | 9 | **Adopted mitigation**: direct Parquet access via DatasetService (see Architecture). This removes the unstable dependency entirely while preserving access to the official datasets. |
| R5 | **Environmental‑dependency mismatch** – The required Parquet engine (pyarrow/fastparquet) may not be available in all target environments. | Medium | Medium | 6 | The DatasetService catches import errors and falls back to mock data. Documentation specifies the required Python packages (`pandas`, `pyarrow` or `fastparquet`, `streamlit`). |
| R6 | **UI execution failure in headless environments** – Streamlit may fail to start without a graphical display. | Low | Medium | 3 | Use Streamlit’s `--server.headless true` flag; the MVP validation includes this mode. |

**Risk Score** = Impact (1‑3) × Likelihood (1‑3). Higher scores indicate higher priority.

