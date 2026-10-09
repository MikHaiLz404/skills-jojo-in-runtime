# Private Emily Marketplace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a private, Git-synchronized marketplace that distributes only first-party Emily plugins and keeps external skills outside its install catalog and Git history.

**Architecture:** The repository root contains only marketplace metadata, first-party `emily-*` plugin packages, documentation, validation tooling, and a tracked external-source registry. Optional clones of third-party projects live under ignored `external/checkouts/`; `marketplace.json` permits only first-party source paths. A small standard-library Python validator enforces that boundary before Claude and Git validation.

**Tech Stack:** Claude Code plugin manifests, JSON, Markdown, Python 3 standard library, Git, GitHub CLI.

**Spec:** `docs/superpowers/specs/2026-10-09-emily-plugin-taxonomy-design.md`

## Global Constraints

- Publish only confirmed first-party skills under `emily-*` plugin identifiers.
- `jira-kitsu-ticket-management` is first-party and becomes `emily-production-operations`.
- Stefan Vaskevich / Top3D Character Sheet Pipeline sources are external and must not enter this marketplace.
- `caveman` and `understand-anything` are external and must not appear in `marketplace.json` or tracked Git files.
- Record external provenance without redistributing third-party source trees.
- Keep optional third-party clones below `external/checkouts/`, ignored by Git, and retain their nested `.git` directories unchanged.
- Use concise, calm Emily copy in all first-party plugin manifests.
- Preserve first-party skill names, required scripts, prompts, references, commands, examples, and assets.
- Create the GitHub repository as private; do not force-push or overwrite an existing remote repository.

## Review Focus

- External source leakage: a marketplace source, staged path, or plugin name must never point at `external/`, `caveman`, `understand-anything`, or Stefan/Top3D material; Task 2 validator and Task 7 staged-file check cover this.
- Nested Git preservation: moving each external checkout must retain its `.git` directory and its original `origin`; Task 3 checks both immediately after the move.
- Broken skill resources: relative links in moved `SKILL.md` files must still resolve to scripts, references, prompts, commands, examples, or assets; Task 4 checks every link-bearing skill before validation.
- Provenance ambiguity: candidate skills with no affirmative first-party registry record must remain external and cannot create an installable plugin; Task 2 validator and Task 5 import gate cover this.
- Private remote safety: an existing remote with a different GitHub owner, name, or visibility must stop publication before push; Task 7 verifies the target before setting `origin`.

---

## File Structure

| Path | Responsibility |
|---|---|
| `.claude-plugin/marketplace.json` | Private Emily marketplace catalog; contains first-party plugin entries only. |
| `.gitignore` | Excludes local external checkouts and machine artifacts from Git. |
| `external/README.md` | Explains why external sources are separated and how to refresh a local checkout. |
| `external/sources.json` | Machine-readable provenance, classification, upstream, license/status, and local checkout metadata. |
| `scripts/validate_marketplace.py` | Dependency-free validation of first-party catalog and external boundary. |
| `emily-strategy-planning/` | First-party strategy and planning skills. |
| `emily-visual-communication/` | First-party brand, infographic, data-storytelling, and presentation skills. |
| `emily-team-communications/` | First-party Google Chat webhook integration, including resources. |
| `emily-production-operations/` | First-party Jira–Kitsu ticket-management skills and references. |
| `emily-game-workflows/` | First-party Unreal explorer and Matcha Cat game workflow skills. |
| `emily-3d-character-production/` | First-party 3D production skills that pass the provenance gate. |
| `emily-sprite-asset-pipeline/` | First-party sprite/asset skills that pass the provenance gate. |
| `emily-granblue-routines/` | First-party Granblue routines that pass the provenance gate. |

### Task 1: Establish the marketplace-boundary validator

**Files:**
- Create: `scripts/validate_marketplace.py`
- Create: `tests/test_validate_marketplace.py`

**Interfaces:**
- Consumes: repository root containing `.claude-plugin/marketplace.json` and optionally `external/sources.json`.
- Produces: `python3 scripts/validate_marketplace.py [repository_root]` exits `0` when the catalog has no external leakage and prints one line per verified plugin; exits non-zero with an actionable path/name error otherwise.

- [ ] **Step 1: Initialize the local Git repository without staging project files**

Run: `test ! -e .git && git init -b main && git status --short`

Expected: Git reports an initialized `main` branch and a status listing existing files as untracked; no file is staged yet.

- [ ] **Step 2: Write failing validator tests in `tests/test_validate_marketplace.py`**

Cover a valid one-plugin fixture, an entry whose name lacks `emily-`, an entry whose source begins `./external/`, a missing source directory, and a source containing a nested `.git` directory. Assert that invalid fixtures return a non-zero exit code and identify the offending entry.

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 -m unittest tests/test_validate_marketplace.py -v`

Expected: FAIL because `scripts/validate_marketplace.py` does not exist.

- [ ] **Step 4: Implement `main(argv: Sequence[str]) -> int` in `scripts/validate_marketplace.py`**

Load JSON with the Python standard library. Require every plugin entry to have an `emily-` name, a relative source under the repository root, an existing `.claude-plugin/plugin.json`, and no nested `.git` ancestor. Reject `external`, `caveman`, `understand-anything`, and source paths outside the root. Print errors to stderr and return `1` on any violation.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python3 -m unittest tests/test_validate_marketplace.py -v`

Expected: PASS for all boundary cases.

- [ ] **Step 6: Commit the validator**

```bash
git add scripts/validate_marketplace.py tests/test_validate_marketplace.py
git commit -m "test: enforce marketplace ownership boundary"
```

### Task 2: Record external provenance and configure Git exclusions

**Files:**
- Create: `.gitignore`
- Create: `external/README.md`
- Create: `external/sources.json`
- Modify: `scripts/validate_marketplace.py`
- Modify: `tests/test_validate_marketplace.py`

**Interfaces:**
- Consumes: upstream URLs and provenance for Caveman, Understand Anything, and Stefan/Top3D Character Sheet Pipeline.
- Produces: external registry records with `name`, `classification`, `upstream`, `attribution`, `license_or_status`, `update`, and `local_checkout` fields.

- [ ] **Step 1: Extend tests for external registry structure**

Add fixtures asserting that the validator rejects a record missing `classification` or `upstream`, rejects an `external` record with `marketplace: true`, and accepts external records whose `local_checkout` is inside `external/checkouts/`.

- [ ] **Step 2: Run the tests to verify the registry tests fail**

Run: `python3 -m unittest tests/test_validate_marketplace.py -v`

Expected: FAIL because registry validation is not implemented.

- [ ] **Step 3: Add registry validation to `scripts/validate_marketplace.py`**

Require known external entries `caveman`, `understand-anything`, `character-sheet-pipeline`, and `character-sheet-pipeline-openai` with `classification: "external"` and `marketplace: false`. Allow `unverified` candidates but reject any `external` or `unverified` record that declares marketplace availability.

- [ ] **Step 4: Create `.gitignore`, `external/README.md`, and `external/sources.json`**

Ignore `external/checkouts/`, `.DS_Store`, Python bytecode, and `__pycache__/`. In the registry, write upstream and attribution for the three known external sources; write each optional candidate as `unverified` unless a documented first-party decision is available. In the README, document `git -C external/checkouts/<source> pull --ff-only` as a local-only upstream refresh and state that it does not update the Emily marketplace.

- [ ] **Step 5: Run the validator and tests**

Run: `python3 -m unittest tests/test_validate_marketplace.py -v && python3 scripts/validate_marketplace.py .`

Expected: all tests pass; the current legacy catalog is expected to fail the validator until Task 6 rewrites it.

- [ ] **Step 6: Commit the boundary metadata**

```bash
git add .gitignore external scripts/validate_marketplace.py tests/test_validate_marketplace.py
git commit -m "docs: record external skill provenance"
```

### Task 3: Separate external checkouts without modifying them

**Files:**
- Move: `caveman/` → `external/checkouts/caveman/`
- Move: `understand-anything/` → `external/checkouts/understand-anything/`
- Modify: `external/sources.json`

**Interfaces:**
- Consumes: the two existing external working trees at repository root.
- Produces: ignored local checkouts at the paths declared in the registry, each retaining its upstream `origin`.

- [ ] **Step 1: Capture the current upstream remotes and HEAD revisions**

Run: `git -C caveman remote get-url origin && git -C caveman rev-parse HEAD && git -C understand-anything remote get-url origin && git -C understand-anything rev-parse HEAD`

Expected: record the four values in the task log before moving either tree.

- [ ] **Step 2: Move the two directories with a filesystem rename**

Create `external/checkouts/`, then move exactly `caveman` and `understand-anything` into it. Do not run any Git command inside either checkout and do not copy its source files into a tracked path.

- [ ] **Step 3: Verify nested Git and upstream preservation**

Run: `git -C external/checkouts/caveman remote get-url origin && git -C external/checkouts/caveman rev-parse HEAD && git -C external/checkouts/understand-anything remote get-url origin && git -C external/checkouts/understand-anything rev-parse HEAD`

Expected: all four values exactly equal the values captured in Step 1.

- [ ] **Step 4: Update the registry checkout paths and verify Git ignores them**

Run: `git check-ignore -v external/checkouts/caveman/.git external/checkouts/understand-anything/.git`

Expected: both paths match `.gitignore`'s `external/checkouts/` rule.

- [ ] **Step 5: Commit only the registry update**

```bash
git add external/sources.json
git commit -m "chore: relocate external checkouts"
```

### Task 4: Split existing confirmed first-party packages by work domain

**Files:**
- Create: `emily-strategy-planning/.claude-plugin/plugin.json`
- Create: `emily-visual-communication/.claude-plugin/plugin.json`
- Create: `emily-team-communications/.claude-plugin/plugin.json`
- Create: `emily-production-operations/.claude-plugin/plugin.json`
- Create: `emily-game-workflows/.claude-plugin/plugin.json`
- Move: skills/resources from `emily-core-skills/`, `emily-planning/`, `emily-presentation-system/`, `emily-google-chat-webhook/`, and `jira-kitsu-ticket-management/`
- Remove: those five superseded source package directories after verification

**Interfaces:**
- Consumes: existing first-party package files and resource trees.
- Produces: five domain-specific first-party plugin directories, each with one manifest and no duplicate skill names.

- [ ] **Step 1: Make an expected-skill inventory test fixture**

In `tests/test_validate_marketplace.py`, add an integration fixture whose expected plugin-to-skill mapping is: strategy (`emily-advisor-strategy`, `grill-me`, `grill-with-docs`, `grilling`, `wayfinder`); visual (`emily-brand-unified-guidelines`, `emily-infographic-gen`, `data-storytelling`, `presentation-generation`, `visualization-expert`); team (`emily-google-chat-webhook`); operations (`jira-kitsu-ticket-sync`, `jira-kitsu-weekly-brief`, `jira-kitsu-apply-brief`); game (`emily-unreal-explorer`, `matcha-cat-memory-game`).

- [ ] **Step 2: Run the integration test to verify it fails against the legacy package names**

Run: `python3 -m unittest tests/test_validate_marketplace.py -v`

Expected: FAIL because the five `emily-*` target directories do not yet exist.

- [ ] **Step 3: Move each first-party skill and its resources into its target package**

Move complete skill directories, not individual `SKILL.md` files. Preserve the Google Chat package's `commands/`, `scripts/`, `references/`, `examples/`, and `assets/`; preserve the Jira–Kitsu `references/` tree. Write one `plugin.json` per target with the exact package name, `jojo-in-runtime` author, and Emily-focused keywords.

- [ ] **Step 4: Verify resource links and package manifests**

For each moved skill, resolve every Markdown link that uses a relative local path. Run `claude plugin validate` on all five new directories.

Expected: every referenced local resource exists and every plugin validation passes.

- [ ] **Step 5: Remove obsolete first-party package roots after confirmation**

Remove only `emily-core-skills/`, `emily-planning/`, `emily-presentation-system/`, `emily-google-chat-webhook/`, and `jira-kitsu-ticket-management/` after the inventory test and plugin validations pass. Do not remove `external/`.

- [ ] **Step 6: Run the integration test and commit the split**

Run: `python3 -m unittest tests/test_validate_marketplace.py -v`

Expected: PASS, with every expected skill in exactly one target package.

```bash
git add -A -- . ':!external/checkouts'
git commit -m "feat: split Emily skills by workflow domain"
```

### Task 5: Import only approved local 3D, sprite, and Granblue skills

**Files:**
- Create or modify: `emily-3d-character-production/`
- Create or modify: `emily-sprite-asset-pipeline/`
- Create or modify: `emily-granblue-routines/`
- Modify: `external/sources.json`
- Modify: `tests/test_validate_marketplace.py`

**Interfaces:**
- Consumes: candidate directories under `/Users/jojo/.agents/skills/` and their registry classification.
- Produces: only candidate skills with `classification: "first-party"` copied into exactly one Emily package; others stay external/unverified and are not copied.

- [ ] **Step 1: Add a provenance-gate test**

Test that a candidate listed as `unverified` or `external` cannot appear in any package inventory, while an explicitly `first-party` candidate must appear once in the declared target package.

- [ ] **Step 2: Run the tests to verify the provenance gate fails**

Run: `python3 -m unittest tests/test_validate_marketplace.py -v`

Expected: FAIL because the validator has not compared the registry and package contents.

- [ ] **Step 3: Implement registry-to-package enforcement and record decisions**

Extend `scripts/validate_marketplace.py` to compare registry candidates with discovered `skills/*/SKILL.md` names. Record `3d-scene-gen` as first-party evidence from its `author: jojo-in-runtime` metadata. Do not classify a candidate first-party without recorded evidence; leave it `unverified` otherwise.

- [ ] **Step 4: Copy approved skill directories and normalize only their frontmatter**

Copy approved skills with their direct supporting files: `agents/openai.yaml`, `references/`, and `scripts/` when present. Move no `.DS_Store` or `__pycache__`. Convert legacy `author`, `tags`, `version`, `updated`, or `co-author` fields into valid skill metadata without erasing attribution. Do not copy either Stefan character-sheet variant.

- [ ] **Step 5: Validate every copied skill and its plugin**

Run the repository skill validator on each copied `SKILL.md`, then run `claude plugin validate` for every non-empty new plugin directory.

Expected: all included skills and plugin manifests validate; unverified candidates appear only in `external/sources.json`.

- [ ] **Step 6: Run the provenance test and commit approved imports**

Run: `python3 -m unittest tests/test_validate_marketplace.py -v && python3 scripts/validate_marketplace.py .`

Expected: PASS; no external or unverified candidate occurs below an `emily-*` source directory.

```bash
git add emily-3d-character-production emily-sprite-asset-pipeline emily-granblue-routines external/sources.json scripts/validate_marketplace.py tests/test_validate_marketplace.py
git commit -m "feat: add approved Emily production workflows"
```

### Task 6: Publish the first-party-only marketplace catalog

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `tests/test_validate_marketplace.py`

**Interfaces:**
- Consumes: valid `emily-*` plugin source directories from Tasks 4–5.
- Produces: marketplace version `2.0.0`, containing exactly the non-empty first-party Emily plugin packages and no legacy/external entry.

- [ ] **Step 1: Add marketplace catalog assertions**

Assert that every entry name starts with `emily-`, every source is a current package directory, `caveman`, `understand-anything`, `character-sheet-pipeline`, and legacy package names are absent, and the package set exactly equals the non-empty validated packages on disk.

- [ ] **Step 2: Run the test to confirm it fails against version `1.3.0`**

Run: `python3 -m unittest tests/test_validate_marketplace.py -v`

Expected: FAIL due to external and legacy entries in the catalog.

- [ ] **Step 3: Rewrite `.claude-plugin/marketplace.json` as version `2.0.0`**

Use concise Emily descriptions and domain-appropriate categories. Include operations as `emily-production-operations`; include optional 3D, sprite, and Granblue packages only if their directory is non-empty and has passed Task 5 validation. Do not add aliases to old package names.

- [ ] **Step 4: Run complete marketplace validation**

Run: `python3 -m unittest tests/test_validate_marketplace.py -v && python3 scripts/validate_marketplace.py . && claude plugin validate .`

Expected: all three commands pass and the validator lists first-party Emily plugins only.

- [ ] **Step 5: Commit the catalog release**

```bash
git add .claude-plugin/marketplace.json tests/test_validate_marketplace.py
git commit -m "feat: publish private Emily marketplace catalog"
```

### Task 7: Create and verify the private GitHub remote

**Files:**
- Modify: `.git/` metadata created by Git; no tracked source-file changes are expected.

**Interfaces:**
- Consumes: a fully validated local repository and authenticated GitHub CLI account.
- Produces: private `origin` remote named `<authenticated-login>/skills-jojo-in-runtime`, with local and remote HEAD at the same commit.


- [ ] **Step 1: Inspect the prospective tracked set**

Run: `git status --short && git check-ignore -v external/checkouts/caveman/.git external/checkouts/understand-anything/.git`

Expected: external checkout paths are ignored; no unexpected credentials, cache files, or nested external sources are in the status output.

- [ ] **Step 2: Stage, inspect, and commit the complete first-party repository**

Run: `git add . && git diff --cached --name-only && git diff --cached --check && git status --short`

Expected: the staged list contains no `external/checkouts/`, `caveman/`, `understand-anything/`, `.DS_Store`, or `__pycache__`; whitespace check passes.

Commit only after that check passes:

```bash
git commit -m "chore: initialize private Emily marketplace"
```

- [ ] **Step 3: Resolve the authenticated owner and check for an existing target**

Run: `gh auth status && gh api user --jq .login && gh repo view "$(gh api user --jq .login)/skills-jojo-in-runtime" --json name,visibility,url 2>/dev/null || true`

Expected: record the authenticated login. If a repository exists, continue only when its name is `skills-jojo-in-runtime`, visibility is `PRIVATE`, and it is intended as this marketplace; otherwise stop for user direction.

- [ ] **Step 4: Create or attach the private remote without overwriting history**

If the repository does not exist, run: `gh repo create skills-jojo-in-runtime --private --source=. --remote=origin --push`.

If the verified intended repository already exists, add its clone URL as `origin`, fetch it, inspect divergence with `git log --oneline --left-right main...origin/main`, and push only when no unrelated remote history would be overwritten.

- [ ] **Step 5: Verify privacy, synchronization, and cleanliness**

Run: `gh repo view --json visibility,url --jq '.visibility + " " + .url' && git rev-parse HEAD && git rev-parse origin/main && git status --short && git ls-files external/checkouts`

Expected: visibility reports `PRIVATE`; the two commit IDs are identical; worktree is clean; `git ls-files external/checkouts` prints nothing.

- [ ] **Step 6: Commit any final tracked metadata only when necessary**

If no tracked files changed after the initial commit, do not create an empty commit. Otherwise inspect and commit the exact file list with `git add <paths>` and `git commit -m "chore: finalize marketplace metadata"` before repeating Step 5.

## Self-review

- Spec coverage: Tasks 1–2 enforce the ownership boundary and registry; Task 3 separates known external clones; Tasks 4–5 build first-party packages; Task 6 produces the install catalog; Task 7 initializes and verifies the private remote.
- Step scan: each task starts with a failing or baseline check, makes one cohesive implementation change, and ends with validation plus a reviewable commit.
- Type/interface consistency: all package names, registry fields, validator entry point, and GitHub repository name are defined once and reused unchanged.
- Review focus: every listed failure mode has a named validator, test, or Git verification step in its owning task.
- Proportion: the plan specifies package boundaries and validation contracts without duplicating skill bodies or third-party sources.
