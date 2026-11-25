"""Step 1 (D1): search NISAR GCOV over the area of interest, group by track/direction/frame, optionally download.
  python pipeline/01_search_download.py                      # list only
  python pipeline/01_search_download.py --download _084_A_019_4005_DHDH_A_20261111   # any part of a scene name
Downloads need EARTHDATA_USER and EARTHDATA_PASS. Each file is ~7 GB: download only the scenes you chose.
asf_search NISAR support is still evolving: `pip install --upgrade asf_search`. If a name below fails, print(results[0].properties).
"""
import argparse, json, os
import asf_search as asf
from riverbed.config import load, bbox_wkt, RAW, DERIVED
from riverbed.nisar import group_scenes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", nargs="*", default=None, help="substrings of scene names to download")
    args = ap.parse_args()
    cfg = load()
    n = cfg["nisar"]
    results = asf.search(dataset="NISAR", processingLevel=n["processing_level"],
                         intersectsWith=bbox_wkt(cfg["aoi"]["bbox"]), start=n["start"], end=n["end"])
    urls = results.find_urls(extension=".h5", directAccess=False)
    groups = group_scenes(urls)
    for key, items in groups.items():
        print(f"\n{key}: {len(items)} scenes")
        for it in items:
            print("  ", it["start"][:8], it["pols"], it["scene"])
    DERIVED.mkdir(parents=True, exist_ok=True)
    (DERIVED / "scenes_found.json").write_text(json.dumps(groups, indent=2))
    print(f"\nSaved {DERIVED / 'scenes_found.json'}")
    if args.download:
        chosen = [u for u in urls if any(s in u for s in args.download)]
        print(f"Downloading {len(chosen)} files to {RAW} ...")
        RAW.mkdir(parents=True, exist_ok=True)
        session = asf.ASFSession().auth_with_creds(os.environ["EARTHDATA_USER"], os.environ["EARTHDATA_PASS"])
        asf.download_urls(chosen, str(RAW), session=session, processes=2)


if __name__ == "__main__":
    main()
