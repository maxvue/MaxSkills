---
name: damage-control
description: "Defensive safeguards, destructive command interception, and rollback patterns for automated agents. Use when reviewing potentially destructive terminal operations (rm, drop database, format, git reset --hard) to prevent data loss."
risk: critical
source: curated-youtube
---
# Damage Control: Destructive Command Safeguards

## When to Use
- Intercepting and vetting high-risk shell commands before execution.
- Preventing catastrophic file loss, database truncation, or unrecoverable git resets.
- Verifying safety constraints in automated agent execution pipelines.

## Critical Prohibited Patterns
1. **Unconstrained Removals:** Never execute `rm -rf /` or `rm -rf *` without explicit path constraints and user confirmation.
2. **Database Destruction:** Intercept `DROP DATABASE`, `TRUNCATE TABLE`, or `migrate:fresh` unless targeted at an ephemeral test container.
3. **Git Force Overwrites:** Block `git push --force` or `git reset --hard` on shared tracking branches (`main`, `master`, `develop`).

## Safe Alternatives
- Prefer soft-deletes or moving to `.trash/` instead of direct `rm`.
- Create explicit backup snapshots before bulk file mutations:
  ```bash
  cp -r target_folder target_folder.bak_$(date +%s)
  ```
