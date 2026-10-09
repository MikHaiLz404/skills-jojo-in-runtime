---
name: jira-kitsu-apply-brief
description: Apply the newest reviewed Jira-to-Kitsu sync brief after final confirmation. Use when a user asks to execute a pending weekly ticket-sync plan.
metadata:
  author: jojo-in-runtime
  version: 1.0.0
  source: jumbojumps-art-pipeline weekly apply workflow adaptation
---

# Apply a reviewed sync brief

1. Find unapplied `briefs/weekly-*.md` files, excluding `briefs/applied/`. If none exists, report that there is no pending plan.
2. Select the newest file by date. Name older unapplied briefs that are being skipped; do not silently discard them.
3. Re-display the brief's action counts and anomaly count. Ask for final explicit confirmation before any write.
4. On confirmation, apply exactly the Create, Status, and Timeline actions recorded in the chosen brief. Do not re-query Jira or generate a new diff; the reviewed plan is the authorized scope.
5. Continue after an individual write failure and record that line item as failed. Never write anomalies, create task types, or delete target records.
6. Add an `## Apply result` section using [the sync brief format](../../references/brief-format.md), set `applied` to the application time, and move the brief to `briefs/applied/` so it cannot run again accidentally.

Report actual applied, failed, and skipped counts with the source ticket keys. A partial apply is not a successful full sync.
