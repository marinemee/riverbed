import glob
import re

import numpy as np
import rasterio
from scipy.ndimage import median_filter
from skimage.filters import threshold_otsu
from skimage.morphology import remove_small_objects


MANUAL = {}  # e.g. {"20261111": -19.0} to override Otsu after checking by eye

for filename in sorted(glob.glob("output/swat/*_h[hv]_AMP.tif")):
    date = re.search(r"_(\d{8})T\d{6}_\d{8}T", filename).group(1)
    pol = "hh" if "_hh_" in filename else "hv"
    with rasterio.open(filename) as raster:
        amplitude = raster.read(1).astype("float32")
        profile = raster.profile
        db_formula = raster.tags().get("DB_FORMULA", "")

    offset_match = re.search(
        r"20\*log10\(DN\)\s*([+-]\s*\d+(?:\.\d+)?)?", db_formula
    )
    if not offset_match:
        raise ValueError(f"Unrecognized or missing DB_FORMULA in {filename}: {db_formula!r}")
    db_offset = float(offset_match.group(1).replace(" ", "")) if offset_match.group(1) else 0.0

    bad = (amplitude <= 0) | ~np.isfinite(amplitude)
    amplitude[bad] = np.nan
    db = 20 * np.log10(amplitude) + db_offset
    filled = np.where(bad, np.nanmedian(db), db)
    db = median_filter(filled, size=3)
    db[bad] = np.nan

    profile.update(dtype="float32", nodata=np.nan, compress="deflate")
    output = f"data/derived/{date}_{pol}_dB.tif"
    with rasterio.open(output, "w", **profile) as raster:
        raster.write(db, 1)
    print(output, "p1/p50/p99:", np.nanpercentile(db, [1, 50, 99]).round(1))

    if pol == "hh":
        valid = db[~np.isnan(db)]
        threshold = MANUAL.get(date, threshold_otsu(np.clip(valid[::50], -35, 5)))
        mask = remove_small_objects((db < threshold) & ~bad, 200).astype("uint8")
        profile.update(dtype="uint8", nodata=255)
        with rasterio.open(f"data/derived/{date}_water_raw.tif", "w", **profile) as raster:
            raster.write(mask, 1)
        print(
            "  threshold",
            round(float(threshold), 1),
            "dB, water share",
            round(mask.mean() * 100, 2),
            "%",
        )
