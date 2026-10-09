# Private Emily marketplace and plugin taxonomy design

## Goal

Turn this workspace into a private, Git-backed Emily marketplace so the
first-party plugin catalog has one canonical remote and can be synchronized
across machines. The marketplace is a distribution channel for Emily-owned
work only. It must never publish, rebrand, or vend third-party skills.

## Ownership boundary

Every candidate skill is classified before it can enter a plugin:

| Classification | Repository treatment | Marketplace treatment |
|---|---|---|
| First party | Tracked inside an `emily-*` plugin and branded consistently with Emily | Listed in `marketplace.json` |
| External | Recorded with upstream URL, license, version or commit, and attribution in the external registry; optional local checkout is ignored | Not listed or installable from this marketplace |
| Unverified | Held in the external registry until ownership and redistribution permission are confirmed | Not listed or installable from this marketplace |

Known external skills are `caveman`, `understand-anything`, and both
Character Sheet Pipeline variants attributed to Stefan Vaskevich / Top3D.
They remain intact for local reference, but neither their source trees nor
their plugin manifests are published through the Emily marketplace.

The following copied skills need an explicit provenance decision before they
can be considered first party: `low-poly-diorama`,
`character-sprite-animation`, `isometric-asset-sheets`, and
`strip-asset-cutter`. They must stay external until that decision is recorded.

## Repository and sync model

- Initialize the existing `skills-jojo-in-runtime` directory as a Git
  repository and publish it to one private GitHub repository. Its exact GitHub
  owner is selected from the authenticated account at publish time; the
  repository name defaults to `skills-jojo-in-runtime`.
- The remote `origin` is the canonical source for all first-party Emily
  plugins. Updating another machine is a normal `git pull`; changes return by
  commit and push.
- Track only first-party plugin sources, marketplace metadata, validation
  tooling, documentation, and the external-source registry.
- Store the registry as `external/sources.json` plus a short `external/README.md`.
  It records provenance and an update command or URL, but contains no
  third-party source distribution.
- Place optional local third-party clones at `external/checkouts/<source>/` and
  ignore that path in `.gitignore`. Move the existing `caveman` and
  `understand-anything` clones there without altering their nested Git history.
  Updating an external checkout remains an upstream-specific operation, not a
  marketplace update.

This arrangement keeps the shared marketplace small, auditable, and free of
nested repositories while preserving a local reference to external work.

## First-party plugin layout

The marketplace contains only confirmed first-party `emily-*` plugins. The
intended domain split is:

| Plugin | Confirmed or candidate skills |
|---|---|
| `emily-strategy-planning` | `emily-advisor-strategy`, `grill-me`, `grill-with-docs`, `grilling`, `wayfinder` |
| `emily-visual-communication` | `emily-brand-unified-guidelines`, `emily-infographic-gen`, `data-storytelling`, `presentation-generation`, `visualization-expert` |
| `emily-team-communications` | `emily-google-chat-webhook` |
| `emily-production-operations` | `jira-kitsu-ticket-sync`, `jira-kitsu-weekly-brief`, `jira-kitsu-apply-brief` |
| `emily-game-workflows` | `emily-unreal-explorer`, `matcha-cat-memory-game` |
| `emily-3d-character-production` | `3d-scene-gen`; add `low-poly-diorama` only if classified first party |
| `emily-sprite-asset-pipeline` | Add `character-sprite-animation`, `isometric-asset-sheets`, and `strip-asset-cutter` only if classified first party |
| `emily-granblue-routines` | `granblue-daily-mission`, `granblue-event-raid-battle`, `granblue-event-special-quests`, subject to the same provenance gate |

No plugin entry is created for a candidate that has not passed the ownership
boundary. In particular, the character-sheet pipeline is external and does not
belong in `emily-3d-character-production`.

Each published plugin has a `.claude-plugin/plugin.json` manifest with an
`emily-` name, calm concise Emily copy, `jojo-in-runtime` as its author, and
domain-specific keywords. Existing first-party skill invocation names remain
unchanged. The Emily brand-guideline skill remains the source of truth for
visual-language and copy decisions; unsupported manifest fields such as colors
or artwork are not invented.

## Migration

1. Create the new plugin directories and move confirmed first-party skills
   from the current broad packages into their single domain package.
2. Copy eligible local skills only after writing their provenance decision into
   the registry. Preserve their required scripts, prompts, references, and UI
   metadata; normalize legacy skill frontmatter without removing attribution.
3. Replace the current legacy marketplace entries with the first-party
   `emily-*` plugins only. The manifest contains no `caveman`,
   `understand-anything`, or other external entry.
4. Move the existing third-party working trees into ignored
   `external/checkouts/`, then create the tracked external registry and
   README. Do not change upstream source trees.
5. Remove superseded first-party package directories only after every
   destination is validated.
6. Initialize Git, add the private GitHub remote, make the initial commit, and
   push only after the resulting repository status and staged file list have
   been reviewed.

## Compatibility and risk

This is an intentional breaking change for existing first-party plugin install
identifiers:

- `emily-core-skills` becomes scoped Emily plugins.
- `emily-planning` becomes `emily-strategy-planning`.
- `emily-presentation-system` becomes `emily-visual-communication`.
- `emily-google-chat-webhook` becomes `emily-team-communications`.
- `jira-kitsu-ticket-management` becomes `emily-production-operations`.

Skill names remain stable after their first-party plugin is installed. The
marketplace supplies no aliases pointing to duplicated sources. External skills
must be installed and updated directly from their own upstreams.

The OpenAI Agents SDK character-sheet variant remains excluded: it is external
and its image-generation adapters are stubs.

## Verification

1. Confirm every marketplace entry is an `emily-*` first-party source and its
   directory and manifest exist.
2. Confirm no external source path, nested Git repository, or third-party
   plugin name appears in `marketplace.json` or Git's staged file list.
3. Validate all published `SKILL.md` files and run `claude plugin validate` for
   each published plugin and the marketplace.
4. Confirm every published skill appears exactly once across the Emily plugins.
5. Verify `external/sources.json` identifies every separated source with its
   upstream, attribution, license/status, and update path.
6. Verify a clean clone can install the first-party marketplace and that an
   external checkout remains absent from tracked files.
7. Verify the public remote, initial push, clean worktree, and matching local
   and `origin` commit IDs.

## Out of scope

- Publishing or redistributing external skills through the Emily marketplace.
- Changing third-party source trees or their upstream Git history.
- Inventing provenance, licensing, credentials, visual assets, schedules, or
  workspace-specific data.
- Shipping the OpenAI character-pipeline runtime before its adapters are
  implemented and tested.
