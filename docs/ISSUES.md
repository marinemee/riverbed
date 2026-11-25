# Issues

Create all at once with `python scripts/create_issues.py`, or paste each into GitHub. Codes (D3, F7...) are used in dependencies.

## Role 1: Management and writing

### [M1] Repo setup and rules
Labels: role-1-mgmt, must

**Goal:** Make the repo safe to work in.

**Done when:** main is protected, everyone pushed a test branch, README/LICENSE/CONTRIBUTING reviewed, LICENSE names the team.

**Depends on:** none

**Priority:** MUST

### [M2] Source and fact-check log
Labels: role-1-mgmt, must

**Goal:** Every fact shown in the app has a source.

**Done when:** docs/SOURCES.md lists each claim with a link; wording is neutral; no victim photos; two people reviewed it.

**Depends on:** none

**Priority:** MUST

### [M3] Method and limits text
Labels: role-1-mgmt, must

**Goal:** Plain-language method and limits (max 250 words) for the app.

**Done when:** docs/METHOD.md final, numbers filled from validation.json.

**Depends on:** D7

**Priority:** MUST

### [M4] Guided tour copy (5 steps)
Labels: role-1-mgmt, should

**Goal:** Write the tour text: radar sees through cloud, footprint, buildings, what if it rises, limits.

**Done when:** Each step is 30 words or fewer, reviewed.

**Depends on:** none

**Priority:** SHOULD

### [M5] Urdu translation
Labels: role-1-mgmt, should

**Goal:** Translate interface and tour text.

**Done when:** web/i18n/ur.json complete and checked by a native speaker.

**Depends on:** M4, F12

**Priority:** SHOULD

### [M6] Demo video script and recording
Labels: role-1-mgmt, must

**Goal:** A 2-3 minute video that explains the problem and shows the app.

**Done when:** Script approved; video recorded after the must features work; captions added.

**Depends on:** F7, F8

**Priority:** MUST

### [M7] One-page summary and submission checklist
Labels: role-1-mgmt, must

**Goal:** Prepare everything the challenge page asks for.

**Done when:** Summary, repo link, live link and video link all ready; submission checked by two people.

**Depends on:** none

**Priority:** MUST

## Role 2: Data

### [D1] Choose the NISAR scene group
Labels: role-2-data, must

**Goal:** Run pipeline/01 and pick a track/direction/frame with a June (high flow) pass plus Oct/Nov (low flow) passes with HH+HV.

**Done when:** config.yaml and docs/DATA_SOURCES.md updated with the scene names. If no June pass fits, open an issue to use Sentinel-1 for the high-flow pass.

**Depends on:** none

**Priority:** MUST

### [D2] Download and crop scenes
Labels: role-2-data, must

**Goal:** Run pipeline/01 --download then pipeline/02 for the chosen scenes (~7 GB each).

**Done when:** HH dB, HV dB and mask tifs for every chosen date open in QGIS and line up with the river.

**Depends on:** D1

**Priority:** MUST

### [D5] Slope and HAND from NASADEM
Labels: role-2-data, must

**Goal:** Implement pipeline/03: slope, first-pass HAND, then second-pass HAND with channels from the low-flow water mask.

**Done when:** slope.tif and hand.tif exist; spot checks look sensible (riverbank near 0 m, ridges high).

**Depends on:** P1, D3

**Priority:** MUST

### [D3] Water masks per date
Labels: role-2-data, must

**Goal:** Implement pipeline/04: thresholds tuned by eye, shadow removed with slope/HAND, tiny blobs removed.

**Done when:** One clean water mask per date, checked against a basemap, thresholds recorded in config.yaml.

**Depends on:** D2, D5 (first pass)

**Priority:** MUST

### [D4] Footprint products
Labels: role-2-data, must

**Goal:** Implement pipeline/05: water frequency, corridor polygon, high-flow-only zone.

**Done when:** water_frequency.tif and corridor.geojson look right in QGIS.

**Depends on:** D3

**Priority:** MUST

### [D6] Scenario inundation frames
Labels: role-2-data, must

**Goal:** Implement pipeline/07 scenario part: flooded = HAND at most h and connected to the river, for h 0 to 10 in 0.5 steps.

**Done when:** 21 frames produced and the area grows smoothly with h.

**Depends on:** D5

**Priority:** MUST

### [D7] Validation
Labels: role-2-data, must

**Goal:** Fit the rise on one radar pass, test it on a different pass, report overlap (IoU).

**Done when:** validation.json written and an agree/disagree layer produced; misses described honestly.

**Depends on:** D3, D6

**Priority:** MUST

### [D8] Export to web/data
Labels: role-2-data, must

**Goal:** Implement pipeline/08 exactly as in docs/DATA_CONTRACT.md.

**Done when:** All contract files exist, bounds are in meta.json, folder is under 40 MB.

**Depends on:** D4, D6, P3

**Priority:** MUST

### [D9] Safer-ground layer
Labels: role-2-data, should

**Goal:** Raster of spots above the slider level and below a slope limit.

**Done when:** Exported and documented as 'relatively safer', never 'safe'.

**Depends on:** D5

**Priority:** SHOULD

## Role 4: Deployment and integration

### [P1] NASADEM download
Labels: role-4-deploy, must

**Goal:** Get tiles n34e072 and n35e072 from Earthdata Search, mosaic and clip to the area of interest.

**Done when:** data/derived/dem.tif exists; DOI credit added to docs.

**Depends on:** none

**Priority:** MUST

### [P2] OpenStreetMap buildings
Labels: role-4-deploy, must

**Goal:** Pull buildings, hotels and restaurants with osmnx and judge how complete OSM is in Swat.

**Done when:** Count and a short completeness note in docs; fallback chosen (Microsoft footprints) if OSM is thin.

**Depends on:** none

**Priority:** MUST

### [P3] Join buildings to HAND and corridor
Labels: role-4-deploy, must

**Goal:** Implement pipeline/06: hand_min, dist_m, inside_corridor, exposure.

**Done when:** web/data/buildings.geojson has all contract fields; neutral wording.

**Depends on:** D4, D5, P2

**Priority:** MUST

### [P4] Vercel deployment
Labels: role-4-deploy, must

**Goal:** Connect the repo to Vercel with Root Directory = web, preview deploys on pull requests.

**Done when:** Public link opens from a different device.

**Depends on:** none

**Priority:** MUST

### [P5] Integration check
Labels: role-4-deploy, must

**Goal:** Check that every exported file loads in the app and placeholders show when a file is missing.

**Done when:** No console errors; contract mismatches fixed with Role 2 and 3.

**Depends on:** D8, F7

**Priority:** MUST

### [P6] Phone test and performance
Labels: role-4-deploy, must

**Goal:** Test on a real phone; check load time and keyboard/contrast basics.

**Done when:** Loads in under 3 seconds on a normal connection, web/data under 40 MB, slider usable by touch.

**Depends on:** F10

**Priority:** MUST

## Role 3: Frontend

### [F1] Layout shell and real basemap
Labels: role-3-frontend, must

**Goal:** Build the layout from the design and replace the demo basemap with a real free one (do not hammer OpenStreetMap's own tile servers).

**Done when:** Desktop and mobile layouts match the design: https://claude.ai/artifact/5kTFLofJZwSEWCEEyED9UP

**Depends on:** none

**Priority:** MUST

### [F2] Layer switcher and pass selector
Labels: role-3-frontend, must

**Goal:** Toggle water frequency, water mask and radar; pick the radar pass.

**Done when:** All layers line up with the river and have legend entries.

**Depends on:** F1, D8 (or sample data)

**Priority:** MUST

### [F3] High vs low flow swipe
Labels: role-3-frontend, must

**Goal:** Compare the June pass with an Oct/Nov pass.

**Done when:** Works with mouse and touch.

**Depends on:** F2

**Priority:** MUST

### [F4] Corridor outline and legend
Labels: role-3-frontend, must

**Goal:** Draw corridor.geojson with a legend entry.

**Done when:** Visible and readable on every layer.

**Depends on:** F1

**Priority:** MUST

### [F5] Height-above-river layer
Labels: role-3-frontend, must

**Goal:** Show hand.png with a legend in metres.

**Done when:** Legend and colours readable; colours differ in lightness, not just hue.

**Depends on:** F1

**Priority:** MUST

### [F6] Buildings by exposure
Labels: role-3-frontend, must

**Goal:** Colour buildings as inside / near / above, with a legend; add a shape or lightness difference as well as colour.

**Done when:** Counts match buildings.geojson; neutral wording.

**Depends on:** F1, P3

**Priority:** MUST

### [F7] Rise slider and live count
Labels: role-3-frontend, must

**Goal:** Slider swaps inundation frames and updates the building count.

**Done when:** Updates in under half a second.

**Depends on:** F6, D6

**Priority:** MUST

### [F8] Click card
Labels: role-3-frontend, must

**Goal:** Show height above river, distance to river, in footprint?, flooded at the slider level.

**Done when:** Works on any clicked point and on touch.

**Depends on:** F5, F7

**Priority:** MUST

### [F9] Method and limits panel, credits
Labels: role-3-frontend, must

**Goal:** Show docs/METHOD.md text and the exact credit lines from docs/DATA_SOURCES.md.

**Done when:** Reachable in one tap from every screen.

**Depends on:** M3

**Priority:** MUST

### [F10] Mobile bottom sheet
Labels: role-3-frontend, must

**Goal:** Controls in a bottom sheet under the map on narrow screens.

**Done when:** Usable with one thumb on a real phone.

**Depends on:** F7

**Priority:** MUST

### [F11] Opening screen and 5-step tour
Labels: role-3-frontend, should

**Goal:** Opening screen with the question, then a guided tour.

**Done when:** A stranger understands the project in about a minute.

**Depends on:** M4, F7

**Priority:** SHOULD

### [F12] Validation panel
Labels: role-3-frontend, should

**Goal:** Show the overlap score and the agree/disagree map.

**Done when:** Numbers come from validation.json, misses are visible.

**Depends on:** D7

**Priority:** SHOULD

### [F13] English/Urdu toggle with right-to-left
Labels: role-3-frontend, should

**Goal:** Switch all interface text between English and Urdu.

**Done when:** No text is hard-coded; layout flips correctly.

**Depends on:** M5

**Priority:** SHOULD

### [F14] Download corridor GeoJSON
Labels: role-3-frontend, should

**Goal:** Button that downloads corridor.geojson.

**Done when:** File opens in QGIS.

**Depends on:** D4

**Priority:** SHOULD

### [F15] Safer-ground layer toggle
Labels: role-3-frontend, should

**Goal:** Show the safer-ground raster with a clear disclaimer.

**Done when:** Labelled 'relatively safer', not 'safe'.

**Depends on:** D9

**Priority:** SHOULD

### [F16] Shareable link
Labels: role-3-frontend, should

**Goal:** Keep slider value and map position in the URL hash.

**Done when:** A pasted link reopens the same view.

**Depends on:** F7

**Priority:** SHOULD
