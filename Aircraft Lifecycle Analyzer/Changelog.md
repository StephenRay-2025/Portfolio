# Changelog

## [Unreleased] - 2026-06-15
### Added
- Fallback profit calculation in `analysis/lifecycle.py` when route not found in route.parquet.
- Ability to save computed routes back to route.parquet via `DatasetService.add_route_record`.
- UI enhancements in `ui/lifecycle_app.py`: show profit source and a "Save this route" button.
- Helper methods in `analysis/datasets.py`: `get_aircraft_by_id`, `get_airport_by_id`, `add_route_record`.
- Updated `analysis/lifecycle.py` to expose IDs and profit source for UI.
- Updated `analysis/lifecycle.py`'s `get_route_profit` to return profit and source flag.
- Updated `analysis/lifecycle.py`'s `compute_route_metrics` and `lifecycle_analysis` to propagate IDs and source.
- Added Flight Detail Card in `ui/lifecycle_app.py` displaying aircraft specs, route demand, ticket prices, revenue breakdown, fuel/CO₂ costs, and route fee when clicking Analyze.
- 更新：Flight Detail Card 使用结构化表格展示航线数据、两款飞机对比（包含详细参数、单程飞行时间、燃油消耗（lbs）、CO₂ 消耗（lbs）），并在表格中提供单程收益、每日/周/月/年收益以及以小时为单位的回本周期（默认全经济舱）。
- Added structured tables to Flight Detail Card: route data (length, fee, demand, ticket prices) and aircraft comparison (specs, flight time, fuel/CO₂ consumption in kg), plus profit per day/week/month/year and payback period in hours.
### Changed
- Modified `get_route_profit` to fallback to on-the-fly profit computation using `compute_flight_economics`.
- Updated `lifecycle_analysis` to return additional fields for UI.
- Adjusted UI to display profit source and conditionally show save button.
### Fixed
- Resolved "Route not found for aircraft A220-100 from PEK to SIN" error by enabling dynamic profit calculation and persistence.
- Fixed `find_routes` in `analysis/datasets.py` to correctly map aircraft, origin, destination IDs.
- Verified dashboard works with default parameters (A220-100, PEK→SIN) showing computed profit and save button.
- Fixed syntax error in `ui/lifecycle/app.py`: removed stray trailing backslash in import statement.
- Fixed import error in `ui/lifecycle/app.py`: changed `from analysis.datasets import dataset_service` to `from datasets import dataset_service` to match sys.path adjustment.

## Development Log (2026-06-12 to 2026-06-15)

### 中文摘要
- 2026-06-12：创建项目文件夹 `/home/ubuntu/AM4user`，编写需求清单 `REQUIREMENTS.md`，明确功能模块：账户概览、财务分析、燃油+CO₂价格变化图、升级建议、枢纽分析、股票市场分析；采用官方 API (airline4.net)、abc8747/am4、Python、SQLite、Streamlit 等技术栈。
- 2026-06-15：调试 AM4user 仪表盘在点击 Analyze 时出现 “Current aircraft metrics: Route not found for aircraft A220-100 from PEK to SIN” 的错误；检查发现路线数据中缺少该飞机-航线组合；实现了在路线未找到时回退到即时利润计算（基于飞机规格、大圆距离、实时燃油/CO₂ 价格），并在 UI 中添加 “保存此航线” 按钮，将计算结果写回 route.parquet 以便后续查询。
- 2026-06-15：修复 `ui/lifecycle_app.py` 中的语法错误（多余反斜杠）和导入错误（将 `from analysis.datasets import dataset_service` 改为 `from datasets import dataset_service`）。
- 修改了 `analysis/datasets.py`（添加 `add_route_record`、`get_aircraft_by_id`、`get_airport_by_id` 等方法），`analysis/lifecycle.py`（修改 `get_route_profit`、`compute_route_metrics`、`lifecycle_analysis` 以返回利润来源并暴露 ID），`ui/lifecycle_app.py`（显示利润来源并条件显示保存按钮）。
- 修复了 `analysis/datasets.py` 中的 `find_routes` 函数，将 ID 列映射正确（aircraft_id → fd, origin_id → jd, dest_id → yd），确保保存的航线能被正确查询。
- 更新了 Changelog.md。

- 更新：在仪表盘中添加「Flight Detail Card」，点击 Analyze 时显示飞机参数（购买价、座位数、航程、发动机型号-油耗-速度、维修时间、A检时间、机组配置）、航线每日需求、各舱位单座票单价、单程收益（经济/商务/头等舱）、燃油成本、CO₂ 成本及航线费用。
- 更新：Flight Detail Card 使用结构化表格展示航线数据（长度、开通费、日需求、三舱票价）和两款飞机对比（含详细参数、单程飞行时间、燃油消耗（lb）、CO₂ 消耗（kg）），并提供单程收益、每日/周/月/年收益以及以小时为单位的回本周期（默认全经济舱）。
### English Summary
- 2026-06-12: Created project folder `/home/ubuntu/AM4user`, authored requirements list `REQUIREMENTS.md` outlining modules: account overview, financial analysis, fuel & CO₂ price change charts, upgrade suggestions, hub analysis, in‑game stock market analysis; stack: official API (airline4.net), abc8747/am4, Python, SQLite, Streamlit.
- 2026-06-15: Debugged the “Route not found for aircraft A220-100 from PEK to SIN” error in the AM4user dashboard; discovered missing route entry in `route.parquet`; implemented on‑the‑fly profit fallback using aircraft specs, great‑circle distance, and live fuel/CO₂ pricing; added a “Save this route” button in the UI to persist computed routes to `route.parquet` for future look‑ups.
- 2026-06-15: Fixed syntax error (stray backslash) and import error in `ui/lifecycle_app.py` (changed `from analysis.datasets import dataset_service` to `from datasets import dataset_service`).
- Modified files: `analysis/datasets.py` (added `add_route_record`, `get_aircraft_by_id`, `get_airport_by_id`), `analysis/lifecycle.py` (updated `get_route_profit`, `compute_route_metrics`, `lifecycle_analysis` to return profit source and expose IDs), `ui/lifecycle_app.py` (show profit source and conditionally render save button).
- Fixed `find_routes` in `analysis/datasets.py` to correctly map IDs (aircraft_id → fd, origin_id → jd, dest_id → yd), ensuring saved routes are lookup‑able.
- Updated Changelog.md.
- Added Flight Detail Card to the dashboard: when clicking Analyze, displays aircraft parameters (purchase price, seat count, range, engine model‑fuel‑consumption‑speed, maintenance time, A‑check time, crew composition), route daily demand, ticket prices per class, single‑flight revenue (Economy/Business/First), fuel cost, CO₂ cost, and route fee.
- Updated Flight Detail Card to display structured tables for route data and aircraft comparison (including detailed specs, one‑way flight time, fuel consumption in lbs, CO₂ quota consumption in kg). The tables also show single‑flight revenue, profit per day/week/month/year, and payback period in hours (defaulting to full‑economy class).
- Updated: Flight Detail Card now displays structured tables for route data and aircraft comparison (including detailed specs, one‑way flight time, fuel consumption in lbs, CO₂ quota consumption in lbs). The tables also show single‑flight revenue, profit per day/week/month/year, and payback period in hours (defaulting to full‑economy class).
