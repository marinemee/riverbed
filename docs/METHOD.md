# Method and limits (draft, plain language, max ~250 words in the app)

TODO (issue M3): fill after the pipeline works.

## How it works
1. Radar: water is dark in NISAR L-band images. We combine several dates into a water frequency map and an observed river corridor.
2. Terrain: NASADEM elevation gives each spot's height above the nearest river channel (HAND).
3. Slider: a spot is flooded at "rise h" if its HAND is at most h and it connects to the river.
4. Check: we fit h on one radar pass and test it on another, and report the overlap.

## Limits (keep these in the app)
- Dark areas in radar can be terrain shadow; we filter them with slope and height above river.
- We probably do not have a pass at the exact flood peak.
- The elevation data can be off by several metres in mountains, so results are approximate.
- The model ignores flow speed, debris and rainfall.
- This shows exposure, not predicted floods or timing, and does not replace official warnings.
