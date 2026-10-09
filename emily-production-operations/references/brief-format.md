# Sync brief format

Use this format for a proposed or scheduled sync. Include only actions supported by the current source and target records.

```markdown
---
generated: <ISO-8601 timestamp>
applied: null
---

## Ticket sync — <scope and date>

### Create (N)
- <source key> <summary> -> <target entity and task type>

### Status changes (N)
- <source key>: <old target status> -> <new target status>

### Timeline changes (N)
- <source key>: <old start/due> -> <new start/due>; carry-over fix: <yes/no>

### Anomalies — skipped, not written (N)
- <source key or target record>: <reason>
```

For an apply result, add an `## Apply result` section with counts for applied, failed, and skipped actions. If any action fails, name its source key and error without retrying a materially different action.
