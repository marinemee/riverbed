"""Helpers for NISAR GCOV products. STARTER CODE: test on ONE scene first and fix what breaks.
Layer paths follow ASF's NISAR docs: /science/LSAR/GCOV/grids/frequencyA/{HHHH,HVHV,mask,projection,xCoordinates,yCoordinates}
"""
from collections import defaultdict
from pathlib import Path

BASE = "/science/LSAR/GCOV/grids/frequencyA/"


def parse_scene_name(name):
    """NISAR_L2_PR_GCOV_035_084_A_019_4005_DHDH_A_20261111T002237_..._001(.h5)"""
    base = Path(str(name)).name.replace(".h5", "")
    p = base.split("_")
    return {"scene": base, "cycle": int(p[4]), "track": int(p[5]), "direction": p[6],
            "frame": int(p[7]), "pols": p[9], "start": p[11]}


def group_scenes(urls):
    """Group scenes that can be compared: same track + direction + frame."""
    groups = defaultdict(list)
    for u in urls:
        info = parse_scene_name(u)
        info["url"] = u
        groups[f"T{info['track']:03d}_{info['direction']}_F{info['frame']:03d}"].append(info)
    for v in groups.values():
        v.sort(key=lambda d: d["start"])
    return dict(sorted(groups.items()))


def crop_gcov_to_geotiff(h5_path, bbox, out_dir, bands=("HHHH", "HVHV")):
    """Crop a local GCOV .h5 to bbox (west, south, east, north in EPSG:4326).
    Writes <scene>_<band>_dB.tif (float32) and <scene>_mask.tif. Check the mask meaning in the NISAR Data User Guide."""
    import h5py
    import numpy as np
    import rasterio
    from pyproj import Transformer
    from rasterio.transform import from_origin

    h5_path, out_dir = Path(h5_path), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scene = h5_path.stem
    with h5py.File(h5_path, "r") as f:
        g = f[BASE]
        epsg = int(g["projection"][()])
        x, y = g["xCoordinates"][:], g["yCoordinates"][:]
        tr = Transformer.from_crs(4326, epsg, always_xy=True)
        w, s, e, n = bbox
        pts = [tr.transform(lon, lat) for lon in (w, e) for lat in (s, n)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        ix = np.where((x >= min(xs)) & (x <= max(xs)))[0]
        iy = np.where((y >= min(ys)) & (y <= max(ys)))[0]
        if ix.size == 0 or iy.size == 0:
            raise ValueError(f"{scene}: area of interest is outside this scene")
        sl = (slice(iy.min(), iy.max() + 1), slice(ix.min(), ix.max() + 1))
        dx, dy = float(x[1] - x[0]), float(y[1] - y[0])
        assert dy < 0, "expected y to decrease downwards; check the layout"
        transform = from_origin(x[ix.min()] - dx / 2, y[iy.min()] - dy / 2, dx, abs(dy))
        prof = dict(driver="GTiff", height=sl[0].stop - sl[0].start, width=sl[1].stop - sl[1].start,
                    count=1, crs=f"EPSG:{epsg}", transform=transform, compress="deflate")
        for b in bands:
            arr = g[b][sl].astype("float32")
            with np.errstate(divide="ignore", invalid="ignore"):
                db = np.where(arr > 0, 10 * np.log10(arr), -9999).astype("float32")
            with rasterio.open(out_dir / f"{scene}_{b}_dB.tif", "w", dtype="float32", nodata=-9999, **prof) as dst:
                dst.write(db, 1)
        if "mask" in g:
            with rasterio.open(out_dir / f"{scene}_mask.tif", "w", dtype="uint8", **prof) as dst:
                dst.write(g["mask"][sl].astype("uint8"), 1)
    return scene
