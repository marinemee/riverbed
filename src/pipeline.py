import glob, json, os, re
import numpy as np, rasterio, geopandas as gpd
if not hasattr(np, "in1d"): np.in1d = np.isin
from rasterio.features import shapes
from scipy import ndimage as ndi
from shapely.geometry import shape

D = "data/derived/"
TH_HH, TH_HV, SLOPE_MAX, HAND_MAX_WATER, MIN_BLOB = -10, -17, 8, 15, 200
HIGH, LOW, TEST = "20260726", ["20261030", "20261111"], "20260819"

def rd(p):
    with rasterio.open(p) as r: return r.read(1), r.profile
dem, prof = rd(D + "dem.tif"); dem = dem.astype("float32")
bad = ~np.isfinite(dem) | (dem < -100)
if bad.any():
    idx = ndi.distance_transform_edt(bad, return_distances=False, return_indices=True)
    dem = dem[tuple(idx)]
gy, gx = np.gradient(dem, 10)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))
T = prof["transform"]

def wr(path, arr, dtype, nodata=None):
    p = prof.copy(); p.update(dtype=dtype, count=1, compress="deflate", nodata=nodata)
    with rasterio.open(path, "w", **p) as w: w.write(arr.astype(dtype), 1)

def clean(m, n_min):
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    keep = np.bincount(lab.ravel()) >= n_min; keep[0] = False
    return keep[lab]

def lowch(ms):
    c = ms[LOW[0]] & ms[LOW[1]]
    return c if c.sum() else (ms[LOW[0]] | ms[LOW[1]])

dates = sorted({re.search(r"(\d{8})_hh_dB\.tif", f).group(1) for f in glob.glob(D + "*_hh_dB.tif")})
print("dates:", dates)
assert HIGH in dates and all(d in dates for d in LOW), "missing dates"

# 1. raw masks (slope + blob filter)
raw = {}
for d in dates:
    hh, _ = rd(f"{D}{d}_hh_dB.tif"); hv, _ = rd(f"{D}{d}_hv_dB.tif")
    with np.errstate(invalid="ignore"):
        raw[d] = np.isfinite(hh) & np.isfinite(hv) & (hh < TH_HH) & (hv < TH_HV) & (slope < SLOPE_MAX)
    print(d, "raw water share %.2f%%" % (raw[d].mean() * 100))
    assert raw[d].mean() < 0.15, "water share too high: check dB values / thresholds"
p1 = {d: clean(raw[d], MIN_BLOB) for d in dates}
channel1 = clean(lowch(p1), 2000)
print("channel pixels (pass 1):", int(channel1.sum()))
assert channel1.sum() > 1000, "almost no river found: loosen thresholds"

# 2. HAND
hp = D + "hand.tif"
if os.path.exists(hp):
    hand = rd(hp)[0]
else:
    try:
        from pysheds.grid import Grid
        from pysheds.sview import Raster
        grid = Grid.from_raster(D + "dem.tif")
        dm = grid.read_raster(D + "dem.tif")
        filled = grid.resolve_flats(grid.fill_depressions(grid.fill_pits(dm)))
        fdir = grid.flowdir(filled)
        ch = Raster(channel1.astype(bool), viewfinder=grid.viewfinder)
        hand = np.array(grid.compute_hand(fdir, dm, ch), dtype="float32")
    except Exception as e:
        print("pysheds failed:", e, "-> Euclidean fallback (rougher)")
        _, idx = ndi.distance_transform_edt(~channel1, return_indices=True)
        hand = dem - dem[tuple(idx)]
    hand = np.where(np.isfinite(hand), np.clip(hand, 0, None), np.nan).astype("float32")
    wr(hp, hand, "float32", np.nan)
print("HAND p5/50/95:", np.nanpercentile(hand, [5, 50, 95]).round(1))

# 3. final masks
with np.errstate(invalid="ignore"):
    final = {d: clean(raw[d] & (hand < HAND_MAX_WATER), MIN_BLOB) for d in dates}
for d in dates:
    wr(f"{D}{d}_water.tif", final[d], "uint8", 255)
    print(d, "final water share %.2f%%" % (final[d].mean() * 100))
channel = lowch(final)

# 4. footprint
freq = np.mean([final[d] for d in dates], axis=0).astype("float32")
wr(D + "water_frequency.tif", freq, "float32")
wr(D + "high_flow_only.tif", final[HIGH] & ~(final[LOW[0]] | final[LOW[1]]), "uint8", 255)
union = np.any([final[d] for d in dates], axis=0)
corr = clean(ndi.binary_closing(union, structure=np.ones((3, 3)), iterations=3), 500)
wr(D + "corridor.tif", corr, "uint8", 255)
polys = [shape(g) for g, v in shapes(corr.astype("uint8"), mask=corr, transform=T)]
gdf = gpd.GeoDataFrame(geometry=polys, crs=prof["crs"])
gdf["geometry"] = gdf.geometry.simplify(10)
gdf.to_crs(4326).to_file(D + "corridor.geojson", driver="GeoJSON")
print("corridor polygons:", len(gdf))

# 5. scenarios + validation
def flood(h):
    lab, n = ndi.label((hand <= h) | channel, structure=np.ones((3, 3)))
    ids = np.unique(lab[channel]); keep = np.zeros(n + 1, bool); keep[ids[ids > 0]] = True
    return keep[lab]
def iou(a, b):
    u = (a | b).sum(); return float((a & b).sum() / u) if u else 0.0
hs = [round(x * 0.5, 1) for x in range(21)]
res = {d: {} for d in dates}
for h in hs:
    f = flood(h)
    wr(f"{D}flood_h{int(h * 10):03d}.tif", f, "uint8", 255)
    for d in dates: res[d][h] = iou(f, final[d])
    print(f"h={h:4.1f} m flooded {f.sum() * 100 / 1e6:7.2f} km2  IoU vs {HIGH}: {res[HIGH][h]:.3f}")
fit = max(hs, key=lambda h: res[HIGH][h])
val = {"fit_date": HIGH, "fit_rise_m": fit, "iou_fit": round(res[HIGH][fit], 3),
       "test_date": TEST, "iou_test": round(res[TEST][fit], 3) if TEST in dates else None,
       "iou_at_fit_by_date": {d: round(res[d][fit], 3) for d in dates},
       "iou_at_0m_by_date": {d: round(res[d][0.0], 3) for d in dates},
       "thresholds": {"hh_db": TH_HH, "hv_db": TH_HV, "slope_max_deg": SLOPE_MAX},
       "note": "approximate; DEM errors can be several metres in mountains"}
json.dump(val, open(D + "validation.json", "w"), indent=2)
print(json.dumps(val, indent=2))
ref = final[TEST if TEST in dates else HIGH]
wr(D + "agree_disagree.tif", flood(fit).astype("uint8") + 2 * ref.astype("uint8"), "uint8", 255)

# 6. buildings -> centroid points near the river
b = gpd.read_file(D + "buildings_overture.geojson").to_crs(prof["crs"])
c = b.geometry.centroid; x, y = c.x.values, c.y.values
cf, rf = ~T * (x, y); col, row = np.floor(cf).astype(int), np.floor(rf).astype(int)
H, W = hand.shape
inb = (row >= 0) & (row < H) & (col >= 0) & (col < W)
row, col = np.clip(row, 0, H - 1), np.clip(col, 0, W - 1)
dist_ch = ndi.distance_transform_edt(~channel) * 10
dist_co = ndi.distance_transform_edt(~corr) * 10
hm, dm_, ins, dco = hand[row, col], dist_ch[row, col], corr[row, col], dist_co[row, col]
expo = np.where(ins, "inside", np.where(dco <= 50, "near", "above"))
keep = inb & ((hm <= 15) | (dm_ <= 300))
o = gpd.GeoDataFrame({"hand_min": np.round(hm, 1), "dist_m": np.round(dm_).astype(int),
                      "inside_corridor": ins, "exposure": expo},
                     geometry=gpd.points_from_xy(x, y), crs=prof["crs"])[keep].to_crs(4326)
o["geometry"] = o.geometry.set_precision(1e-5)
os.makedirs("web/data", exist_ok=True)
o.to_file("web/data/buildings.geojson", driver="GeoJSON")
print("buildings kept:", len(o), o.exposure.value_counts().to_dict(),
      "size MB:", round(os.path.getsize("web/data/buildings.geojson") / 1e6, 1))

# 7. preview
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
s = 4; sub = final[HIGH][::s, ::s]
fig, ax = plt.subplots(1, 3, figsize=(24, 8))
ax[0].imshow(hand[::s, ::s], cmap="viridis", vmin=0, vmax=30); ax[0].set_title("HAND (m)")
rgb = np.zeros(sub.shape + (3,)); rgb[..., 0] = sub; rgb[..., 2] = channel[::s, ::s]
ax[1].imshow(rgb); ax[1].set_title("red = Jul 26 water, blue = low-flow water")
ax[2].imshow(freq[::s, ::s], cmap="Blues"); ax[2].set_title("water frequency")
for a in ax: a.axis("off")
plt.tight_layout(); plt.savefig(D + "pipeline_preview.png", dpi=70)
print("DONE")
