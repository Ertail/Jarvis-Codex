from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_explainer.py"
SPEC = importlib.util.spec_from_file_location("validate_explainer", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ValidateExplainerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.template = self.root / "template.html"
        self.manifest = self.root / "manifest.json"
        self.output = self.root / "output.html"
        self.template.write_text(
            "<html><head><style>body{color:#111}</style></head></html>",
            encoding="utf-8",
        )
        self.manifest.write_text(
            json.dumps([{"file": "figure1.png"}, {"file": "table1.png"}]),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_output(self, image_src: str = "data:image/png;base64,AA==") -> None:
        self.output.write_text(
            f"""<!doctype html>
<html lang="ko"><head><style>body{{color:#111}}</style></head><body>
<section class="ch"><div class="tldr">요약</div><p>상세 설명</p>
<img data-figure="figure1" src="{image_src}" alt="그림">
<table data-figure="table1"><tr><td>표</td></tr></table>
</section></body></html>""",
            encoding="utf-8",
        )

    def test_accepts_complete_offline_explainer(self) -> None:
        self.write_output()
        self.assertEqual(
            [],
            VALIDATOR.validate(self.output, self.manifest, self.template),
        )

    def test_rejects_remote_image(self) -> None:
        self.write_output("https://example.com/figure.png")
        errors = VALIDATOR.validate(self.output, self.manifest, self.template)
        self.assertTrue(any("not an embedded data URI" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
