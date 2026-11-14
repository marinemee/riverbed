"""All project issues. Edit here, then run create_issues.py or issues_to_md.py."""
ROLES = {"M": "role-1-mgmt", "D": "role-2-data", "F": "role-3-frontend", "P": "role-4-deploy"}
LABELS = {"role-1-mgmt": "5319E7", "role-2-data": "0E8A16", "role-3-frontend": "1D76DB",
          "role-4-deploy": "D93F0B", "must": "B60205", "should": "FBCA04"}
ISSUES = []


def I(code, prio, title, goal, done, deps="none"):
    ISSUES.append({"code": code, "title": f"[{code}] {title}",
                   "labels": [ROLES[code[0]], prio],
                   "body": f"**Goal:** {goal}\n\n**Done when:** {done}\n\n**Depends on:** {deps}\n\n**Priority:** {prio.upper()}"})


# Role 1: management and writing
I("M1", "must", "Repo setup and rules", "Make the repo safe to work in.", "main is protected, everyone pushed a test branch, README/LICENSE/CONTRIBUTING reviewed, LICENSE names the team.")
I("M2", "must", "Source and fact-check log", "Every fact shown in the app has a source.", "docs/SOURCES.md lists each claim with a link; wording is neutral; no victim photos; two people reviewed it.")
I("M3", "must", "Method and limits text", "Plain-language method and limits (max 250 words) for the app.", "docs/METHOD.md final, numbers filled from validation.json.", "D7")
I("M4", "should", "Guided tour copy (5 steps)", "Write the tour text: radar sees through cloud, footprint, buildings, what if it rises, limits.", "Each step is 30 words or fewer, reviewed.")
I("M5", "should", "Urdu translation", "Translate interface and tour text.", "web/i18n/ur.json complete and checked by a native speaker.", "M4, F12")
I("M6", "must", "Demo video script and recording", "A 2-3 minute video that explains the problem and shows the app.", "Script approved; video recorded after the must features work; captions added.", "F7, F8")
I("M7", "must", "One-page summary and submission checklist", "Prepare everything the challenge page asks for.", "Summary, repo link, live link and video link all ready; submission checked by two people.")

# Role 2: data
I("D1", "must", "Choose the NISAR scene group", "Run pipeline/01 and pick a track/direction/frame with a June (high flow) pass plus Oct/Nov (low flow) passes with HH+HV.", "config.yaml and docs/DATA_SOURCES.md updated with the scene names. If no June pass fits, open an issue to use Sentinel-1 for the high-flow pass.")
I("D2", "must", "Download and crop scenes", "Run pipeline/01 --download then pipeline/02 for the chosen scenes (~7 GB each).", "HH dB, HV dB and mask tifs for every chosen date open in QGIS and line up with the river.", "D1")
I("D5", "must", "Slope and HAND from NASADEM", "Implement pipeline/03: slope, first-pass HAND, then second-pass HAND with channels from the low-flow water mask.", "slope.tif and hand.tif exist; spot checks look sensible (riverbank near 0 m, ridges high).", "P1, D3")
I("D3", "must", "Water masks per date", "Implement pipeline/04: thresholds tuned by eye, shadow removed with slope/HAND, tiny blobs removed.", "One clean water mask per date, checked against a basemap, thresholds recorded in config.yaml.", "D2, D5 (first pass)")
I("D4", "must", "Footprint products", "Implement pipeline/05: water frequency, corridor polygon, high-flow-only zone.", "water_frequency.tif and corridor.geojson look right in QGIS.", "D3")
I("D6", "must", "Scenario inundation frames", "Implement pipeline/07 scenario part: flooded = HAND at most h and connected to the river, for h 0 to 10 in 0.5 steps.", "21 frames produced and the area grows smoothly with h.", "D5")
I("D7", "must", "Validation", "Fit the rise on one radar pass, test it on a different pass, report overlap (IoU).", "validation.json written and an agree/disagree layer produced; misses described honestly.", "D3, D6")
I("D8", "must", "Export to web/data", "Implement pipeline/08 exactly as in docs/DATA_CONTRACT.md.", "All contract files exist, bounds are in meta.json, folder is under 40 MB.", "D4, D6, P3")
I("D9", "should", "Safer-ground layer", "Raster of spots above the slider level and below a slope limit.", "Exported and documented as 'relatively safer', never 'safe'.", "D5")

# Role 4: deploy and integration (data prep first)
I("P1", "must", "NASADEM download", "Get tiles n34e072 and n35e072 from Earthdata Search, mosaic and clip to the area of interest.", "data/derived/dem.tif exists; DOI credit added to docs.")
I("P2", "must", "OpenStreetMap buildings", "Pull buildings, hotels and restaurants with osmnx and judge how complete OSM is in Swat.", "Count and a short completeness note in docs; fallback chosen (Microsoft footprints) if OSM is thin.")
I("P3", "must", "Join buildings to HAND and corridor", "Implement pipeline/06: hand_min, dist_m, inside_corridor, exposure.", "web/data/buildings.geojson has all contract fields; neutral wording.", "D4, D5, P2")
I("P4", "must", "Vercel deployment", "Connect the repo to Vercel with Root Directory = web, preview deploys on pull requests.", "Public link opens from a different device.")
I("P5", "must", "Integration check", "Check that every exported file loads in the app and placeholders show when a file is missing.", "No console errors; contract mismatches fixed with Role 2 and 3.", "D8, F7")
I("P6", "must", "Phone test and performance", "Test on a real phone; check load time and keyboard/contrast basics.", "Loads in under 3 seconds on a normal connection, web/data under 40 MB, slider usable by touch.", "F10")

# Role 3: frontend
I("F1", "must", "Layout shell and real basemap", "Build the layout from the design and replace the demo basemap with a real free one (do not hammer OpenStreetMap's own tile servers).", "Desktop and mobile layouts match the design: https://claude.ai/artifact/5kTFLofJZwSEWCEEyED9UP")
I("F2", "must", "Layer switcher and pass selector", "Toggle water frequency, water mask and radar; pick the radar pass.", "All layers line up with the river and have legend entries.", "F1, D8 (or sample data)")
I("F3", "must", "High vs low flow swipe", "Compare the June pass with an Oct/Nov pass.", "Works with mouse and touch.", "F2")
I("F4", "must", "Corridor outline and legend", "Draw corridor.geojson with a legend entry.", "Visible and readable on every layer.", "F1")
I("F5", "must", "Height-above-river layer", "Show hand.png with a legend in metres.", "Legend and colours readable; colours differ in lightness, not just hue.", "F1")
I("F6", "must", "Buildings by exposure", "Colour buildings as inside / near / above, with a legend; add a shape or lightness difference as well as colour.", "Counts match buildings.geojson; neutral wording.", "F1, P3")
I("F7", "must", "Rise slider and live count", "Slider swaps inundation frames and updates the building count.", "Updates in under half a second.", "F6, D6")
I("F8", "must", "Click card", "Show height above river, distance to river, in footprint?, flooded at the slider level.", "Works on any clicked point and on touch.", "F5, F7")
I("F9", "must", "Method and limits panel, credits", "Show docs/METHOD.md text and the exact credit lines from docs/DATA_SOURCES.md.", "Reachable in one tap from every screen.", "M3")
I("F10", "must", "Mobile bottom sheet", "Controls in a bottom sheet under the map on narrow screens.", "Usable with one thumb on a real phone.", "F7")
I("F11", "should", "Opening screen and 5-step tour", "Opening screen with the question, then a guided tour.", "A stranger understands the project in about a minute.", "M4, F7")
I("F12", "should", "Validation panel", "Show the overlap score and the agree/disagree map.", "Numbers come from validation.json, misses are visible.", "D7")
I("F13", "should", "English/Urdu toggle with right-to-left", "Switch all interface text between English and Urdu.", "No text is hard-coded; layout flips correctly.", "M5")
I("F14", "should", "Download corridor GeoJSON", "Button that downloads corridor.geojson.", "File opens in QGIS.", "D4")
I("F15", "should", "Safer-ground layer toggle", "Show the safer-ground raster with a clear disclaimer.", "Labelled 'relatively safer', not 'safe'.", "D9")
I("F16", "should", "Shareable link", "Keep slider value and map position in the URL hash.", "A pasted link reopens the same view.", "F7")
