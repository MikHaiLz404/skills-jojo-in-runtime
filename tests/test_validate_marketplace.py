import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_marketplace.py"


class MarketplaceValidatorTests(unittest.TestCase):
    def make_repository(
        self,
        plugin: dict,
        *,
        nested_git: bool = False,
        sources: list[dict] | None = None,
    ) -> Path:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        root = Path(tempdir.name)
        source = plugin.get("source", "./emily-valid").removeprefix("./")
        package = root / source
        (package / ".claude-plugin").mkdir(parents=True)
        (package / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": plugin["name"]}), encoding="utf-8"
        )
        if nested_git:
            (package / ".git").mkdir()
        (root / ".claude-plugin").mkdir()
        (root / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps({"name": "fixture", "plugins": [plugin]}), encoding="utf-8"
        )
        if sources is not None:
            (root / "external").mkdir()
            (root / "external" / "sources.json").write_text(
                json.dumps({"sources": sources}), encoding="utf-8"
            )
        return root

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_accepts_first_party_plugin_with_local_manifest(self) -> None:
        result = self.run_validator(
            self.make_repository({"name": "emily-valid", "source": "./emily-valid"})
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("emily-valid", result.stdout)

    def test_rejects_plugin_without_emily_prefix(self) -> None:
        result = self.run_validator(
            self.make_repository({"name": "non-emily", "source": "./non-emily"})
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non-emily", result.stderr)

    def test_rejects_external_source_path(self) -> None:
        result = self.run_validator(
            self.make_repository(
                {"name": "emily-invalid", "source": "./external/checkouts/invalid"}
            )
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("external", result.stderr)

    def test_rejects_missing_source_directory(self) -> None:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(root))
        (root / ".claude-plugin").mkdir()
        (root / ".claude-plugin" / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "fixture",
                    "plugins": [{"name": "emily-missing", "source": "./emily-missing"}],
                }
            ),
            encoding="utf-8",
        )
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("emily-missing", result.stderr)

    def test_rejects_nested_git_source(self) -> None:
        result = self.run_validator(
            self.make_repository(
                {"name": "emily-nested", "source": "./emily-nested"}, nested_git=True
            )
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("nested Git", result.stderr)

    def external_sources(self) -> list[dict]:
        return [
            {
                "name": "caveman",
                "classification": "external",
                "marketplace": False,
                "upstream": "https://github.com/JuliusBrussee/caveman",
                "attribution": "Julius Brussee",
                "license_or_status": "upstream license",
                "update": "git pull --ff-only",
                "local_checkout": "external/checkouts/caveman",
            },
            {
                "name": "understand-anything",
                "classification": "external",
                "marketplace": False,
                "upstream": "https://github.com/Egonex-AI/Understand-Anything",
                "attribution": "Egonex-AI",
                "license_or_status": "MIT",
                "update": "git pull --ff-only",
                "local_checkout": "external/checkouts/understand-anything",
            },
            {
                "name": "character-sheet-pipeline",
                "classification": "external",
                "marketplace": False,
                "upstream": "https://www.top3d.ai/",
                "attribution": "Stefan Vaskevich / Top3D",
                "license_or_status": "attribution retained; redistribution not approved",
                "update": "check upstream source",
                "local_checkout": "external/checkouts/character-sheet-pipeline",
            },
            {
                "name": "character-sheet-pipeline-openai",
                "classification": "external",
                "marketplace": False,
                "upstream": "https://www.top3d.ai/",
                "attribution": "Stefan Vaskevich / Top3D",
                "license_or_status": "attribution retained; redistribution not approved",
                "update": "check upstream source",
                "local_checkout": "external/checkouts/character-sheet-pipeline-openai",
            },
        ]

    def test_accepts_external_registry_checkout(self) -> None:
        result = self.run_validator(
            self.make_repository(
                {"name": "emily-valid", "source": "./emily-valid"},
                sources=self.external_sources(),
            )
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_registry_source_without_classification(self) -> None:
        sources = self.external_sources()
        del sources[0]["classification"]
        result = self.run_validator(
            self.make_repository(
                {"name": "emily-valid", "source": "./emily-valid"}, sources=sources
            )
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("caveman", result.stderr)
        self.assertIn("classification", result.stderr)

    def test_rejects_registry_source_without_upstream(self) -> None:
        sources = self.external_sources()
        del sources[0]["upstream"]
        result = self.run_validator(
            self.make_repository(
                {"name": "emily-valid", "source": "./emily-valid"}, sources=sources
            )
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("caveman", result.stderr)
        self.assertIn("upstream", result.stderr)

    def test_rejects_external_registry_source_marked_for_marketplace(self) -> None:
        sources = self.external_sources()
        sources[0]["marketplace"] = True
        result = self.run_validator(
            self.make_repository(
                {"name": "emily-valid", "source": "./emily-valid"}, sources=sources
            )
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("caveman", result.stderr)
        self.assertIn("marketplace", result.stderr)


if __name__ == "__main__":
    unittest.main()
