from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "discover_checks.py"
SPEC = importlib.util.spec_from_file_location("discover_checks", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DiscoverChecksTest(unittest.TestCase):
    def test_discovers_declared_node_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "scripts": {
                            "test": "vitest run",
                            "lint": "eslint .",
                            "start": "vite",
                        }
                    }
                ),
                encoding="utf-8",
            )

            checks = MODULE.discover(root)

        commands = {item["command"] for item in checks}
        self.assertEqual(commands, {"npm run test", "npm run lint"})

    def test_ignores_node_modules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            dependency = root / "node_modules" / "example"
            dependency.mkdir(parents=True)
            (dependency / "package.json").write_text(
                json.dumps({"scripts": {"test": "should-not-run"}}),
                encoding="utf-8",
            )

            self.assertEqual(MODULE.discover(root), [])


if __name__ == "__main__":
    unittest.main()
