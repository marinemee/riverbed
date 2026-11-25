"""Step 2 (D2): crop every downloaded GCOV .h5 in data/raw to the area of interest -> data/derived/radar/*.tif
Open the results in QGIS and check they line up with the river before moving on."""
from riverbed.config import load, RAW, DERIVED
from riverbed.nisar import crop_gcov_to_geotiff

if __name__ == "__main__":
    cfg = load()
    for h5 in sorted(RAW.glob("NISAR_L2_*_GCOV_*.h5")):
        print("cropping", h5.name)
        crop_gcov_to_geotiff(h5, cfg["aoi"]["bbox"], DERIVED / "radar")
