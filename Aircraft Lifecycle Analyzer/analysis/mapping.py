"""Mapping layer for AM4user project.

Provides functions to convert UI-friendly identifiers to internal IDs used
in the route.parquet dataset and aircraft/airport lookup tables.
"""

from datasets import dataset_service


def resolve_aircraft(ui_input: str) -> str:
    """Map UI aircraft string (e.g., 'A220-100' or 'a221') to internal shortname.

    Args:
        ui_input: Aircraft identifier as entered in UI (name or shortname).

    Returns:
        Internal shortname string (e.g., 'a221').

    Raises:
        ValueError: If aircraft not found.
    """
    ac = dataset_service.get_aircraft_by_name(ui_input)
    if ac is None:
        raise ValueError(f"Aircraft '{ui_input}' not found")
    return ac['shortname']


def resolve_airport(iata: str) -> int:
    """Map IATA code to internal airport ID.

    Args:
        iata: Airport IATA code (e.g., 'PEK').

    Returns:
        Internal airport ID (integer).

    Raises:
        ValueError: If airport not found.
    """
    ap = dataset_service.get_airport_by_code(iata.upper())
    if ap is None:
        raise ValueError(f"Airport IATA '{iata}' not found")
    return int(ap['id'])


def resolve_route(aircraft_ui: str, origin_iata: str, dest_iata: str) -> tuple:
    """Resolve UI inputs to internal route IDs used in route.parquet.

    The route.parquet table uses columns:
        yd -> destination airport ID
        jd -> origin airport ID
        fd -> aircraft ID

    Args:
        aircraft_ui: Aircraft identifier as entered in UI (name or shortname).
        origin_iata: Origin IATA code.
        dest_iata: Destination IATA code.

    Returns:
        Tuple (yd, jd, fd) as integers.

    Raises:
        ValueError: If any lookup fails.
    """
    # Resolve aircraft to get internal aircraft ID (fd) and shortname if needed
    ac = dataset_service.get_aircraft_by_name(aircraft_ui)
    if ac is None:
        raise ValueError(f"Aircraft '{aircraft_ui}' not found")
    fd = int(ac['id'])

    # Resolve airports
    origin_id = resolve_airport(origin_iata)
    dest_id = resolve_airport(dest_iata)

    # yd = destination, jd = origin
    return (dest_id, origin_id, fd)