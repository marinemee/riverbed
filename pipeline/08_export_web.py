"""Export existing src/pipeline.py results; never run or approximate the model.

Run from any directory: python pipeline/08_export_web.py [--max-size 1600]
Missing inputs abort before writing anything. PNGs share one EPSG:4326 grid;
meta.json records its actual bounds, display scales and source filenames.
"""

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
OUTPUT = ROOT / "web" / "data"
# Dates and flood_hNNN.tif convention used by src/pipeline.py / DATA_SOURCES.md.
REQUIRED_DATES = ("20260726", "20260819", "20261030", "20261111")
RISES = [n / 2 for n in range(21)]
MAX_BYTES = 40_000_000


class ExportError(Exception):
    """An input or output does not meet the data contract."""


def read_json(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ExportError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ExportError(f"{path}: expected a JSON object")
    return value


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False,
                               separators=(",", ":")) + "\n", encoding="utf-8")


def inputs():
    # Include unpaired files, so a missing radar or water mask cannot hide a pass.
    dates = set(REQUIRED_DATES)
    validation_path = DERIVED / "validation.json"
    if validation_path.is_file():
        scores = read_json(validation_path)
        # Keep unmeasured scores null. Any additional measured validation date
        # also requires its corresponding real inputs, beyond the four selected.
        keys = ["fit_date"] + (["test_date"] if scores.get("iou_test") is not None else [])
        for key in keys:
            date = scores.get(key)
            if isinstance(date, str) and re.fullmatch(r"\d{8}", date):
                dates.add(date)
    for pattern, suffix in (("*_hh_dB.tif", "_hh_dB.tif"),
                            ("*_water.tif", "_water.tif")):
        for path in DERIVED.glob(pattern):
            date = path.name.removesuffix(suffix)
            if re.fullmatch(r"\d{8}", date):
                dates.add(date)
    dates = sorted(dates)
    rasters = {"water_frequency.png": DERIVED / "water_frequency.tif",
               "hand.png": DERIVED / "hand.tif"}
    for date in dates:
        rasters[f"water_mask_{date}.png"] = DERIVED / f"{date}_water.tif"
        rasters[f"radar_{date}.png"] = DERIVED / f"{date}_hh_dB.tif"
    for rise in RISES:
        rasters[f"inundation/h_{rise:.1f}.png"] = (
            DERIVED / f"flood_h{round(rise * 10):03d}.tif")
    required = [*rasters.values(), DERIVED / "corridor.geojson",
                DERIVED / "validation.json", OUTPUT / "buildings.geojson",
                DERIVED / "scenes_found.json", ROOT / "config.yaml"]
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise ExportError("Missing required input(s):\n" +
                          "\n".join(f"  {path}" for path in missing) +
                          "\nRun the upstream processing first. No files were exported.")
    return dates, rasters


def number(value, field, path, minimum=0, maximum=None, nullable=False):
    if value is None and nullable:
        return value
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or
            not math.isfinite(value) or value < minimum or
            (maximum is not None and value > maximum)):
        raise ExportError(f"{path}: invalid {field}: {value!r}")
    return value


def validation(dates):
    path = DERIVED / "validation.json"
    source = read_json(path)
    # Translate the actual upstream keys without recalculating or rounding scores.
    required = ("fit_date", "test_date", "fit_rise_m", "iou_fit", "iou_test", "note")
    missing = [key for key in required if key not in source]
    if missing:
        raise ExportError(f"{path}: missing fields: {', '.join(missing)}")
    fit, test = source["fit_date"], source["test_date"]
    if (fit not in dates or not isinstance(test, str) or
            not re.fullmatch(r"\d{8}", test) or fit == test or
            (source["iou_test"] is not None and test not in dates)):
        raise ExportError(f"{path}: fit_date and test_date must identify different passes; "
                          "measured overlap requires an exported pass")
    rise = number(source["fit_rise_m"], "fit_rise_m", path, maximum=10)
    if rise not in RISES:
        raise ExportError(f"{path}: fit_rise_m {rise} has no scenario frame")
    notes = source["note"]
    if not isinstance(notes, str):
        raise ExportError(f"{path}: note must be text")
    if source["iou_test"] is None:
        notes += " Held-out overlap was not measured in the upstream results."
    return {"calibrated_on": fit, "tested_on": test, "best_rise_m": rise,
            "iou_fit": number(source["iou_fit"], "iou_fit", path, maximum=1),
            "iou_test": number(source["iou_test"], "iou_test", path,
                               maximum=1, nullable=True), "notes": notes}


def orbit_group(metadata, path, context):
    missing = [key for key in ("track", "direction", "frame") if key not in metadata]
    if missing:
        raise ExportError(f"{path}: {context} is missing metadata: {', '.join(missing)}")
    direction = str(metadata["direction"]).strip().upper()
    directions = {"A": "A", "ASCENDING": "A", "D": "D", "DESCENDING": "D"}
    if direction not in directions:
        raise ExportError(f"{path}: {context} has invalid direction {metadata['direction']!r}")
    for key in ("track", "frame"):
        if isinstance(metadata[key], bool) or not re.fullmatch(r"\d+", str(metadata[key])):
            raise ExportError(f"{path}: {context} has invalid {key} {metadata[key]!r}")
    return int(metadata["track"]), directions[direction], int(metadata["frame"])


def passes(dates, config):
    path = DERIVED / "scenes_found.json"
    expected_group = orbit_group(config["nisar"], ROOT / "config.yaml", "nisar")
    track, direction, frame = expected_group
    group = f"T{track:03d}_{direction}_F{frame:03d}"
    catalog = read_json(path)
    if "scenes" in catalog:
        actual_group = orbit_group(catalog, path, "catalog")
        if actual_group != expected_group:
            raise ExportError(f"{path}: catalog track/direction/frame {actual_group} "
                              f"does not match configured {group}")
        records, date_field = catalog["scenes"], "date"
    else:
        # Retain support for the grouped catalog written by step 01.
        records, date_field = catalog.get(group), "start"
    if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
        raise ExportError(f"{path}: expected a scenes list with date fields, or a {group} list "
                          "with start fields")
    result = []
    for date in dates:
        matches = [record for record in records
                   if isinstance(record.get(date_field), str) and record[date_field][:8] == date]
        if len(matches) != 1:
            raise ExportError(f"{path}: expected one scene for {date} in {group}; "
                              f"found {len(matches)}. Resolve scene provenance before exporting.")
        record = matches[0]
        scene = record.get("scene")
        # Same scene-name fields as src/riverbed/nisar.py; verify the catalog's
        # group and acquisition date against the actual, unmodified scene ID.
        identity = re.match(
            r"^NISAR_L2_[^_]+_GCOV_\d+_(\d+)_([AD])_(\d+)_"
            r"[^_]+_[^_]+_[^_]+_(\d{8})T\d{6}_", scene or "")
        if identity is None:
            raise ExportError(f"{path}: {date} has a missing or invalid scene ID; "
                              "cannot verify track, direction, frame and acquisition date")
        scene_track, scene_direction, scene_frame, scene_date = identity.groups()
        if ((int(scene_track), scene_direction, int(scene_frame)) != expected_group or
                scene_date != date):
            raise ExportError(f"{path}: scene {scene} does not match {group} on {date}")
        # Flow and maturity come only from explicit catalog metadata. In the
        # copied catalog they are the two comma-separated parts of 'role'.
        role = record.get("role", "")
        role_parts = [part.strip().lower() for part in role.split(",")] if isinstance(role, str) else []
        flow = record.get("flow")
        maturity = record.get("maturity")
        if flow is None and role_parts and role_parts[0] in ("high flow", "low flow"):
            flow = role_parts[0].split()[0]
        if maturity is None and len(role_parts) == 2 and role_parts[1]:
            maturity = role_parts[1]
        if not isinstance(flow, str) or flow.lower() not in ("high", "low"):
            raise ExportError(f"{path}: {date} is missing high/low flow metadata "
                              "in flow or role; it cannot be inferred from the date")
        if not isinstance(maturity, str) or not maturity.strip():
            raise ExportError(f"{path}: {date} is missing maturity metadata in maturity or role")
        flow, maturity = flow.lower(), maturity.strip().upper()
        label = datetime.strptime(date, "%Y%m%d").strftime("%d %b %Y")
        label += f" - {flow} flow"
        result.append({"id": date, "label": label, "flow": flow,
                       "scene": scene, "maturity": maturity})
    return result


def normalize_buildings(features, path):
    ids = set()
    for index, feature in enumerate(features):
        properties = feature.get("properties") or {}
        # src/pipeline.py drops identity/category columns. Supply export-local IDs
        # and the generic building category; do not guess names or business types.
        properties.setdefault("id", feature.get("id", f"building-{index}"))
        properties.setdefault("type", "building")
        identifier = properties["id"]
        if not isinstance(identifier, (str, int)) or isinstance(identifier, bool):
            raise ExportError(f"{path}: feature {index} has invalid id")
        if identifier in ids:
            raise ExportError(f"{path}: duplicate building id {identifier!r}")
        ids.add(identifier)
        if properties["type"] not in ("hotel", "restaurant", "building"):
            raise ExportError(f"{path}: building {identifier} has invalid type")
        for key in ("hand_min", "dist_m", "inside_corridor", "exposure"):
            if key not in properties:
                raise ExportError(f"{path}: building {identifier} is missing {key}")
        # Preserve unknown HAND as JSON null, as in the actual processed file.
        number(properties["hand_min"], "hand_min", path, nullable=True)
        number(properties["dist_m"], "dist_m", path)
        inside, exposure = properties["inside_corridor"], properties["exposure"]
        if (not isinstance(inside, bool) or exposure not in ("inside", "near", "above")
                or inside != (exposure == "inside")):
            raise ExportError(f"{path}: building {identifier} has inconsistent exposure")
        feature["properties"] = properties


def geojson(path, buildings=False):
    from rasterio.crs import CRS
    from rasterio.warp import transform_geom

    collection = read_json(path)
    if collection.get("type") != "FeatureCollection":
        raise ExportError(f"{path}: expected a GeoJSON FeatureCollection")
    crs = CRS.from_user_input(collection.get("crs", {}).get("properties", {}).get(
        "name", "EPSG:4326"))
    features = collection.get("features")
    if not isinstance(features, list):
        raise ExportError(f"{path}: features must be an array")
    allowed = ("Point", "MultiPoint", "Polygon", "MultiPolygon") if buildings else (
        "Polygon", "MultiPolygon")
    for index, feature in enumerate(features):
        geometry = feature.get("geometry")
        if not geometry or geometry.get("type") not in allowed:
            raise ExportError(f"{path}: feature {index} has invalid geometry")
        if crs != CRS.from_epsg(4326):
            feature["geometry"] = transform_geom(crs, "EPSG:4326", geometry)
    if buildings:
        normalize_buildings(features, path)
    # RFC 7946 GeoJSON is always longitude/latitude; remove legacy CRS/bbox hints.
    return {"type": "FeatureCollection", "features": features}


def grid(path, max_size):
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.warp import calculate_default_transform, transform_bounds

    with rasterio.open(path) as source:
        if source.crs is None:
            raise ExportError(f"{path}: missing raster CRS")
        bounds = transform_bounds(source.crs, "EPSG:4326", *source.bounds, densify_pts=21)
        _, width, height = calculate_default_transform(
            source.crs, "EPSG:4326", source.width, source.height, *source.bounds)
    scale = min(1, max_size / max(width, height))
    width, height = max(1, round(width * scale)), max(1, round(height * scale))
    return bounds, from_bounds(*bounds, width, height), width, height


def overlay(source_path, target_path, kind, target_grid):
    import numpy as np
    import rasterio
    from rasterio.enums import ColorInterp, Resampling
    from rasterio.vrt import WarpedVRT
    from matplotlib import colormaps

    _, transform, width, height = target_grid
    binary = kind in ("water_mask", "inundation")
    with rasterio.open(source_path) as source:
        if source.crs is None or source.count != 1:
            raise ExportError(f"{source_path}: expected one band with a CRS")
        with WarpedVRT(source, crs="EPSG:4326", transform=transform,
                       width=width, height=height, dtype="float32", nodata=float("nan"),
                       resampling=Resampling.nearest if binary else Resampling.bilinear) as vrt:
            data = vrt.read(1, masked=True).filled(np.nan)
    valid = np.isfinite(data)
    if not valid.any():
        raise ExportError(f"{source_path}: no valid pixels within the export bounds")
    if binary and not np.isin(data[valid], [0, 1]).all():
        raise ExportError(f"{source_path}: expected binary values 0/1 (with declared nodata)")
    if kind == "water_frequency" and ((data[valid] < 0) | (data[valid] > 1)).any():
        raise ExportError(f"{source_path}: water frequency must be between 0 and 1")
    if kind == "hand" and (data[valid] < 0).any():
        raise ExportError(f"{source_path}: HAND must be nonnegative metres")
    values = np.where(valid, data, 0)
    if binary:
        rgba = np.zeros((height, width, 4), dtype="uint8")
        rgba[..., :3] = [30, 136, 229]
        rgba[..., 3] = np.where(valid & (values == 1), 210, 0)
    elif kind == "radar":
        gray = np.rint(np.clip((values + 35) / 40, 0, 1) * 255).astype("uint8")
        rgba = np.empty((height, width, 4), dtype="uint8")
        rgba[..., :3] = gray[..., None]
        rgba[..., 3] = valid.astype("uint8") * 255
    else:
        normalized = values / 30 if kind == "hand" else values
        cmap = "viridis" if kind == "hand" else "Blues"
        rgba = colormaps[cmap](np.clip(normalized, 0, 1), bytes=True)
        rgba[..., 3] = (valid & ((values > 0) if kind == "water_frequency" else True)) * 255
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(target_path, "w", driver="PNG", width=width, height=height,
                       count=4, dtype="uint8", zlevel=9) as target:
        target.write(np.moveaxis(rgba, -1, 0))
        target.colorinterp = (ColorInterp.red, ColorInterp.green,
                              ColorInterp.blue, ColorInterp.alpha)


def export(max_size):
    # Check paths before importing optional GIS dependencies or touching outputs.
    dates, rasters = inputs()
    import yaml

    with (ROOT / "config.yaml").open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    scenario = config["scenario"]
    if [scenario[k] for k in ("rise_min_m", "rise_max_m", "rise_step_m")] != [0, 10, 0.5]:
        raise ExportError(f"{ROOT / 'config.yaml'}: scenario must match the processed "
                          "0..10 m frames in 0.5 m steps")
    metadata_passes = passes(dates, config)
    scores = validation(dates)
    corridor = geojson(DERIVED / "corridor.geojson")
    buildings = geojson(OUTPUT / "buildings.geojson", buildings=True)
    target_grid = grid(DERIVED / "water_frequency.tif", max_size)
    bounds, _, width, height = target_grid
    meta = {"aoi_bbox": list(bounds), "passes": metadata_passes, "rise_steps": RISES,
            "credits": ["NISAR data courtesy of NASA/JPL, distributed by ASF DAAC",
                        "NASA JPL (2020). NASADEM HGT V001. doi:10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001",
                        "\u00a9 OpenStreetMap contributors, Overture Maps Foundation",
                        "Overture buildings: ODbL 1.0 (https://opendatacommons.org/licenses/odbl/1-0/); "
                        "source attributions: https://docs.overturemaps.org/attribution/#buildings"],
            "generated": datetime.now(timezone.utc).isoformat(),
            "raster_crs": "EPSG:4326", "raster_size": [width, height],
            "legends": {"water_frequency": {"min": 0, "max": 1, "unit": "share", "cmap": "Blues"},
                        "hand": {"min": 0, "max": 30, "unit": "m", "cmap": "viridis", "clipped": True},
                        "radar": {"min": -35, "max": 5, "unit": "dB", "band": "HH", "clipped": True}},
            "sources": {name: path.relative_to(ROOT).as_posix() for name, path in rasters.items()}}
    # Stage every result first: corrupt/missing input or an oversize export leaves
    # the previously published files intact. Publish meta.json last.
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="riverbed-export-", dir=OUTPUT.parent) as temporary:
        stage = Path(temporary)
        for name, source in rasters.items():
            kind = ("inundation" if name.startswith("inundation/") else
                    "water_mask" if name.startswith("water_mask_") else
                    "radar" if name.startswith("radar_") else Path(name).stem)
            overlay(source, stage / name, kind, target_grid)
        for name, value in (("corridor.geojson", corridor), ("buildings.geojson", buildings),
                            ("validation.json", scores), ("meta.json", meta)):
            write_json(stage / name, value)
        files = sorted(path for path in stage.rglob("*") if path.is_file())
        names = {path.relative_to(stage) for path in files}
        total = sum(path.stat().st_size for path in files)
        total += sum(path.stat().st_size for path in OUTPUT.rglob("*")
                     if path.is_file() and path.relative_to(OUTPUT) not in names)
        if total >= MAX_BYTES:
            raise ExportError(f"Export would occupy {total / 1e6:.1f} MB in {OUTPUT}; "
                              "limit is 40 MB. Try a smaller --max-size.")
        for path in sorted(files, key=lambda path: path.name == "meta.json"):
            destination = OUTPUT / path.relative_to(stage)
            destination.parent.mkdir(parents=True, exist_ok=True)
            path.replace(destination)
    print(f"Exported {len(files)} files to {OUTPUT} ({total / 1e6:.1f} MB).")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-size", type=int, default=1600,
                        help="maximum PNG width/height in pixels (default: 1600)")
    args = parser.parse_args()
    if args.max_size <= 0:
        parser.error("--max-size must be positive")
    try:
        export(args.max_size)
    except ImportError as exc:
        print(f"Export stopped: {exc}. Install the environment in environment.yml.", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Export stopped: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
