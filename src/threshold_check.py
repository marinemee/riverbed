import numpy as np
import rasterio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


D = "20261111"
with rasterio.open(f"data/derived/{D}_hh_dB.tif") as raster:
    hh = raster.read(1)
with rasterio.open(f"data/derived/{D}_hv_dB.tif") as raster:
    hv = raster.read(1)
with rasterio.open("data/derived/dem.tif") as raster:
    dem = raster.read(1).astype("float32")

gy, gx = np.gradient(dem, 10)
slope = np.degrees(np.arctan(np.hypot(gx, gy)))
ok = np.isfinite(hh) & np.isfinite(hv)

print("HH percentiles 0.5/1/2/5/10:", np.nanpercentile(hh, [0.5, 1, 2, 5, 10]).round(1))
print("HV percentiles 0.5/1/2/5/10:", np.nanpercentile(hv, [0.5, 1, 2, 5, 10]).round(1))

candidates = [(-12, -19), (-10, -17), (-8, -15)]
fig, axes = plt.subplots(2, 2, figsize=(16, 16))
stride = 4
axes[0, 0].imshow(hh[::stride, ::stride], cmap="gray", vmin=-20, vmax=3)
axes[0, 0].set_title(f"{D} HH dB")
for axis, (hh_threshold, hv_threshold) in zip(axes.flat[1:], candidates):
    mask = ok & (hh < hh_threshold) & (hv < hv_threshold) & (slope < 8)
    print(
        f"HH<{hh_threshold} & HV<{hv_threshold} & slope<8 -> "
        f"water share {mask.mean() * 100:.2f}%"
    )
    axis.imshow(hh[::stride, ::stride], cmap="gray", vmin=-20, vmax=3)
    axis.imshow(
        np.ma.masked_where(~mask[::stride, ::stride], mask[::stride, ::stride]),
        cmap="autumn",
        alpha=0.9,
    )
    axis.set_title(f"HH<{hh_threshold}, HV<{hv_threshold}, slope<8")

for axis in axes.flat:
    axis.axis("off")
plt.tight_layout()
plt.savefig("data/derived/threshold_preview.png", dpi=80)
print("saved data/derived/threshold_preview.png")
