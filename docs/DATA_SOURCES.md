# Locked data sources

| Data | Use | Link |
|---|---|---|
| NISAR L2 GCOV (HH, HV) | river footprint | https://search.asf.alaska.edu/ , product: https://www.earthdata.nasa.gov/data/catalog/asf-nisar-l2-gcov-v1-1 |
| NASADEM HGT V001 (30 m) | slope, HAND | https://www.earthdata.nasa.gov/data/catalog/lpcloud-nasadem-hgt-001 , doi:10.5067/MEaSUREs/NASADEM/NASADEM_HGT.001 |
| OpenStreetMap | buildings | https://www.openstreetmap.org/ |
| Sentinel-1 (backup) | high-flow pass if NISAR dates do not pair | https://search.asf.alaska.edu/ |

NISAR docs: https://nisar-docs.asf.alaska.edu/ . Code examples: https://asfopensarlab.github.io/NISAR_Cookbook/ . Tools: https://openseppo.readthedocs.io/en/latest/

## Scenes chosen (fill in at issue D1)
- Confirmed so far: NISAR_L2_PR_GCOV_035_084_A_019_4005_DHDH_A_20261111T002237_20261111T002311_P05036_N_F_J_001 (Nov 11 2026, track 84, ascending, HH+HV, validated)
- High-flow (June) scene on the same track/frame: TODO

## Scenes used (Track 84, ascending, Frame 19, GCOV DHDH)
- 2026-07-26 and 2026-08-19 (high flow, PROVISIONAL); 2026-10-30 and 2026-11-11 (low flow, validated)
- No June pass on this track; "high flow" here means July/August.
- DEM: NASADEM HGT v001 tiles n34e072, n35e072. Buildings: Overture Maps (OSM too sparse in Swat).
