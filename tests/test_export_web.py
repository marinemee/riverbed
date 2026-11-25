"""Exercise fail-fast export against the checkout, without fabricated inputs."""

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "pipeline" / "08_export_web.py"
spec = importlib.util.spec_from_file_location("export_web", SCRIPT)
export_web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_web)


def snapshot():
    return {str(path.relative_to(ROOT / "web")): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (ROOT / "web").rglob("*") if path.is_file()}


class ExportTests(unittest.TestCase):
    def test_actual_scene_catalog_is_used_without_inventing_metadata(self):
        path = ROOT / "data" / "derived" / "scenes_found.json"
        if not path.is_file():
            self.skipTest("The real scene catalog has not been copied into this checkout")
        catalog = export_web.read_json(path)
        config = {"nisar": {key: catalog[key] for key in ("track", "direction", "frame")}}
        # Exercise lower-case catalog direction against the config's upper case.
        config["nisar"]["direction"] = config["nisar"]["direction"].upper()
        exported = export_web.passes(export_web.REQUIRED_DATES, config)
        originals = {record["date"]: record for record in catalog["scenes"]}
        self.assertEqual([record["id"] for record in exported], list(export_web.REQUIRED_DATES))
        for record in exported:
            original = originals[record["id"]]
            flow, maturity = original["role"].split(",")
            self.assertEqual(record["scene"], original["scene"])
            self.assertEqual(record["flow"] + " flow", flow.strip())
            self.assertEqual(record["maturity"], maturity.strip().upper())

    def test_catalog_errors_report_missing_or_conflicting_metadata(self):
        path = ROOT / "data" / "derived" / "scenes_found.json"
        if not path.is_file():
            self.skipTest("The real scene catalog has not been copied into this checkout")
        catalog = export_web.read_json(path)
        config = {"nisar": {key: catalog[key] for key in ("track", "direction", "frame")}}
        # Remove or alter real records in memory only; never write test data or
        # substitute a fabricated scene ID for a missing observation.
        cases = []
        missing_track = json.loads(json.dumps(catalog))
        del missing_track["track"]
        cases.append((missing_track, "missing metadata: track"))
        wrong_orbit = json.loads(json.dumps(catalog))
        wrong_orbit["direction"] = "descending"
        cases.append((wrong_orbit, "does not match configured T084_A_F019"))
        duplicate = json.loads(json.dumps(catalog))
        duplicate["scenes"].append(duplicate["scenes"][0].copy())
        cases.append((duplicate, "found 2"))
        wrong_date = json.loads(json.dumps(catalog))
        wrong_date["scenes"][0]["date"], wrong_date["scenes"][1]["date"] = (
            wrong_date["scenes"][1]["date"], wrong_date["scenes"][0]["date"])
        cases.append((wrong_date, "does not match T084_A_F019 on"))
        for field, message in (("scene", "missing or invalid scene ID"),
                               ("role", "missing high/low flow metadata")):
            incomplete = json.loads(json.dumps(catalog))
            del incomplete["scenes"][0][field]
            cases.append((incomplete, message))
        for incomplete, message in cases:
            with self.subTest(message=message), patch.object(export_web, "read_json", return_value=incomplete):
                with self.assertRaises(export_web.ExportError) as raised:
                    export_web.passes(export_web.REQUIRED_DATES, config)
                self.assertIn(str(path), str(raised.exception))
                self.assertIn(message, str(raised.exception))

    def test_missing_inputs_stop_without_changing_web_files(self):
        # No TIFF/JSON test fixtures: use only the real files in this checkout.
        if (ROOT / "data" / "derived" / "water_frequency.tif").is_file():
            self.skipTest("This checkout has processed data; do not run a publishing test")
        before = snapshot()
        # Also verifies that paths are relative to the repository, not the CWD.
        with TemporaryDirectory() as unrelated_directory:
            result = subprocess.run([sys.executable, str(SCRIPT)],
                                    cwd=unrelated_directory, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Missing required input(s)", result.stderr)
        for name in ("water_frequency.tif", "hand.tif", "20260726_water.tif",
                     "20260819_water.tif", "20260819_hh_dB.tif",
                     "20261030_hh_dB.tif", "flood_h000.tif", "flood_h100.tif",
                     "validation.json", "scenes_found.json", "corridor.geojson"):
            path = ROOT / "data" / "derived" / name
            if not path.is_file():
                self.assertIn(str(path), result.stderr)
        self.assertIn("No files were exported", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(before, snapshot())

    def test_metadata_field_names_match_contract(self):
        # Check actual exporter field names against the documented JSON example,
        # without inventing scene metadata or needing unavailable raster inputs.
        contract = (ROOT / "docs" / "DATA_CONTRACT.md").read_text(encoding="utf-8")
        example = json.loads(re.search(r"```json\s*(.*?)\s*```", contract, re.S).group(1))
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        metadata = next(node.value for node in ast.walk(tree)
                        if isinstance(node, ast.Assign) and any(
                            isinstance(target, ast.Name) and target.id == "meta"
                            for target in node.targets))
        self.assertLessEqual(set(example), {key.value for key in metadata.keys})
        pass_fields = next(node.args[0] for node in ast.walk(tree)
                           if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                           and node.func.attr == "append" and node.args
                           and isinstance(node.args[0], ast.Dict))
        self.assertEqual(set(example["passes"][0]), {key.value for key in pass_fields.keys})

    def test_invalid_resolution_is_rejected_without_changing_web_files(self):
        before = snapshot()
        result = subprocess.run([sys.executable, str(SCRIPT), "--max-size", "0"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--max-size must be positive", result.stderr)
        self.assertEqual(before, snapshot())

    def test_unknown_measurements_remain_null(self):
        self.assertIsNone(export_web.number(None, "hand_min", "input", nullable=True))
        for value in (float("nan"), float("inf"), -1, True):
            with self.subTest(value=value), self.assertRaises(export_web.ExportError):
                export_web.number(value, "measurement", "input")

    def test_real_buildings_keep_all_measurements_and_gain_contract_fields(self):
        path = ROOT / "web" / "data" / "buildings.geojson"
        source = json.loads(path.read_text(encoding="utf-8"))
        features = json.loads(json.dumps(source["features"]))
        export_web.normalize_buildings(features, path)
        identifiers = [feature["properties"]["id"] for feature in features]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for original, normalized in zip(source["features"], features):
            self.assertEqual(original["geometry"], normalized["geometry"])
            for key, value in original["properties"].items():
                self.assertEqual(value, normalized["properties"][key])
            self.assertIn(normalized["properties"]["type"], ("hotel", "restaurant", "building"))
        # Re-exporting an already normalized file must keep its identifiers.
        export_web.normalize_buildings(features, path)
        self.assertEqual(identifiers, [feature["properties"]["id"] for feature in features])


if __name__ == "__main__":
    unittest.main()
