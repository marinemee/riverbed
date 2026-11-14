# Data contract (Role 2/4 export, Role 3 loads)

All files live in `web/data/`. Rasters are PNG overlays in EPSG:4326; their bounds are in `meta.json`. A missing file means the app shows a labelled placeholder.

| File | What | Notes |
|---|---|---|
| `meta.json` | bounds, passes, rise steps, credits | see below |
| `water_frequency.png` | share of passes with water (0..1) | |
| `water_mask_<passid>.png` | water mask per pass | `passid` = YYYYMMDD |
| `radar_<passid>.png` | HH or HV backscatter, grayscale | |
| `hand.png` | height above river, colour ramp | legend in metres |
| `inundation/h_<rise>.png` | flooded area at rise `<rise>` | `h_0.0.png` ... `h_10.0.png`, 0.5 steps |
| `corridor.geojson` | observed river corridor polygon(s) | EPSG:4326 |
| `buildings.geojson` | buildings/hotels/restaurants | fields below |
| `validation.json` | model vs radar overlap | fields below |

## meta.json
```json
{
  "aoi_bbox": [72.25, 34.7, 72.65, 35.1],
  "passes": [{"id": "YYYYMMDD", "label": "Jun - high flow", "flow": "high", "scene": "NISAR_L2_...", "maturity": "PROVISIONAL"}],
  "rise_steps": [0, 0.5, 1.0],
  "credits": ["NISAR data courtesy of NASA/JPL, distributed by ASF DAAC", "..."],
  "generated": "ISO-8601 timestamp"
}
```

## buildings.geojson properties
`id`, `name` (optional), `type` ("hotel" | "restaurant" | "building"), `hand_min` (metres above nearest river channel),
`dist_m` (metres to the low-flow channel), `inside_corridor` (bool), `exposure` ("inside" | "near" | "above").
"near" means within `exposure.near_distance_m` in config.yaml.

## validation.json
`calibrated_on` (passid), `tested_on` (passid), `best_rise_m`, `iou_fit`, `iou_test`, `notes`.

Wording rule: say "inside the observed river footprint". Never "illegal" or "violation".
