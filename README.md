# Emily Skills Marketplace

Private marketplace for first-party Emily workflows. The default branch is
`develop`.

## Install a plugin

Use the plugin name you need with the private marketplace:

```text
/plugin install <plugin-name> --marketplace MikHaiLz404/skills-jojo-in-runtime
```

Available plugins:

| Plugin | Focus |
|---|---|
| `emily-strategy-planning` | Strategy, decision support, and project planning |
| `emily-visual-communication` | Brand guidance, infographics, presentations, and data stories |
| `emily-team-communications` | Google Chat webhook notifications and Card v2 updates |
| `emily-production-operations` | Jira–Kitsu ticket comparison, briefs, and guarded application |
| `emily-game-workflows` | Unreal exploration and game workflow support |
| `emily-3d-character-production` | First-party 3D scene-production guidance |

## External sources

This marketplace distributes only skills recorded as first-party in
[`external/sources.json`](external/sources.json). Third-party and
unverified skills are excluded from the catalog and Git history. Optional
local checkouts are stored in `external/checkouts/`, which Git ignores.

In particular, Caveman, Understand Anything, and the Stefan/Top3D Character
Sheet Pipeline remain external. Refresh an external checkout directly from
its own upstream; doing so never updates this marketplace.

## Sync and maintain

Clone the private repository and work from `develop`:

```sh
git clone https://github.com/MikHaiLz404/skills-jojo-in-runtime.git
cd skills-jojo-in-runtime
git switch develop
git pull --ff-only origin develop
```

Before publishing a marketplace update, run:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_marketplace.py .
claude plugin validate .
python3 scripts/verify_private_remote.py --owner MikHaiLz404
```

To push only after the remote, branch, clean worktree, and external-boundary
checks pass:

```sh
python3 scripts/verify_private_remote.py --owner MikHaiLz404 --push
```

## Contribution rules

- Keep each published plugin under an `emily-*` directory and list it in
  `.claude-plugin/marketplace.json`.
- Add an affirmative first-party provenance record before importing a skill.
- Preserve source attribution and keep external or unverified material out of
  the marketplace.
- Keep one skill in one Emily plugin; retain its required scripts, prompts,
  references, examples, and assets.
