# LOCK-FIX Codex Task Plan

Use one branch and one PR per coherent task group. Keep each task small enough to review.

## Task 1: RBAC And Department Schema

- Verify role and permission enums.
- Verify department, user, role permission, approval, review, notification, and audit schema contracts.
- Update row mappers and tests when schema changes.

## Task 2: Approval Workflow Services

- Implement request creation.
- Assign department reviews automatically by request type.
- Enforce creator and duplicate approval rules.
- Enforce required approval counts and expiration.
- Keep execution APIs blocked until approvals are complete.

## Task 3: Department Review Collaboration

- Add department review APIs.
- Add review comments.
- Add notifications.
- Audit every comment and status transition.
- Keep final approval disabled until department review status allows it.

## Task 4: Web UI Permission And Workflow Views

- Hide unauthorized menus.
- Block direct URL access without permission.
- Show Repository Online request reason, department statuses, final approval count, approve and reject actions.
- Keep UI functions testable from `window.lockfixUiAuth`.

## Task 5: Audit And Export

- Ensure audit logs cannot be deleted through API.
- Audit denied access and blocked execution.
- Keep CSV export restricted to allowed roles.

## Task 6: Packaging And Offline Validation

- Validate installer can run in an offline network.
- Keep Veeam REST preflight checks explicit.
- Ensure installer never embeds real secrets.

## Task 7: PR Review

- Run `node --check web\static\app.js`.
- Run `python -m unittest tests.test_lockfix`.
- Review staged files for secrets and unrelated generated output.
- Open PR with summary, tests, and known residual risks.
