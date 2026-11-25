"""Step 7 (D6, D7): scenario frames and validation.
TODO
 Scenario: for h in 0..10 step 0.5: flooded = (HAND <= h) AND connected to the river channel -> inundation/h_<h>.png
 Validation: choose the rise h* that best matches one radar high-flow pass (maximise IoU = overlap / union).
   Then TEST h* against a DIFFERENT pass. Report IoU for both. Save validation.json and an agree/disagree layer
   (model only / radar only / both). Report misses honestly.
 The slider means "metres above the low-flow river level", not a flood stage or discharge.
"""
raise NotImplementedError("See docstring and issues D6, D7")
