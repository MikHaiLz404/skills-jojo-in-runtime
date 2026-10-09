import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_marketplace.py"


class MarketplaceValidatorTests(unittest.TestCase):
    EXPECTED_DOMAIN_SKILLS = {
        "emily-strategy-planning": {
            "emily-advisor-strategy",
            "grill-me",
            "grill-with-docs",
            "grilling",
            "wayfinder",
        },
        "emily-visual-communication": {
            "emily-brand-unified-guidelines",
            "emily-infographic-gen",
            "data-storytelling",
            "presentation-generation",
            "visualization-expert",
        },
        "emily-team-communications": {"emily-google-chat-webhook"},
        "emily-production-operations": {
            "jira-kitsu-ticket-sync",
            "jira-kitsu-weekly-brief",
            "jira-kitsu-apply-brief",
        },
        "emily-game-workflows": {
            "emily-unreal-explorer",
            "matcha-cat-memory-game",
        },
    }

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

    def test_rejects_nested_blocked_source_path(self) -> None:
        result = self.run_validator(
            self.make_repository(
                {"name": "emily-wrapper", "source": "./emily-wrapper/caveman"}
            )
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must equal", result.stderr)
        self.assertIn("caveman", result.stderr)

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

    def test_rejects_package_manifest_name_mismatch(self) -> None:
        root = self.make_repository(
            {"name": "emily-valid", "source": "./emily-valid"}
        )
        (root / "emily-valid" / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "emily-different"}), encoding="utf-8"
        )
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("manifest name", result.stderr)

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

    def first_party_3d_source(self) -> dict:
        return {
            "name": "3d-scene-gen",
            "classification": "first-party",
            "marketplace": True,
            "upstream": "local first-party source",
            "attribution": "jojo-in-runtime",
            "license_or_status": "approved for Emily marketplace",
            "update": "maintain through this marketplace repository after import",
            "local_checkout": "external/checkouts/3d-scene-gen",
            "target_plugin": "emily-3d-character-production",
        }

    def add_skill(self, root: Path, package_name: str, skill_name: str) -> None:
        package = root / package_name
        (package / ".claude-plugin").mkdir(parents=True, exist_ok=True)
        (package / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": package_name}), encoding="utf-8"
        )
        skill = package / "skills" / skill_name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {skill_name}\ndescription: fixture\n---\n", encoding="utf-8"
        )

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

    def test_rejects_first_party_source_missing_from_target_package(self) -> None:
        sources = self.external_sources() + [self.first_party_3d_source()]
        result = self.run_validator(
            self.make_repository(
                {"name": "emily-valid", "source": "./emily-valid"}, sources=sources
            )
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("3d-scene-gen", result.stderr)

    def test_accepts_first_party_source_in_declared_target_package(self) -> None:
        sources = self.external_sources() + [self.first_party_3d_source()]
        root = self.make_repository(
            {"name": "emily-valid", "source": "./emily-valid"}, sources=sources
        )
        self.add_skill(root, "emily-3d-character-production", "3d-scene-gen")
        result = self.run_validator(root)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_unverified_source_imported_into_an_emily_package(self) -> None:
        sources = self.external_sources()
        sources.append(
            {
                "name": "low-poly-diorama",
                "classification": "unverified",
                "marketplace": False,
                "upstream": "not established",
                "attribution": "not established",
                "license_or_status": "hold outside marketplace",
                "update": "record source before import",
                "local_checkout": "external/checkouts/low-poly-diorama",
            }
        )
        root = self.make_repository(
            {"name": "emily-valid", "source": "./emily-valid"},
            sources=sources,
        )
        self.add_skill(root, "emily-invalid", "low-poly-diorama")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("low-poly-diorama", result.stderr)

    def test_rejects_unregistered_skill_in_an_emily_package(self) -> None:
        root = self.make_repository(
            {"name": "emily-valid", "source": "./emily-valid"},
            sources=self.external_sources(),
        )
        self.add_skill(root, "emily-valid", "renamed-stefan-skill")
        result = self.run_validator(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("renamed-stefan-skill", result.stderr)

    def test_repository_has_expected_domain_skill_inventory(self) -> None:
        for package_name, expected_skills in self.EXPECTED_DOMAIN_SKILLS.items():
            package = REPO_ROOT / package_name
            self.assertTrue(
                (package / ".claude-plugin" / "plugin.json").is_file(), package_name
            )
            actual_skills = {
                child.name
                for child in (package / "skills").iterdir()
                if (child / "SKILL.md").is_file()
            }
            self.assertEqual(actual_skills, expected_skills, package_name)

    def test_catalog_matches_nonempty_first_party_packages(self) -> None:
        manifest = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["version"], "2.0.0")
        expected_packages = {
            package.name
            for package in REPO_ROOT.glob("emily-*")
            if (package / ".claude-plugin" / "plugin.json").is_file()
            and any((skill / "SKILL.md").is_file() for skill in (package / "skills").iterdir())
        }
        catalog_names = {plugin["name"] for plugin in manifest["plugins"]}
        self.assertEqual(catalog_names, expected_packages)
        for plugin in manifest["plugins"]:
            self.assertTrue(plugin["name"].startswith("emily-"))
            self.assertEqual(plugin["source"], f"./{plugin['name']}")
            self.assertIsInstance(plugin["category"], str)
        self.assertFalse(
            {
                "caveman",
                "understand-anything",
                "character-sheet-pipeline",
                "emily-core-skills",
                "emily-planning",
                "emily-presentation-system",
                "emily-google-chat-webhook",
                "jira-kitsu-ticket-management",
            }
            & catalog_names
        )


if __name__ == "__main__":
    unittest.main()
