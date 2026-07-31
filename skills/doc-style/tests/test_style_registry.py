from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "style_registry.py"
SPEC = importlib.util.spec_from_file_location("style_registry", SCRIPT)
assert SPEC and SPEC.loader
STYLE_REGISTRY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STYLE_REGISTRY)


CSS = """:root{--paper:#fff;--ink:#111;--ar:#087;--arb:#a50;}
section.ch{}.tldr{}.tbl-wrap{}figure img{max-width:100%;height:auto}"""


class StyleRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        STYLE_REGISTRY.SKILL_DIR = root
        STYLE_REGISTRY.BUILTIN_REGISTRY_DIR = root / "assets" / "design-systems"
        STYLE_REGISTRY.DEFAULT_ACTIVE_FILE = root / "active.txt"
        STYLE_REGISTRY.USER_ROOT = root / "user"
        STYLE_REGISTRY.USER_REGISTRY_DIR = (
            STYLE_REGISTRY.USER_ROOT / "design-systems"
        )
        STYLE_REGISTRY.USER_ACTIVE_FILE = STYLE_REGISTRY.USER_ROOT / "active.txt"
        style = STYLE_REGISTRY.BUILTIN_REGISTRY_DIR / "paper-ink"
        style.mkdir(parents=True)
        (style / "design-system.css").write_text(CSS, encoding="utf-8")
        (style / "components.md").write_text("# Components\n", encoding="utf-8")
        for filename in ("template.html", "preview.html"):
            (style / filename).write_text(
                f"<html><head><style>{CSS}</style></head></html>",
                encoding="utf-8",
            )
        STYLE_REGISTRY.DEFAULT_ACTIVE_FILE.write_text(
            "paper-ink\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_validate_and_clone(self) -> None:
        self.assertEqual([], STYLE_REGISTRY.validate_style("paper-ink"))
        self.assertEqual(0, STYLE_REGISTRY.command_clone("night-ink", None))
        self.assertEqual([], STYLE_REGISTRY.validate_style("night-ink"))
        self.assertEqual(0, STYLE_REGISTRY.command_activate("night-ink"))
        self.assertEqual("night-ink", STYLE_REGISTRY.read_active())

    def test_rejects_divergent_embedded_css(self) -> None:
        template = (
            STYLE_REGISTRY.BUILTIN_REGISTRY_DIR
            / "paper-ink"
            / "template.html"
        )
        template.write_text("<style>body{color:red}</style>", encoding="utf-8")
        errors = STYLE_REGISTRY.validate_style("paper-ink")
        self.assertTrue(any("<style> differs" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
