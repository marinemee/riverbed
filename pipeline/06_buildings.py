"""Step 6 (P2, P3): OSM buildings joined to HAND and the corridor.
TODO
 1. osmnx: features_from_bbox with building=True, tourism in [hotel, guest_house], amenity=restaurant (config aoi.bbox)
 2. Report how many were found and how complete OSM looks vs imagery (fallback: Microsoft building footprints)
 3. For each: hand_min (min HAND inside footprint), dist_m (to low-flow channel), inside_corridor (bool),
    exposure = "inside" | "near" (<= exposure.near_distance_m) | "above"
 4. Save web/data/buildings.geojson with the fields in docs/DATA_CONTRACT.md
 Neutral wording only: never label a building "illegal".
"""
raise NotImplementedError("See docstring and issues P2, P3")
