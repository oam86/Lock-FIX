# LOCK-FIX Agent Instructions

## Project Baseline

- Repository remote: `https://github.com/oam86/Lock-FIX.git`
- Primary working source: this repository root.
- Keep release package output, runtime state, credentials, and generated build folders out of feature commits unless the task explicitly targets packaging.
- Do not commit real Veeam credentials, Windows passwords, tokens, audit logs, runtime approval stores, or installer secrets.

## Security And Approval Rules

- Never add an audit log delete API or `AUDIT_LOG_DELETE` permission.
- The request creator cannot approve their own approval request.
- The same user cannot approve the same request twice.
- Required department reviews must be completed before final approval can proceed.
- `NEEDS_CHANGES` blocks final approval until the requester resubmits or the review is corrected.
- `BLOCKED` department reviews require Super Admin exception handling.
- Dual approval operations cannot be completed by Super Admin alone.
- Execution APIs for `DISK_ONLINE`, `POLICY_CHANGE`, `EMERGENCY_UNLOCK`, `HARDWARE_POWER_ON`, and `HARDWARE_POWER_OFF` must remain blocked until approval policy requirements are met.
- Emergency unlock must require a reason, department review where configured, dual approval, and audit logging.
- Unauthorized or insufficient-permission access must return `403 Forbidden` and write an audit event.
- All request creation, department review comments, review status changes, approval/rejection decisions, execution attempts, blocked execution, and failures must be audit logged.

## Department Collaboration Rules

- `ApprovalRequest.reviewDepartments` must be assigned from request type policy.
- `DepartmentReview` status values are `PENDING`, `IN_REVIEW`, `REVIEWED`, `NEEDS_CHANGES`, and `BLOCKED`.
- Review comments are stored separately from department review state.
- Notifications are stored separately and must point back to the target approval request.
- Repository Online requests must clearly show:
  - request reason
  - Security review status
  - Hardware Control review status
  - final approval count
  - approve/reject actions only for eligible approvers

## Development Workflow

- Prefer small task-scoped commits.
- Keep unrelated dirty files out of commits. This repo may have local `webui.py` changes that are not part of a current task.
- Use existing local patterns before adding new abstractions.
- Update tests when changing RBAC, approval, audit, schema, or Web UI authorization behavior.
- Run at minimum:

```powershell
node --check web\static\app.js
python -m unittest tests.test_lockfix
```

If `python` is unavailable on PATH in Codex Desktop, use the bundled runtime path reported by `load_workspace_dependencies`.

## PR Checklist

- [ ] GitHub remote is `origin`.
- [ ] Branch name starts with `codex/`.
- [ ] No secrets or runtime data are staged.
- [ ] Approval/security rules above still hold.
- [ ] Tests pass.
- [ ] PR description lists changed files, test results, and residual risks.
