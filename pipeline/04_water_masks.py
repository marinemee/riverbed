"""Step 4 (D3): water mask per date.
TODO
 1. Open HH and HV dB tifs per scene. Light speckle filter (3x3 median).
 2. Water = dark: HH < water.hh_db_max AND HV < water.hv_db_max (config.yaml). Tune by eye on a real basemap.
 3. Remove false water from terrain shadow: drop pixels with high slope or high HAND (hand_v1.tif).
 4. Remove tiny blobs; keep only water connected to the main river.
 5. Save data/derived/water_<YYYYMMDD>.tif (uint8 0/1)
"""
raise NotImplementedError("See docstring and issue D3")
