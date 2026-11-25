"""Step 3 (D5, with P1): slope and HAND (height above nearest drainage) from NASADEM.
TODO
 1. Read data/derived/dem.tif (made in issue P1). Reproject to the radar grid (same CRS and pixel size as a cropped GCOV tif).
 2. Slope in degrees -> data/derived/slope.tif
 3. First pass HAND: fill pits, flow direction (pysheds or whitebox), channels from flow accumulation -> hand_v1.tif
 4. Second pass (after step 04): seed channels from the LOW-FLOW radar water mask -> hand.tif
 DEM heights are relative to the EGM96 geoid: fine for height ABOVE river. Vertical error can be several metres in mountains.
"""
raise NotImplementedError("See docstring and issue D5")
