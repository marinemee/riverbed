Exported files the site loads. Format is defined in docs/DATA_CONTRACT.md. Keep this folder under ~40 MB.
Until the pipeline exports real files, the app shows labelled placeholders.

Run `python pipeline/08_export_web.py` from the repository root after
`src/pipeline.py` has finished. The exporter also works from another working
directory when invoked by its full path. It reads these existing inputs:

- `data/derived/water_frequency.tif`, `hand.tif`, and `corridor.geojson`.
- `data/derived/<YYYYMMDD>_hh_dB.tif` and `<YYYYMMDD>_water.tif` for each pass,
  including all four selected scenes: high-flow passes `20260726` and `20260819`,
  and low-flow passes `20261030` and `20261111`.
- `data/derived/flood_h000.tif`, `flood_h005.tif`, ... `flood_h100.tif`.
- `data/derived/validation.json` with the keys written by `src/pipeline.py`.
- `data/derived/scenes_found.json` to identify the source scene for each date.
  The copied catalog has top-level `track`, `direction`, `frame`, and a `scenes`
  list with `date`, `scene`, and `role` fields. Direction is case-insensitive
  (`ascending` or `A`). The exporter checks each scene ID against the configured
  orbit group and date. It reads flow/maturity from the catalog's `role` text
  (for example, `high flow, provisional`) or explicit `flow`/`maturity` fields.
  The grouped `T084_A_F019`/`start` format from step 01 is also accepted, but
  needs explicit flow/maturity metadata; these values are never guessed.
- `web/data/buildings.geojson` already written by `src/pipeline.py`.

Missing inputs produce a nonzero exit with every exact expected path before any
output is written. The exporter never creates replacement measurements. It
preserves unknown building HAND and unmeasured test overlap as `null`; it adds
unique export-local building IDs and uses `type: "building"` where the upstream
file has no category.

All PNGs share EPSG:4326 bounds recorded in `meta.json.aoi_bbox`, derived from
the real frequency raster. Binary masks use nearest-neighbour resampling;
continuous layers use bilinear resampling. Nodata is transparent, as are dry
pixels in the water/flood layers. `meta.json.legends` describes the display
scales: frequency 0 to 1, HAND 0 to 30 m (viridis), radar HH -35 to 5 dB (grayscale).
Values outside the HAND/radar display scales are clipped for display only.

Outputs are staged and checked against the 40 MB folder budget before replacing
published files. The default maximum PNG dimension is 1600 pixels; use
`--max-size 1200` for smaller exports. Validation scores are mapped directly to
the contract fields without recomputation.

The metadata field names are `aoi_bbox`, `passes`, `rise_steps`, `credits`, and
`generated`, as specified in `docs/DATA_CONTRACT.md`. `web/app.js` uses these
bounds and pass/rise choices to load the exported PNGs, corridor and buildings.
The slider selects the actual `inundation/h_<rise>.png` for each metadata level.
Building counts sample the selected PNG's alpha at exported building points;
they do not treat a missing HAND value as zero or assume all low-HAND points
are connected to inundation. Missing layers are labeled unavailable in the UI.
See `docs/DATA_SOURCES.md` for the verified Overture credit and the remaining
source-provenance check before publication.
