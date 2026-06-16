# Airline Manager 4 Dashboard – Requirements List

## Project Goal
Build a web‑based dashboard (Streamlit) that assists Airline Manager 4 players in making informed aircraft‑upgrade decisions by integrating live game data, financial metrics, fuel/CO₂ pricing, hub performance, and in‑game stock‑market trends. The project follows a clean four‑layer architecture to ensure maintainability and ease of swapping storage back‑ends.

## Core Modules
1. **Account Overview**
   - Display current player stats: level, share value, founded date, alliance status, achievements, fleet size, routes.
   - Show quick‑look KPIs: cash on hand, daily profit/loss, aircraft utilization.
   - Data source: `airline4.net` API endpoints (`/user`, `/alliance`, `/fleet`, `/routes`).

2. **Financial Analysis**
   - Income statement (revenue vs. expenses) over selectable time windows (daily, weekly, monthly).
   - Cash‑flow trend chart.
   - Break‑even analysis for each aircraft type.
   - **Note on data availability:** The official API provides only the most recent 24‑hour financial snapshot. To enable multi‑day analysis, the **Collector** will store a daily snapshot of the financial data in the SQLite repository. Over time this builds a historical series that powers the income statement and cash‑flow charts.
   - Data source: user‑provided financial logs (CSV) **or** accumulated daily snapshots from the API.

3. **Fuel & CO₂ Price Tracking**
   - Line chart of fuel price and CO₂ quota price over time (last 30 days).
   - Ability to set price alerts.
   - Data source: `airline4.net` `/fuel` and `/co2` endpoints (if available) or community‑maintained CSV from `am4-prices` PyPI package.

4. **Aircraft Lifecycle Analyzer** *(new high‑value page)*
   - Input: current fleet composition (e.g., BAe146‑300 × 7) and performance metrics (daily profit, fuel burn, maintenance cost).
   - Allows user to select a target aircraft type (A220‑100, ARJ21, 737‑800, etc.) and quantity.
   - Output: projected profit after replacement, profit increase %, payback period (days), and CO₂ impact.
   - Example:
     ```
     Current Fleet: BAe146-300 × 7
     Current Daily Profit: 12.5M
     Replace with: A220-100 × 7
     → Profit: 15.2M
     → Increase: +21.6%
     → Payback: 188 days
     ```
   - Uses the `abc8747/am4` core calculations for aircraft performance, fuel burn, and route compatibility.

5. **Fleet Health** *(new page)*
   - Computes a Fleet Health Score (0‑100) based on:
     - Average fleet age
     - Remaining A‑check time (or next maintenance due)
     - Fuel efficiency (burn per seat‑km)
     - Maintenance cost ratio
   - Highlights aircraft needing priority retirement or heavy maintenance.
   - Example output:
     ```
     Fleet Health Score: 82/100
     Priority for retirement: BAe146 #3, BAe146 #5
     ```

6. **Hub Analysis**
   - Map view of owned hubs (airports) with metrics: passenger demand, cargo demand, slot utilization, competition level.
   - Heatmap of route profitability per hub.
   - Suggest under‑served high‑demand routes.
   - Data source: API `/airports`, `/routes`, plus static airport data (IATA/ICAO, coordinates) from `abc8747/am4` database.

7. **In‑Game Stock Market Analysis**
   - Track share price history of owned airlines (via `/share_development` endpoint).
   - Visualize price trends, volume, and dividend events.
   - Comparative analysis against peers in same alliance or region.
   - Simple technical indicators (moving averages, RSI) for speculative trading decisions.

8. **Scenario Simulator / Sensitivity Analysis** *(new page)*
   - User defines multiple scenarios (e.g., fuel price, CO₂ quota price, demand multipliers).
   - For each scenario, the engine re‑runs profit projections for each aircraft type in the fleet.
   - Output table showing profit change for A220, 737‑800, ARJ21, etc., under each scenario.
   - Enables “what‑if” analysis for strategic planning and demonstrates data‑analysis chops.
   - Example:
     ```
     Scenario 1: Fuel = 3000, CO2 = 120
     Scenario 2: Fuel = 1500, CO2 = 80
     → A220 profit change: +X%
     → 737 profit change: +Y%
     → ARJ profit change: +Z%
     ```

9. **Upgrade Recommendation Engine**
   - Input: current fleet composition, route profitability, fuel/CO₂ trends, available cash.
   - Output: ranked list of aircraft upgrades (new models, retrofits) with expected ROI, payback period, and impact on emissions.
   - **Implementation:** Simple scoring model using pandas/numpy (no machine learning or demand forecasting). Scores combine:
     - Estimated profit increase from the new aircraft type.
     - Fuel‑efficiency gain.
     - Emissions reduction.
     - Payback period based on aircraft cost and incremental profit.
   - Leverages core calculations from `abc8747/am4` (C++ core exposed via Python API).

## Risks and Mitigations
| Risk | Description | Mitigation |
|------|-------------|------------|
| **R1 – Heavy reliance on official API** | The airline4.net API requires an email request for access; approval is uncertain. | - Design the **Collector** to work with optional API token; if absent, fall back to user‑uploaded CSV or mock data.<br>- Provide a sample dataset and instructions for manual data import.<br>- Allow the dashboard to run fully offline using static data from `abc8747/am4`. |
| **R2 – Insufficient data for financial analysis** | API returns only the latest 24‑hour financials; multi‑day statements need accumulation. | - Collector stores a timestamped snapshot each successful API call (or when user uploads a CSV).<br>- Over days/weeks this builds a time series for income statement and cash‑flow analysis.<br>- Clearly document that meaningful financial trends appear after several days of data collection. |
| **R3 – Overly complex upgrade recommendation** | Initial draft mentioned ML, regression, demand forecasting which need data not yet available. | - Simplify to a rule‑based scoring model (see module 9).<br>- Keep the door open for future enhancement once sufficient historical data is collected.<br>- Emphasize interpretability and ease of validation. |

## Data Persistence
- **SQLite** database (`am4_dashboard.db`) stores:
  - Cached API responses (to respect rate limits).
  - User‑uploaded CSV logs (financials, flight operations).
  - Pre‑computed metrics (ROI scores, hub scores, fleet health).
- Schema designed for extensibility; later migration to PostgreSQL only affects the repository layer.

## Four‑Layer Architecture
```
API (airline4.net, am4‑prices, etc.)
        ↓
Collector ──► fetches raw data, normalizes, writes to Repository
        ↓
Repository ──► SQLite (or future PostgreSQL) provides CRUD interface
        ↓
Analysis Engine ──► contains all business logic:
                    - Aircraft Lifecycle Analyzer
                    - Fleet Health scorer
                    - Scenario Simulator
                    - Upgrade Advisor
                    - Financial / Fuel / Hub / Stock modules
        ↓
UI (Streamlit) ──► presents interactive pages, calls Analysis Engine via service functions
```
- This separation ensures that swapping SQLite for PostgreSQL only requires changes in the `repository/` module; the analysis and UI layers remain unchanged.
- Each layer is implemented as a Python package (`collector/`, `repository/`, `analysis/`, `ui/`).

## Technical Stack
- **Language**: Python 3.11+
- **Core Libraries**:
  - `requests` – API calls to airline4.net
  - `pandas`, `numpy` – data manipulation
  - `sqlite3` (built‑in) – local storage (via repository layer)
  - `matplotlib` / `seaborn` – static charts
  - `plotly` (optional) – interactive charts
  - `streamlit` – web framework
- **External Tools**:
  - `abc8747/am4` – provides core calculation functions (exposed via its Python API or via compiled C++ extensions)
  - `am4-prices` PyPI package – for historical fuel/CO₂ data (if API lacking)
- **Version Control**: Git (repository hosted on GitHub)
- **Documentation**: README.md, docstrings, and a `docs/` folder with API reference.

## Data Flow
1. User authenticates (API token stored securely in `.env`; optional).
2. **Collector** pulls latest data from airline4.net (respecting `requests_remaining`) and optional third‑party sources.
   - If API token missing or request fails, Collector can load user‑provided CSV or use embedded sample data.
3. **Repository** stores raw and normalized data in SQLite with timestamps.
4. User can upload supplemental CSVs (financials, flight logs) → Collector ingests into Repository.
5. Background refresh (via Streamlit `st.autorefresh` or a separate cron job) triggers Collector every 15‑30 min.
6. **Analysis Engine** reads from Repository, computes metrics, runs scoring/models.
7. **UI** (Streamlit) calls Analysis Engine functions to render charts/tables and interactive widgets.
8. Upgrade advisor runs scoring algorithm on demand and returns ranked suggestions.

## Non‑Functional Requirements
- **Rate‑limit handling**: Respect API limits (default 500 requests per 5 min); implement exponential backoff and caching in Collector.
- **Security**: Store API token in environment variable; never commit to repo.
- **Performance**: Data retrieval < 2 s per page; charts render smoothly with ≤ 500 data points.
- **Extensibility**: Plugin‑like structure allowing addition of new analysis panels in `analysis/`.
- **Testing**: Unit tests for scoring functions (`pytest`); CI workflow on GitHub Actions.
- **Licensing**: MIT license (consistent with upstream `abc8747/am4`).

## Deliverables (for GitHub Showcase)
- `README.md` with project overview, architecture diagram, installation instructions, usage screenshots.
- `requirements.txt` (or `environment.yml`) listing exact package versions.
- Source tree:
  ```
  AM4user/
  ├─ collector/
  ├─ repository/
  ├─ analysis/
  ├─ ui/            ← Streamlit entry point (app.py) and pages
  ├─ data/          ← sample SQLite schema, optional sample CSV
  ├─ scripts/       ← data refresh, DB initialization
  ├─ tests/
  ├─ Dockerfile
  ├─ .github/workflows/ci.yml
  └─ LICENSE
- Four key images for README:
  1. System architecture diagram (API → Collector → Repository → Analysis → Dashboard).
  2. ER diagram: database schema (tables for users, fleet, routes, prices, scenarios, etc.).
  3. Upgrade decision example: ARJ21 → A220 with ROI 17%, Payback 154 Days.
  4. Hub heatmap: Tokyo hub coverage over airport map.
- Additional optional sections: stock analysis with technical indicators, scenario simulator screenshots.

## Milestones
**M1 (Must‑Complete)**
- Set up SQLite schema.
- Integrate `abc8747/am4` core (aircraft performance, route compatibility).
- Load static aircraft and airport data into Repository.

**M2 (Core Value)**
- Implement **Aircraft Lifecycle Analyzer** page.
- Implement **Fleet Health** scorer and page.
- Implement **Upgrade Advisor** with ROI/payback calculations (simple scoring, no ML).

**M3 (Visualization)**
- Build Streamlit dashboard (`ui/`) with pages:
  - Account Overview
  - Financial Analysis
  - Fuel & CO₂ Price Tracking
  - Hub Map (using `streamlit‑folium` or `st.map`)
- Add basic charts for fuel/CO₂ trends.

**M4 (Optional – API Sync)**
- Enable automatic sync with `airline4.net` API (Collector scheduler).
- Handle authentication token storage and refresh.
- Provide fallback to mock/sample data when API unavailable.

**M5 (Nice‑to‑Have)**
- In‑Game Stock Market Analysis (share price trends, technical indicators).
- Scenario Simulator / Sensitivity Analysis page.
- Additional visualizations (e.g., interactive Plotly charts).
- Dockerize the app and set up GitHub Actions CI/CD.

---
*This requirements list will guide the implementation of the AM4 Dashboard project located at `/home/ubuntu/AM4user`. Adjustments can be made as more details about the airline4.net API and the abc8747/am4 library emerge during development.*