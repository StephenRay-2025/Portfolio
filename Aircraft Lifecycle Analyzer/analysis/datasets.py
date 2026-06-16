"""Dataset Service Layer for AM4user project.
Provides a unified interface to load and access Parquet datasets.
Implements caching and graceful fallback to mock data.
"""
import os
import pandas as pd
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Path to the am4 data directory (inside the venv) for routes
DATA_DIR_PARQUET = os.path.join(
    os.path.dirname(__file__), '..', 'venv_spike', 'lib', 'python3.11', 'site-packages', 'am4', 'data'
)
# Path to the models directory for aircraft and airports (CSV files)
DATA_DIR_MODELS = '/home/ubuntu/AM4user/models/'

class DatasetService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatasetService, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self._aircraft = None
        self._airports = None
        self._routes = None
        self._load_errors = []

    def _load_dataset(self, filename, fallback_func):
        """Load a parquet or CSV file; on failure, call fallback_func and log error."""
        # Determine if we should load from CSV (for aircraft and airports) or parquet (for routes)
        if filename == 'aircraft.parquet':
            csv_filename = 'aircrafts.csv'
            path = os.path.join(DATA_DIR_MODELS, csv_filename)
            try:
                df = pd.read_csv(path)
                logger.info(f"Loaded {csv_filename}: {df.shape}")
                return df
            except Exception as e:
                logger.warning(f"Failed to load {csv_filename}: {e}. Using mock data.")
                self._load_errors.append((csv_filename, str(e)))
                return fallback_func()
        elif filename == 'airports.parquet':
            csv_filename = 'airports.csv'
            path = os.path.join(DATA_DIR_MODELS, csv_filename)
            try:
                df = pd.read_csv(path)
                logger.info(f"Loaded {csv_filename}: {df.shape}")
                return df
            except Exception as e:
                logger.warning(f"Failed to load {csv_filename}: {e}. Using mock data.")
                self._load_errors.append((csv_filename, str(e)))
                return fallback_func()
        else:
            # Load from parquet in the original directory (for routes)
            path = os.path.join(DATA_DIR_PARQUET, filename)
            try:
                df = pd.read_parquet(path)
                logger.info(f"Loaded {filename}: {df.shape}")
                return df
            except Exception as e:
                logger.warning(f"Failed to load {filename}: {e}. Using mock data.")
                self._load_errors.append((filename, str(e)))
                return fallback_func()

    @property
    def aircraft(self):
        if self._aircraft is None:
            self._aircraft = self._load_dataset(
                'aircraft.parquet',
                self._mock_aircraft
            )
        return self._aircraft

    @property
    def airports(self):
        if self._airports is None:
            self._airports = self._load_dataset(
                'airports.parquet',
                self._mock_airports
            )
        return self._airports

    @property
    def routes(self):
        if self._routes is None:
            self._routes = self._load_dataset(
                'route.parquet',
                self._mock_routes
            )
        return self._routes

    # Mock data generators
    def _mock_aircraft(self):
        # Minimal mock aircraft data
        data = {
            'id': [1, 2],
            'shortname': ['A220-100', 'A320neo'],
            'manufacturer': ['Airbus', 'Airbus'],
            'name': ['A220-100', 'A320neo'],
            'type': [0, 0],
            'priority': [0, 0],
            'eid': [0, 0],
            'ename': ['PW1500G', 'PW1100G'],
            'speed': [850.0, 870.0],
            'fuel': [12.0, 13.0],
            'co2': [0.1, 0.1],
            'cost': [50000000, 60000000],
            'capacity': [130, 180],
            'rwy': [1500, 1800],
            'check_cost': [500000, 600000],
            'range': [6000, 6500],
            'ceil': [40000, 41000],
            'maint': [100, 120],
            'pilots': [2, 2],
            'crew': [4, 5],
            'engineers': [2, 2],
            'technicians': [2, 2],
            'img': ['', ''],
            'wingspan': [35, 36],
            'length': [35, 38]
        }
        return pd.DataFrame(data)

    def _mock_airports(self):
        data = {
            'id': [1, 2],
            'name': ['PEK', 'SIN'],
            'fullname': ['Beijing Capital', 'Singapore Changi'],
            'country': ['China', 'Singapore'],
            'continent': ['Asia', 'Asia'],
            'iata': ['PEK', 'SIN'],
            'icao': ['ZBAA', 'WSSS'],
            'lat': [40.08, 1.36],
            'lng': [116.58, 103.99],
            'rwy': [3800, 4000],
            'market': [1000, 1500],
            'hub_cost': [200000, 250000],
            'rwy_codes': ['01L/19R', '02C/20C']
        }
        return pd.DataFrame(data)

    def _mock_routes(self):
        # Mock route data with columns yd, jd, fd, d
        data = {
            'yd': [1, 1, 2, 2],
            'jd': [1, 2, 1, 2],
            'fd': [2, 1, 2, 1],
            'd': [1000.0, 1200.0, 900.0, 1100.0]
        }
        return pd.DataFrame(data)

    # Public API methods
    def get_aircraft(self):
        """Return DataFrame of all aircraft."""
        return self.aircraft.copy()

    def get_aircraft_by_name(self, name):
        """
        Return aircraft row matching shortname or name.
        Returns Series if found, else None.
        """
        df = self.aircraft
        # Try shortname first
        match = df[df['shortname'] == name]
        if not match.empty:
            return match.iloc[0]
        # Try name contains
        match = df[df['name'].str.contains(name, case=False, na=False)]
        if not match.empty:
            return match.iloc[0]
        return None

    def get_airport(self):
        """Return DataFrame of all airports."""
        return self.airports.copy()

    def get_airport_by_code(self, code):
        """
        Return airport row matching IATA or ICAO code.
        Returns Series if found, else None.
        """
        df = self.airports
        code = code.upper()
        match = df[(df['iata'] == code) | (df['icao'] == code)]
        if not match.empty:
            return match.iloc[0]
        return None

    def get_route(self):
        """Return DataFrame of all route records."""
        return self.routes.copy()

    def find_routes(self, aircraft_id=None, origin_id=None, dest_id=None):
        """
        Filter routes by optional aircraft, origin, destination IDs.
        Returns DataFrame.
        """
        df = self.routes
        if aircraft_id is not None:
            df = df[df["fd"] == aircraft_id]
        if origin_id is not None:
            df = df[df["jd"] == origin_id]
        if dest_id is not None:
            df = df[df["yd"] == dest_id]
        return df.copy()

    def health(self):
        """Return dict with load errors and status."""
        return {
            'load_errors': self._load_errors,
            'aircraft_shape': self.aircraft.shape,
            'airports_shape': self.airports.shape,
            'routes_shape': self.routes.shape
        }

    def get_aircraft_by_id(self, aircraft_id: int):
        """Return the aircraft row matching the internal ID, or None."""
        df = self.aircraft
        match = df[df["id"] == aircraft_id]
        return None if match.empty else match.iloc[0]

    def get_airport_by_id(self, airport_id: int):
        """Return the airport row matching the internal ID, or None."""
        df = self.airports
        match = df[df["id"] == airport_id]
        return None if match.empty else match.iloc[0]

    # ------------------------------------------------------------------
    #  NEW: Persist a user‑created route record
    # ------------------------------------------------------------------
    def add_route_record(self, aircraft_id: int, origin_id: int,
                         dest_id: int, profit_per_flight: float) -> None:
        """
        Append a single route row to the internal route table and
        rewrite the backing Parquet file.

        Parameters
        ----------
        aircraft_id : int
            Internal aircraft ID (fd in route.parquet)
        origin_id : int
            Internal origin‑airport ID (jd)
        dest_id : int
            Internal destination‑airport ID (yd)
        profit_per_flight : float
            The “d” column value – profit per flight in the simulation’s
            currency unit.
        """
        # Load the current table (this will hit the cache if already loaded)
        routes = self.routes.copy()

        # Build the new row – note the column order used by the original file:
        #   yd = destination airport id
        #   jd = origin airport id
        #   fd = aircraft id
        new_row = {
            "yd": dest_id,   # destination
            "jd": origin_id, # origin
            "fd": aircraft_id,
            "d": profit_per_flight
        }

        # Append and reset index (keeps a clean integer index)
        routes = pd.concat([routes, pd.DataFrame([new_row])], ignore_index=True)

        # Write back to the same Parquet file that the service reads from.
        # We wrap the write in a temporary file first to avoid corrupting
        # the dataset if the process is interrupted.
        parquet_path = os.path.join(DATA_DIR_PARQUET, "route.parquet")
        tmp_path = parquet_path + ".tmp"
        try:
            routes.to_parquet(tmp_path, index=False)
            os.replace(tmp_path, parquet_path)   # atomic replace on POSIX
        except Exception:
            # Clean up temp file on error and re‑raise
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

        # Bust the internal cache so the next property read sees the new data
        self._routes = None

# Singleton instance for convenience
dataset_service = DatasetService()

if __name__ == '__main__':
    # Quick test
    logging.basicConfig(level=logging.INFO)
    svc = DatasetService()
    print("Aircraft shape:", svc.aircraft.shape)
    print("Airports shape:", svc.airports.shape)
    print("Routes shape:", svc.routes.shape)
    print("Health:", svc.health())
