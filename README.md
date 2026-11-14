# Riverbed

**Where does the Swat River really go, and who is standing in its way?**
A web map built with NASA NISAR L-band radar for the 2026 NASA Space Apps Challenge, "Dancing with the SARs".

Design mockups: https://claude.ai/artifact/5kTFLofJZwSEWCEEyED9UP

## What it shows
1. Observed river footprint from NISAR radar (high flow vs low flow).
2. Height above the river (HAND) from NASADEM elevation.
3. Buildings from OpenStreetMap, grouped by exposure.
4. A "river rises X metres" slider with a live building count.

It shows **exposure, not predicted floods or timing.** See `docs/METHOD.md`.

## Repo layout
```
config.yaml        area of interest, dates, scene choice, thresholds
src/riverbed/      shared helpers (config, NISAR reading)
pipeline/          numbered data steps, run in order (01 -> 08)
web/               the static site (deployed on Vercel, Root Directory = web)
web/data/          small exported files the site loads (see docs/DATA_CONTRACT.md)
data/              raw + derived data, NOT in git (see data/README.md)
docs/              method, data sources, data contract, contributing
scripts/           issue creation helpers
```

## Quick start
```bash
conda env create -f environment.yml && conda activate riverbed
pip install -e .
export EARTHDATA_USER=your_username EARTHDATA_PASS=your_password   # free NASA Earthdata login

python pipeline/01_search_download.py            # list NISAR scenes grouped by track/direction/frame
python pipeline/01_search_download.py --download <part-of-scene-name>   # ~7 GB each
python pipeline/02_crop_gcov.py                  # crop to the area of interest
```
Run the web app locally: `cd web && python -m http.server 8000`, then open http://localhost:8000

## Team and issues
Issues are labelled by role (`role-1-mgmt`, `role-2-data`, `role-3-frontend`, `role-4-deploy`) and priority (`must`, `should`).
Create them all with `python scripts/create_issues.py` (needs the GitHub CLI) or paste from `docs/ISSUES.md`.
Rules are in `docs/CONTRIBUTING.md`.

## Credits
- NISAR data courtesy of NASA/JPL, distributed by ASF DAAC.
- NASA JPL (2020). NASADEM Merged DEM Global 1 arc second V001. NASA EOSDIS Land Processes DAAC. doi:10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001
- Building data: (c) OpenStreetMap contributors.

## License
MIT for code (see LICENSE). Data keeps its original licenses.
