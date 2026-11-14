# How we work
- One issue = one branch = one pull request. Branch name: `<code>-short-name`, e.g. `D3-water-masks`.
- At least one teammate reviews each PR. Nobody pushes straight to `main`.
- Never commit data files (.h5, .tif, large rasters). Only small exports go in `web/data/`.
- Every number in the app comes from a file. No hand-typed results.
- Wording: say "inside the observed river footprint", never "illegal". Use official sources and no victim photos.
- **Done means tested on a phone**, not just on a laptop.
- Feature freeze when every `must` issue is done. New ideas go to a "later" list.
- Cut line: if the `must` issues are not done by the halfway point of the build time, drop all `should` issues.
