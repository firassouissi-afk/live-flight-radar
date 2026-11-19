import os
import time
import webbrowser
from collections import defaultdict, deque
from pathlib import Path

import requests
import folium
from folium.plugins import AntPath

URL = "https://opensky-network.org/api/states/all"
OUTPUT_FILE = Path(__file__).with_name("flight_map.html")
trails = defaultdict(lambda: deque(maxlen=12))

def fetch_flights():
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"OpenSky request failed: {exc}") from exc

    payload = response.json()
    states = payload.get("states") or []
    flights = []
    for state in states:
        if state[5] is None or state[6] is None:
            continue
        flights.append(dict(
            icao24=state[0],
            callsign=(state[1] or "").strip(),
            country=state[2] or "Unknown",
            lon=state[5],
            lat=state[6],
            altitude=state[7],
            velocity=state[9],
            heading=state[10],
        ))
    return flights

def create_map(flights):
    m = folium.Map(location=[30, 10], zoom_start=3, tiles="OpenStreetMap", control_scale=True)
    active_flight_ids = set()
    for f in flights[:5000]:
        active_flight_ids.add(f["icao24"])
        alt = f["altitude"] or 0
        color = "#00e5ff" if alt < 3000 else "#7c4dff" if alt < 8000 else "#ffb300"
        velocity = f["velocity"] or 0
        popup = (
            f"<b>{f['callsign'] or f['icao24']}</b><br>"
            f"{f['country']}<br>"
            f"Altitude: {alt:,.0f} m<br>"
            f"Speed: {velocity * 3.6:,.0f} km/h"
        )
        folium.CircleMarker([f["lat"], f["lon"]], radius=4, color=color,
                            fill=True, fill_opacity=.9, popup=popup).add_to(m)
        trail = trails[f["icao24"]]
        point = [f["lat"], f["lon"]]
        if not trail or trail[-1] != point:
            trail.append(point)
        if len(trail) > 1:
            AntPath(trail[-12:], color=color, weight=1, opacity=.7).add_to(m)

    return m

def refresh():
    flights = fetch_flights()
    create_map(flights).save(str(OUTPUT_FILE))
    print(f"{time.strftime('%H:%M:%S')} - mapped {len(flights):,} aircraft")
    return flights

if __name__ == "__main__":
    try:
        refresh()
        webbrowser.open(OUTPUT_FILE.as_uri())
        for cycle in range(2, 121):
            time.sleep(10)
            refresh()
    except KeyboardInterrupt:
        print("\nFlight radar stopped.")
    except RuntimeError as exc:
        print(exc)
