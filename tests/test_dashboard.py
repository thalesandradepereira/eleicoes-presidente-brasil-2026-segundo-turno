"""Regression tests for the published, self-contained TSE 2026 dashboard.

All data tests operate on the exact index.html deployed to Pages.
No network calls, downloads or external packages are necessary.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EXPECTED_NATIONAL = (64_256_232, 59_826_041, 1_430_496, 2_723_305)
EXPECTED_CUTOFF_1715 = (488_813, 62_657_589, 58_545_934, 1_396_695, 2_654_428)
EXPECTED_EXTERIOR = (1_308, 200_154, 171_497, 4_675, 5_117)


def extract_bundle() -> tuple[str, dict, dict, dict, bytes]:
    html = INDEX.read_text(encoding="utf-8")
    assert "ABRIR_DASHBOARD_TSE_2026_TAP_PT_EN.html" in html
    assert "__DATA_B64__" not in html
    match = re.search(
        r'<script id="dataset" type="application/octet-stream">([A-Za-z0-9+/=\s]+)</script>',
        html,
    )
    if not match:
        raise AssertionError("Embedded dataset script not found")
    packed = base64.b64decode("".join(match.group(1).split()), validate=True)
    head = re.search(r"const GEO=(\{.*?\});const INFO=(\{.*?\});const WORLD=(\{.*?\});</script>", html, re.S)
    if not head:
        raise AssertionError("Geographical metadata not found")
    geo, metadata, world = (json.loads(head.group(i)) for i in (1, 2, 3))
    return html, metadata, geo, world, packed


class DashboardReleaseQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html, cls.meta, cls.geo, cls.world, cls.packed = extract_bundle()
        cls.rows = gzip.decompress(cls.packed).decode("ascii").splitlines()

    def test_single_file_and_source(self):
        self.assertGreater(INDEX.stat().st_size, 9_000_000)
        self.assertLess(INDEX.stat().st_size, 15_000_000)
        self.assertNotIn("<script src=", self.html)
        self.assertIn("https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna", self.html)
        self.assertIn("Made by TAP", self.html)
        self.assertEqual(self.html.count('id="langSelect"'), 1)
        self.assertIn('value="en"', self.html)
        self.assertIn('value="pt"', self.html)
        self.assertEqual(self.html.count('id="time"'), 1)
        self.assertEqual(self.html.count('id="worldMap"'), 1)
        self.assertNotIn("The string contains invalid characters", self.html)

    def test_embedded_data_checksum(self):
        self.assertEqual(hashlib.sha256(self.packed).hexdigest(), self.meta["payload_sha256"])

    def test_metadata_and_geometries(self):
        self.assertEqual(len(self.geo), 27)
        self.assertEqual(len(self.meta["ufs"]), 28)
        self.assertEqual(set(self.meta["ufs"][-1:]), {"ZZ"})
        self.assertGreaterEqual(len(self.world), 170)
        self.assertEqual(len(self.meta["country_boletins"]), 99)
        self.assertEqual(sum(self.meta["country_boletins"].values()), 1_308)
        self.assertEqual(len(self.meta["world_markers"]), 3)
        self.assertEqual(len(self.rows), 499_205)

    def test_reconcile_all_votes_and_cutoff(self):
        cities = self.meta["cities"]
        agg = [0] * 4
        exterior = [0] * 5
        cutoff = [0] * 5
        foreign_countries = set()
        for line in self.rows:
            x = [int(v) for v in line.split(",")]
            self.assertEqual(len(x), 11)
            city, zone, section, machine, t, l, f, blank, null, attendance, utc = x
            self.assertGreaterEqual(city, 0)
            self.assertLess(city, len(cities))
            self.assertGreaterEqual(zone, 0)
            self.assertGreaterEqual(section, 0)
            self.assertGreater(machine, 0)
            self.assertTrue(0 <= l <= 65535 and 0 <= f <= 65535)
            for k, v in enumerate((l, f, blank, null)):
                agg[k] += v
            if cities[city][0] == "ZZ":
                self.assertEqual(utc, 99)
                foreign_countries.add(cities[city][3])
                for k, v in enumerate((1, l, f, blank, null)):
                    exterior[k] += v
            elif t <= 900:  # 17:15:00 Brasília, inclusive
                for k, v in enumerate((1, l, f, blank, null)):
                    cutoff[k] += v
        self.assertEqual(tuple(agg), EXPECTED_NATIONAL)
        self.assertEqual(tuple(exterior), EXPECTED_EXTERIOR)
        self.assertEqual(tuple(cutoff), EXPECTED_CUTOFF_1715)
        self.assertEqual(len(foreign_countries), 99)
        self.assertEqual(self.meta["br_totals"], [*EXPECTED_NATIONAL, 499_205])

    def test_no_accidental_debug_files(self):
        # Confirm only expected code artifacts exist (no ZIPs, tokens or original local history).
        for path in ROOT.rglob("*"):
            if path.is_file():
                self.assertNotIn(path.suffix.lower(), {".zip", ".pem", ".p12", ".pfx", ".key"})
                self.assertFalse(path.name.lower().startswith("token"))


if __name__ == "__main__":
    unittest.main()
