from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
WEB_DATA = ROOT / "web" / "data"


def load(path=None):
    with open(path or ROOT / "config.yaml") as f:
        return yaml.safe_load(f)


def bbox_wkt(bbox):
    w, s, e, n = bbox
    return f"POLYGON(({w} {s},{e} {s},{e} {n},{w} {n},{w} {s}))"
