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
        self.coverage = self.root / "coverage.json"
        self.template.write_text(
            "<html><head><style>body{color:#111}</style></head></html>",
            encoding="utf-8",
        )
        self.manifest.write_text(
            json.dumps([{"file": "figure1.png"}, {"file": "table1.png"}]),
            encoding="utf-8",
        )
        self.coverage.write_text(
            json.dumps(
                {
                    "sections": [
                        {
                            "id": "1",
                            "min_detail_chars": 4,
                            "min_detail_paragraphs": 1,
                        }
                    ],
                    "visuals": [
                        {
                            "id": "figure1",
                            "mode": "image",
                            "crop_reviewed": True,
                            "content_verified": True,
                        },
                        {
                            "id": "table1",
                            "mode": "html",
                            "content_verified": True,
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_output(self, image_src: str = "data:image/png;base64,AA==") -> None:
        self.output.write_text(
            f"""<!doctype html>
<html lang="ko"><head><style>body{{color:#111}}</style></head><body>
<section class="ch"><div class="tldr">요약</div>
<div data-source-section="1"><p>상세 설명</p></div>
<img data-figure="figure1" src="{image_src}" alt="그림">
<table data-figure="table1"><tr><td>표</td></tr></table>
</section></body></html>""",
            encoding="utf-8",
        )

    def test_accepts_complete_offline_explainer(self) -> None:
        self.write_output()
        self.assertEqual(
            [],
            VALIDATOR.validate(
                self.output, self.manifest, self.template, self.coverage
            ),
        )

    def test_rejects_remote_image(self) -> None:
        self.write_output("https://example.com/figure.png")
        errors = VALIDATOR.validate(
            self.output, self.manifest, self.template, self.coverage
        )
        self.assertTrue(any("not an embedded data URI" in error for error in errors))

    def test_rejects_summary_only_source_section(self) -> None:
        self.coverage.write_text(
            json.dumps(
                {
                    "sections": [
                        {
                            "id": "1",
                            "min_detail_chars": 100,
                            "min_detail_paragraphs": 2,
                        }
                    ],
                    "visuals": [],
                }
            ),
            encoding="utf-8",
        )
        self.write_output()
        errors = VALIDATOR.validate(
            self.output, self.manifest, self.template, self.coverage
        )
        self.assertTrue(any("detail characters" in error for error in errors))
        self.assertTrue(any("detail paragraphs" in error for error in errors))

    def test_rejects_unreviewed_image_crop(self) -> None:
        coverage = json.loads(self.coverage.read_text(encoding="utf-8"))
        coverage["visuals"][0]["crop_reviewed"] = False
        self.coverage.write_text(json.dumps(coverage), encoding="utf-8")
        self.write_output()
        errors = VALIDATOR.validate(
            self.output, self.manifest, self.template, self.coverage
        )
        self.assertTrue(any("crop_reviewed" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
