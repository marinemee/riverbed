import json, os, shutil, numpy as np, rasterio
from rasterio.warp import reproject, Resampling, transform_bounds
from rasterio.transform import from_origin
from PIL import Image
import matplotlib; from matplotlib import colormaps

D, O = "data/derived/", "web/data/"
os.makedirs(O + "layers", exist_ok=True)
dem = rasterio.open(D + "dem.tif")
l, b, r, t = transform_bounds(dem.crs, "EPSG:4326", *dem.bounds)
RES = 0.0002
W, H = int(round((r - l) / RES)), int(round((t - b) / RES))
DT = from_origin(l, t, RES, RES)

def grid(path, method=Resampling.nearest):
    with rasterio.open(path) as s:
        a = s.read(1).astype("float32")
        if s.nodata is not None and not np.isnan(s.nodata): a[a == s.nodata] = np.nan
        out = np.full((H, W), np.nan, "float32")
        reproject(a, out, src_transform=s.transform, src_crs=s.crs, dst_transform=DT,
                  dst_crs="EPSG:4326", resampling=method, src_nodata=np.nan, dst_nodata=np.nan)
    return out

def save(name, rgba):
    Image.fromarray(rgba.astype("uint8")).save(O + "layers/" + name, optimize=True)

def solid(m, color, alpha):
    rgba = np.zeros((H, W, 4), "uint8"); rgba[m] = (*color, alpha); return rgba

dates = sorted(f[:8] for f in os.listdir(D) if f.endswith("_water.tif"))
for d in dates:
    save(f"water_{d}.png", solid(grid(D + f"{d}_water.tif") == 1, (20, 90, 230), 190))
    hh = grid(D + f"{d}_hh_dB.tif", Resampling.bilinear)
    g = np.clip((hh + 25) / 30, 0, 1) * 255
    save(f"radar_hh_{d}.png", np.dstack([g, g, g, np.where(np.isnan(hh), 0, 255)]))
    hv = grid(D + f"{d}_hv_dB.tif", Resampling.bilinear)
    g = np.clip((hv + 30) / 30, 0, 1) * 255
    save(f"radar_hv_{d}.png", np.dstack([g, g, g, np.where(np.isnan(hv), 0, 255)]))

fq = np.nan_to_num(grid(D + "water_frequency.tif"))
rgba = (colormaps["Blues"](np.clip(fq, 0, 1)) * 255); rgba[..., 3] = np.where(fq > 0, 210, 0)
save("water_frequency.png", rgba)

hand = grid(D + "hand.tif", Resampling.bilinear)
rgba = colormaps["viridis"](np.clip(np.nan_to_num(hand, nan=30) / 30, 0, 1)) * 255
rgba[..., 3] = np.where(np.isnan(hand) | (hand > 30), 0, 170)
save("hand.png", rgba)

ad = np.nan_to_num(grid(D + "agree_disagree.tif"))
rgba = np.zeros((H, W, 4), "uint8")
rgba[ad == 1] = (230, 150, 20, 200); rgba[ad == 2] = (150, 60, 200, 200); rgba[ad == 3] = (30, 160, 80, 200)
save("agree_disagree.png", rgba)

hs = [round(x * 0.5, 1) for x in range(21)]
for h in hs:
    save(f"flood_{int(h * 10):03d}.png", solid(grid(D + f"flood_h{int(h * 10):03d}.tif") == 1, (30, 110, 230), 170))

shutil.copy(D + "corridor.geojson", O + "corridor.geojson")
shutil.copy(D + "validation.json", O + "validation.json")
if os.path.exists(D + "osm_check.geojson"): shutil.copy(D + "osm_check.geojson", O + "osm_features.geojson")

meta = {"bounds": [l, b, r, t],
        "coordinates": [[l, t], [r, t], [r, b], [l, b]],
        "dates": {"20260726": "high flow (provisional)", "20260819": "high flow (provisional)",
                  "20261030": "low flow", "20261111": "low flow"},
        "rise_steps_m": hs,
        "files": {"flood": "layers/flood_{h*10:03d}.png", "water": "layers/water_{date}.png",
                  "radar_hh": "layers/radar_hh_{date}.png", "radar_hv": "layers/radar_hv_{date}.png",
                  "frequency": "layers/water_frequency.png", "hand": "layers/hand.png",
                  "agree": "layers/agree_disagree.png", "corridor": "corridor.geojson",
                  "buildings": "buildings.geojson", "validation": "validation.json"},
        "credits": ["NISAR data courtesy of NASA/JPL, distributed by ASF DAAC.",
                    "NASA JPL (2020). NASADEM Merged DEM Global 1 arc second V001. NASA EOSDIS Land Processes DAAC. doi:10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001",
                    "© OpenStreetMap contributors.",
                    "Building footprints: Overture Maps Foundation (check exact attribution)."]}
json.dump(meta, open(O + "meta.json", "w"), indent=2)
print("done; bounds", meta["bounds"], "image", W, "x", H)
