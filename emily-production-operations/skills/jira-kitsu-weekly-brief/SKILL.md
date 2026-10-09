---
name: jira-kitsu-weekly-brief
description: Prepare an unattended weekly Jira-to-Kitsu sync brief without changing Kitsu. Use for scheduled ticket-sync reviews, weekly production-tracker drift reports, or a pending sync plan.
metadata:
  author: jojo-in-runtime
  version: 1.0.0
  source: jumbojumps-art-pipeline weekly workflow adaptation
---

# Weekly Jira-to-Kitsu brief

Use this skill when no approver is present. It produces a durable plan; it never creates, updates, or deletes Kitsu records.

1. Establish the scope and exclude work already covered by a more frequent sync. Do not assume project codes, assignee lists, or schedules from another workspace.
2. Run the same discovery and linked-ticket refresh used by `jira-kitsu-ticket-sync`, including pagination and terminal-status refresh.
3. Compute proposed creates, status changes, timeline changes, and anomalies without calling any Kitsu write operation.
4. Write the full result as `briefs/weekly-YYYY-MM-DD.md` in the active project. Use [the sync brief format](../../references/brief-format.md) with `generated` set to the current ISO-8601 time and `applied: null`.
5. Notify the user only through a configured notification channel. If none is available, report the brief path when the next interactive session runs.

Never apply the brief in this skill. A separate confirmed apply step owns all writes.
