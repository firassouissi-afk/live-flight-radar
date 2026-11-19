# Live Flight Radar

Fetches live aircraft positions from the OpenSky Network API and generates an animated-style Folium map with altitude colors and trails.

## Run

```powershell
pip install requests folium
python main.py
```

Open `flight_map.html`. OpenSky public API limits may apply.

The app uses OpenSky's public states endpoint and does not require a credential
for basic live aircraft data. Refreshes every 10 seconds and opens
`flight_map.html` in your browser.

**Website developed by [SOUISSI Technologies Development Group (STDG)](https://www.linkedin.com/company/souissi-technologies-development-group/home/)**

A Development Bureau for AI-Driven IT Projects. From Web Technologies to Autonomous Drones.
