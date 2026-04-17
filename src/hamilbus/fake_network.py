from fastapi import FastAPI
from .datamodels import Line, Stop, BusNetworkGraph

def _create_fake_network() -> tuple[dict[int, Stop], dict[int, Line]]:
    """Create a fake bus network for demonstration purposes."""
    stops = {}
    lines = {}

    # Create fake stops around Paris area
    fake_stops_data = [
        (1000001, "Gare du Nord", "parent_station", 48.8809, 2.3553),
        (1000002, "Châtelet", "parent_station", 48.8584, 2.3471),
        (1000003, "Bastille", "parent_station", 48.8534, 2.3691),
        (1000004, "Montparnasse", "parent_station", 48.8378, 2.3184),
        (1000005, "Opéra", "parent_station", 48.8709, 2.3317),
        (1000006, "République", "parent_station", 48.8676, 2.3636),
        (1000007, "Nation", "parent_station", 48.8485, 2.3958),
        (1000008, "Porte Maillot", "parent_station", 48.8777, 2.2824),
        (1000009, "La Défense", "parent_station", 48.8919, 2.2379),
        (1000010, "Gare de Lyon", "parent_station", 48.8443, 2.3735),
    ]

    for index, name, stop_type, lat, lon in fake_stops_data:
        stops[index] = Stop(
            index=index,
            name=name,
            type=stop_type,
            lat=lat,
            lon=lon,
            lines=[],
            parent_station_idx=None,
        )

    # Create fake lines
    fake_lines_data = [
        (0, "Ligne 1", "Château de Vincennes ↔ La Défense", "#FF0000", [1000001, 1000005, 1000002, 1000006, 1000007]),
        (1, "Ligne 2", "Porte Dauphine ↔ Nation", "#0000FF", [1000008, 1000005, 1000002, 1000006, 1000007]),
        (2, "Ligne 3", "Pont de Levallois ↔ Gallieni", "#00FF00", [1000009, 1000008, 1000005, 1000002, 1000003]),
        (3, "Ligne 4", "Porte de Clignancourt ↔ Mairie de Montrouge", "#FFFF00", [1000001, 1000005, 1000002, 1000004]),
        (4, "Ligne 5", "Bobigny ↔ Place d'Italie", "#FF00FF", [1000006, 1000002, 1000003, 1000010]),
    ]

    for index, name, long_name, color, stop_indices in fake_lines_data:
        line_stops = [stops[idx] for idx in stop_indices if idx in stops]
        # Create shape from stop coordinates
        shape = [(stop.lon, stop.lat) for stop in line_stops]
        lines[index] = Line(
            index=index,
            name=name,
            long_name=long_name,
            color=color,
            shape=shape,
            stops=line_stops,
        )
        # Update stop lines
        for stop in line_stops:
            if index not in stop.lines:
                stop.lines.append(index)

    return stops, lines