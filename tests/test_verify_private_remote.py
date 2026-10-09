import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "verify_private_remote.py"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_private_remote", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load verify_private_remote")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PrivateRemoteVerificationTests(unittest.TestCase):
    OWNER = "MikHaiLz404"
    REPOSITORY = "skills-jojo-in-runtime"

    def runner(self, *, visibility: str = "PRIVATE"):
        calls: list[tuple[str, ...]] = []
        metadata = json.dumps(
            {
                "name": self.REPOSITORY,
                "owner": {"login": self.OWNER},
                "visibility": visibility,
                "url": f"https://github.com/{self.OWNER}/{self.REPOSITORY}",
            }
        )

        def run(command: list[str]) -> subprocess.CompletedProcess[str]:
            calls.append(tuple(command))
            outputs = {
                ("gh", "repo", "view", f"{self.OWNER}/{self.REPOSITORY}", "--json", "name,owner,visibility,url"): metadata,
                ("git", "remote", "get-url", "origin"): f"https://github.com/{self.OWNER}/{self.REPOSITORY}.git\n",
                ("git", "branch", "--show-current"): "main\n",
                ("git", "status", "--porcelain"): "",
                ("git", "ls-files", "external/checkouts"): "",
                ("git", "push", "origin", "main"): "",
            }
            output = outputs.get(tuple(command), "")
            return subprocess.CompletedProcess(command, 0, output, "")

        return run, calls

    def test_rejects_non_private_remote_before_push(self) -> None:
        module = load_module()
        run, calls = self.runner(visibility="PUBLIC")
        errors = module.verify_and_optionally_push(self.OWNER, self.REPOSITORY, run, push=True)
        self.assertIn("repository visibility must be PRIVATE", errors)
        self.assertNotIn(("git", "push", "origin", "main"), calls)

    def test_pushes_only_after_owner_name_visibility_and_git_checks_pass(self) -> None:
        module = load_module()
        run, calls = self.runner()
        errors = module.verify_and_optionally_push(self.OWNER, self.REPOSITORY, run, push=True)
        self.assertEqual(errors, [])
        self.assertEqual(calls[-1], ("git", "push", "origin", "main"))


if __name__ == "__main__":
    unittest.main()
