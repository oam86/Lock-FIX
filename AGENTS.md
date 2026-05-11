# LOCK-FIX Development Guide

## Product Overview

LOCK-FIX is a backup-storage isolation security solution.

It integrates with Veeam backup jobs and controls repository isolation through software-level and hardware-level workflows.

The product must be developed as an enterprise-grade security solution with role-based access control, approval workflow, two-person approval, department review, and immutable audit logging.

## Current PoC Context

The current LOCK-FIX PoC already includes:

- CLI control flow: status, isolate, reconnect, uid
- Backup completion isolation flow
- Flush and I/O completion confirmation
- Volume unmount
- Disk offline / isolation state
- UID verification
- Hash verification
- Quarantine state on verification failure
- Local Web UI
- Report export
- Mock-based dry_run mode

Do not remove or break existing PoC behavior.

## Required Roles

The system must support the following roles:

- SUPER_ADMIN
- SECURITY_ADMIN
- BACKUP_OPERATOR
- HARDWARE_ADMIN
- AUDITOR
- UI_DESIGNER
- DEVELOPER

## Required Departments

The system must support the following departments:

- Management
- Security
- Backup Operation
- Hardware Control
- Audit
- Development
- Web Design

## Permission Rules

Implement role-based access control.

Suggested permissions:

- DASHBOARD_VIEW
- USER_MANAGE
- ROLE_MANAGE
- VEEAM_VIEW
- VEEAM_MANAGE
- AIRGAP_POLICY_VIEW
- AIRGAP_POLICY_MANAGE
- DISK_OFFLINE_REQUEST
- DISK_OFFLINE_EXECUTE
- DISK_ONLINE_REQUEST
- DISK_ONLINE_APPROVE
- HARDWARE_CONTROL
- APPROVAL_REQUEST_VIEW
- APPROVAL_REQUEST_CREATE
- APPROVAL_REQUEST_APPROVE
- DEPARTMENT_REVIEW
- AUDIT_LOG_VIEW
- REPORT_EXPORT
- SYSTEM_SETTING_MANAGE

Permission failures must return 403 Forbidden.

Unauthorized access attempts must be recorded in AuditLog.

## Approval Request Types

The system must support the following approval request types:

- DISK_ONLINE
- DISK_OFFLINE
- POLICY_CHANGE
- EMERGENCY_UNLOCK
- HARDWARE_POWER_ON
- HARDWARE_POWER_OFF

## Two-Person Approval Rules

The following request types require two-person approval:

- DISK_ONLINE
- POLICY_CHANGE
- EMERGENCY_UNLOCK
- HARDWARE_POWER_ON
- HARDWARE_POWER_OFF

Default approval counts:

- DISK_ONLINE: 2 approvals
- DISK_OFFLINE: 1 approval
- POLICY_CHANGE: 2 approvals
- EMERGENCY_UNLOCK: 2 approvals
- HARDWARE_POWER_ON: 2 approvals
- HARDWARE_POWER_OFF: 2 approvals

## Mandatory Approval Rules

The request creator cannot approve their own request.

The same user cannot approve the same request more than once.

SUPER_ADMIN cannot bypass two-person approval for critical operations.

Approval must be completed before executing the actual operation.

Critical operation execution must be blocked until the approval policy is satisfied.

## Department Review Rules

Before final approval, required departments must complete their review.

Default department review mapping:

- DISK_ONLINE:
  - Security
  - Hardware Control

- DISK_OFFLINE:
  - Backup Operation
  - Security

- POLICY_CHANGE:
  - Security
  - Audit

- EMERGENCY_UNLOCK:
  - Security
  - Hardware Control
  - Audit

- HARDWARE_POWER_ON:
  - Hardware Control
  - Security

- HARDWARE_POWER_OFF:
  - Hardware Control
  - Security

Final approval must not be enabled until all required department reviews are completed.

If any department marks NEEDS_CHANGES, the request must return to the requester for revision.

If any department marks BLOCKED, only SUPER_ADMIN can start an exception review process.

## Audit Log Rules

Audit logs must be append-only from the application perspective.

Do not implement audit log delete API.

No user, including SUPER_ADMIN, can delete audit logs through the application.

The following events must always be recorded:

- Login success
- Login failure
- User creation
- User update
- User disable
- Role change
- Permission change
- Approval request creation
- Department review comment
- Department review completion
- Needs changes
- Blocked review
- Approval
- Rejection
- Approval expiration
- Disk online request
- Disk offline request
- Hardware power on request
- Hardware power off request
- Policy change request
- Emergency unlock request
- Execution success
- Execution failure
- Unauthorized access attempt
- 403 Forbidden response

## Backend Requirements

Add models or equivalent structures for:

- Department
- User role and department mapping
- RolePermission
- ApprovalRequest
- ApprovalPolicy
- ApprovalDecision
- DepartmentReview
- ReviewComment
- Notification
- AuditLog

All critical business rules must be enforced in the backend service layer.

Do not rely only on frontend checks.

## Web UI Requirements

Add or prepare UI screens for:

- User & Role Management
- Department Management
- Approval Requests
- My Requests
- Pending Approval
- Department Review
- Review Comments
- Approved Requests
- Rejected Requests
- Expired Requests
- Audit Logs
- Reports

The sidebar menu must be displayed according to the logged-in user’s permissions.

Direct URL access must still be blocked by backend permissions.

For two-person approval, show approval progress.

Example:

1 / 2 approved

The approve button must not be visible for the request creator.

The approve button must not be visible for users without approval permission.

## Testing Requirements

Add tests for:

- Permission allowed
- Permission denied
- 403 audit logging
- Request creator cannot approve own request
- Same user cannot approve twice
- Required approval count
- Two-person approval
- Department review required before approval
- NEEDS_CHANGES blocks approval
- BLOCKED review blocks normal approval
- Audit log creation
- Audit log delete API absence

## Development Rules

Do not refactor unrelated code.

Do not remove existing PoC files.

Keep changes focused and reviewable.

Use mock mode for hardware, Veeam, disk, and power-control tests unless explicitly requested otherwise.

Do not include real production secrets, customer credentials, Veeam credentials, SMTP passwords, or hardware control credentials.

## Pull Request Rules

Every PR must include:

- Summary
- Changed files
- Security-sensitive changes
- Test results
- Remaining limitations
- Next recommended task
