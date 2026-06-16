# Economics Model Layer Documentation

## 1. Overview

The current AM4 Aircraft Dashboard works with raw simulation features from `route.parquet`:
- `yd`, `jd`, `fd` – internal IDs for destination airport, origin airport, and aircraft
- `d` – a simulation feature (distance‑like value) **not** representing financial profit

To enable genuine business‑level analysis (profit, ROI, upgrade decisions) we need an **economic interpretation layer** that converts these simulation features into monetary values using explicit assumptions about ticket pricing, fuel consumption, operating costs, etc.

This document specifies the design and implementation of `analysis/economics.py`, which fulfills that role.

---

## 2. Data Inputs

The economics model consumes the following data, all accessed via the existing `DatasetService`:

| Source | Fields Used | Description |
|--------|-------------|-------------|
| **Aircraft data** (`dataset_service.get_aircraft()`) | `capacity` (seats), `fuel` (fuel consumption per hour, kg/h), `co2` (CO₂ emission per hour, kg/h), `cost` (purchase price, currency units), `speed` (cruise speed, km/h) | Core aircraft performance & cost characteristics |
| **Route data** (`dataset_service.find_routes()`) | `fd` (aircraft ID), `jd` (origin airport ID), `yd` (destination airport ID), `d` (simulation feature – currently unused for economics) | Identifies the aircraft‑origin‑destination tuple |
| **Airport data** (`dataset_service.get_airport()`) | `lat`, `lng` (for great‑circle distance calculation) | Needed to compute actual flight distance |
| **Assumptions** (passed as a dict) | See Section 3 | Parameterizes pricing, load factor, fuel/CO₂ costs, etc. |

> **Note:** The model does **not** read any financial column from `route.parquet`; all economic values are derived from assumptions combined with the physical attributes above.

---

## 3. Economic Model Assumptions

All assumptions are explicit and configurable via a dictionary passed to the model functions. Default values are provided but can be overridden by the caller.

| Assumption | Symbol | Default | Meaning |
|------------|--------|---------|---------|
| `base_price_per_seat_km` | $p$ | 0.10 (currency units per seat‑km) | Average revenue generated per seat‑kilometre flown |
| `load_factor` | $LF$ | 0.75 | Proportion of seats filled with passengers |
| `fuel_cost_per_kg` | $c_f$ | 0.80 (currency units per kg) | Price of jet fuel |
| `co2_cost_per_kg` | $c_{co2}$ | 0.02 (currency units per kg) | Carbon cost or tax per kg CO₂ emitted |
| `maintenance_cost_per_flight` | $m$ | 50.0 (currency units) | Fixed maintenance/operating cost per flight (excluding fuel & CO₂) |
| `utilization_flights_per_day` | $U_{day}$ | 2 (used in higher‑level analysis) | Flights per aircraft per day – passed from UI/lifecycle if needed |
| `days_per_year` | $D_{yr}$ | 365 | Operating days per year |

All assumptions are **simulation‑grade**; they are not calibrated to real airline financials but provide a deterministic basis for comparing aircraft alternatives.

---

## 4. Revenue Model

Revenue is modeled as a function of seat‑kilometres supplied, load factor, and a per‑seat‑km price.

BRACKET_DISPLAY_OPEN
\text{Revenue} = p \times \text{Distance}_{km} \times \text{Capacity} \times LF
BRACKET_DISPLAY_CLOSE

- `Distance_km` is the great‑circle distance between origin and destination airports (calculated from latitude/longitude).
- `Capacity` comes from the aircraft’s `capacity` field (number of seats).
- `LF` is the load factor (default 0.75).

The model assumes revenue scales linearly with distance and seat supply; more sophisticated demand modifiers (e.g., route‑specific demand index) can be added later by adjusting `p` or introducing a `demand_factor`.

---

## 5. Cost Model

Total cost per flight comprises three additive components:

### 5.1 Fuel Cost
BRACKET_DISPLAY_OPEN
\text{FuelCost} = \text{FuelConsumption}_{kg/h} \times \text{FlightTime}_{h} \times c_f
BRACKET_DISPLAY_CLOSE

- `FuelConsumption_kg/h` = aircraft `fuel` field.
- `FlightTime_h = Distance_km / Speed_kmh` (using aircraft `speed`).

### 5.2 CO₂ Cost
BRACKET_DISPLAY_OPEN
\text{CO2Cost} = \text{CO2Emission}_{kg/h} \times \text{FlightTime}_{h} \times c_{co2}
BRACKET_DISPLAY_CLOSE

- `CO2Emission_kg/h` = aircraft `co2` field.

### 5.3 Maintenance / Operating Cost
BRACKET_DISPLAY_OPEN
\text{OperatingCost} = m
BRACKET_DISPLAY_CLOSE

A fixed per‑flight cost capturing routine maintenance, crew, landing fees, etc. (configurable).

BRACKET_DISPLAY_OPEN
\boxed{\text{Total Cost} = \text{FuelCost} + \text{CO2Cost} + \text{OperatingCost}}
BRACKET_DISPLAY_CLOSE

---

## 6. Profit Model

Profit per flight is simply revenue minus cost:

BRACKET_DISPLAY_OPEN
\boxed{\text{Profit}_{flight} = \text{Revenue} - \text{Total Cost}}
BRACKET_DISPLAY_CLOSE

Derived metrics:
- **Profit per day** = `Profit_flight` × `U_{day}`
- **Profit per year** = `Profit_flight` × `U_{day}` × `D_{yr}`

These are returned by the model for further aggregation (e.g., fleet‑level calculations in `lifecycle.py`).

---

## 7. ROI Model (Upgrade Decision Core)

When evaluating a potential aircraft upgrade, the economics module provides the inputs needed for ROI and payback period:

- **Profit increase per flight** = `Profit_target` – `Profit_current`
- **Additional investment** = (Purchase price_target × Qty_target) – (Purchase price_current × Qty_current)
- **Annual profit increase** = Profit increase per flight × `U_{day}` × `D_{yr}` × `Qty_target` (assuming the new aircraft replaces the old one on a one‑to‑one basis; adjust as needed)

Then:

BRACKET_DISPLAY_OPEN
\text{ROI} = \frac{\text{Annual Profit Increase}}{\text{Additional Investment}}
BRACKET_DISPLAY_CLOSE

BRACKET_DISPLAY_OPEN
\text{Payback Period (years)} = \frac{\text{Additional Investment}}{\text{Annual Profit Increase}}
BRACKET_DISPLAY_CLOSE

If the denominator is zero or negative, ROI is undefined and payback is infinite.

These formulas are implemented in helper functions; the Streamlit UI (`lifecycle.py`) can call them directly to display ROI and payback.

---

## 8. Aircraft Comparison Logic

The economics module enables side‑by‑side comparison of any two aircraft on a given route by computing:

| Metric | Current Aircraft | Target Aircraft |
|--------|------------------|-----------------|
| Revenue per flight | … | … |
| Cost per flight | … | … |
| Profit per flight | … | … |
| Profit per year (per aircraft) | … | … |
| ROI of switching | — | computed as above |

Comparison highlights the effect of:
- **Capacity** (more seats → higher revenue)
- **Fuel efficiency** (lower `fuel` → lower fuel cost)
- **Speed** (higher speed → shorter flight time → lower fuel/CO₂ cost)
- **Purchase price** (higher `cost` → larger upfront investment)

Typical comparisons (A220‑100 vs A320neo, BAe146 vs ARJ21, 737 vs A320 family) can be performed by supplying the respective shortnames and letting the model compute the delta.

---

## 9. Core Function Design (Pseudocode Only)