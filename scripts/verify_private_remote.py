#!/usr/bin/env python3
"""Verify the private marketplace remote before an explicit push."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Sequence


CommandRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def run_checked(
    command: list[str], runner: CommandRunner, errors: list[str]
) -> str:
    result = runner(command)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "command failed"
        errors.append(f"{' '.join(command)}: {detail}")
        return ""
    return result.stdout.strip()


def verify_and_optionally_push(
    owner: str, repository: str, runner: CommandRunner, *, push: bool
) -> list[str]:
    """Return verification errors and run `git push` only when every check passes."""

    errors: list[str] = []
    metadata_text = run_checked(
        [
            "gh",
            "repo",
            "view",
            f"{owner}/{repository}",
            "--json",
            "name,owner,visibility,url,defaultBranchRef",
        ],
        runner,
        errors,
    )
    try:
        metadata = json.loads(metadata_text) if metadata_text else {}
    except json.JSONDecodeError as error:
        errors.append(f"GitHub metadata is not valid JSON: {error.msg}")
        metadata = {}

    if metadata.get("name") != repository:
        errors.append(f"repository name must be {repository}")
    if metadata.get("owner", {}).get("login") != owner:
        errors.append(f"repository owner must be {owner}")
    if metadata.get("visibility") != "PRIVATE":
        errors.append("repository visibility must be PRIVATE")
    default_branch = metadata.get("defaultBranchRef", {}).get("name")
    if not isinstance(default_branch, str) or not default_branch:
        errors.append("repository must declare a default branch")
        default_branch = ""

    remote = run_checked(["git", "remote", "get-url", "origin"], runner, errors)
    expected_remotes = {
        f"https://github.com/{owner}/{repository}",
        f"https://github.com/{owner}/{repository}.git",
        f"git@github.com:{owner}/{repository}.git",
    }
    if remote.rstrip("/") not in expected_remotes:
        errors.append(f"origin must target {owner}/{repository}")

    branch = run_checked(["git", "branch", "--show-current"], runner, errors)
    if branch != default_branch:
        errors.append(f"current branch must be {default_branch}")
    if run_checked(["git", "status", "--porcelain"], runner, errors):
        errors.append("worktree must be clean before pushing")
    if run_checked(["git", "ls-files", "external/checkouts"], runner, errors):
        errors.append("external checkouts must not be tracked")

    if errors or not push:
        return errors

    run_checked(["git", "push", "origin", default_branch], runner, errors)
    return errors


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Verify a private GitHub marketplace remote before an explicit push."
    )
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repository", default="skills-jojo-in-runtime")
    parser.add_argument(
        "--push", action="store_true", help="Push main only after all verification checks pass."
    )
    args = parser.parse_args(argv[1:])
    errors = verify_and_optionally_push(args.owner, args.repository, run_command, push=args.push)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"verified private remote {args.owner}/{args.repository}")
    if args.push:
        print("pushed origin/main")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
