import glob

import rasterio


ref = None
for filename in sorted(glob.glob("output/swat/*.tif")):
    with rasterio.open(filename) as raster:
        signature = (
            str(raster.crs),
            raster.shape,
            tuple(round(value, 3) for value in raster.transform[:6]),
        )
        print(
            filename.split("/")[-1],
            signature,
            "bounds:", [round(value, 3) for value in raster.bounds],
        )
        ref = ref or signature
        if signature != ref:
            print("  ^ DIFFERENT GRID from first file")
