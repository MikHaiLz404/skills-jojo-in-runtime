---
name: jira-kitsu-ticket-sync
description: Compare Jira tickets with a Kitsu production tracker and prepare a reviewed sync plan. Use for ticket drift, new production tasks, status or timeline alignment, or Jira-to-Kitsu sync requests.
metadata:
  author: jojo-in-runtime
  version: 1.0.0
  source: jumbojumps-art-pipeline workflow adaptation
---

# Jira-to-Kitsu ticket sync

Treat Jira as the source of truth and Kitsu as the production tracker. Start with a project-specific mapping for source project, target project, in-scope assignees, task-type resolution, status mapping, and linked-record storage. Do not invent mappings, account identities, or Kitsu task types.

## Build the diff before writing

1. Confirm the intended source account and project scope. If a query unexpectedly returns no work or only an unrelated project, stop and ask for the correct connection or scope.
2. Query active candidate tickets for discovery. Include supported work-item types and follow every pagination token.
3. Separately refresh already-linked ticket keys without a status filter, so completed, cancelled, and reopened work is not missed.
4. Resolve a Kitsu task type from a valid ticket tag. If no valid tag exists, use a documented assignee/roster fallback only when it is unambiguous; otherwise record an anomaly.
5. Compare source status, dates, and estimates with the linked Kitsu task. Check carried-over work for stale previous-sprint dates.
6. Isolate anomalies instead of failing the whole batch: stale account identities, unresolved task type, missing or ambiguous linkage, and source/target name drift.

Read [the sync brief format](../../references/brief-format.md) and present the complete proposed Create, Status, Timeline, and Anomaly sections inline. Do not write until the user explicitly approves that exact brief in the same conversation.

## Apply an approved plan

Execute only the reviewed creates and updates. Do not auto-delete Kitsu tasks or entities, auto-create task types, or alter unlinked target records.

After each target write, re-read the affected task and verify the actual assignee and status. Correct a mismatched assignee or status using the documented mapping, then report the repair. Update project mapping documentation only when the project explicitly keeps such a mapping file.

Report applied, skipped, and failed actions separately. Keep anomalies visible for a later resolution; never silently drop them.
