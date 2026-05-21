from __future__ import annotations

import json
import os
import time
import unittest
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import webui
from lockfix.agent_service import AgentServiceClient, AgentServiceUnavailable, AgentServiceWorker
from lockfix.config import load_config, normalize_operation_mode
from lockfix.controller import LockFixController, repository_volume_root
from lockfix.disk import DiskOperator
from lockfix.command import CommandError, CommandRunner
from lockfix.audit import AuditLogger
from lockfix.hashcheck import manifest_digest
from lockfix.identity import compute_uid, fingerprint_parts, slot_uid
from lockfix.offline_reconnect_validation import run_offline_reconnect_validation
from lockfix.approvals import ApprovalStore
from lockfix.audit_log import AUDIT_LOG_FIELDS, audit_logs_to_csv, read_audit_logs, tail_text_lines
from lockfix.rbac import AuthorizationError, Permission, Role, default_policy_document, has_permission, load_role_permissions
from lockfix.schema import (
    LOCKFIX_TABLE_SCHEMA,
    approval_decision_row,
    approval_policy_row,
    approval_request_row,
    audit_log_row,
    department_review_row,
    departments_row,
    notification_row,
    review_comment_row,
    load_schema_sql,
    role_permissions_rows,
    users_row,
)
from lockfix.state_store import StateStore
from lockfix.states import LockFixState
from lockfix.users import UserDirectory
from lockfix.veeam_client import VeeamAuthenticationError, VeeamClient, VeeamSettings, enrich_summary_with_logs, filter_target_repositories, match_backups, restore_point_summary, session_summary
from lockfix.veeam_console_logs import latest_backup_copy_console_log_summary
from lockfix.veeam_factory import create_veeam_client
from lockfix.veeam_diagnostics import run_veeam_diagnostics
from lockfix.veeam_webui_check import WebUiServerNotRunning, compare_veeam_test_with_webui, summarize_webui_backup
from lockfix.veeam_watcher import VeeamWatcher


def write_config(tmp_path: Path, expected_uid: str = "") -> Path:
    mount = tmp_path / "mount"
    mount.mkdir()
    (mount / "backup.dat").write_text("payload", encoding="utf-8")
    (mount / ".lockfix_manifest.sha256").write_text(manifest_digest(mount), encoding="utf-8")
    config = {
        "dry_run": True,
        "state_path": str(tmp_path / "state.json"),
        "audit_log_path": str(tmp_path / "audit.jsonl"),
        "io_quiet_seconds": 1,
        "disk_wait_seconds": 1,
        "slots": [
            {
                "slot_id": "BAY-01",
                "device": "D:\\",
                "mount_point": str(mount),
                "expected_uid": expected_uid,
                "identity": {"serial": "S1", "model": "M1", "wwn": "W1"},
                "manifest_path": ".lockfix_manifest.sha256",
                "power": {"type": "mock", "off_command": [], "on_command": []},
            }
        ],
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


class LockFixTests(unittest.TestCase):
    def make_workspace(self) -> Path:
        root = Path.cwd() / "runtime" / f"test-{uuid.uuid4().hex}"
        root.mkdir(parents=True, exist_ok=True)
        return root

    def approve_operation(self, controller: LockFixController, request_type: str, slot_id: str = "BAY-01") -> dict:
        metadata = {"reason": "unit test emergency unlock"} if request_type == "EMERGENCY_UNLOCK" else {}
        request = controller.approvals.create_request(request_type, "requester", target_id=slot_id, metadata=metadata)
        for review in controller.approvals.department_reviews_for(request["id"]):
            role = {
                "security": Role.SECURITY_ADMIN,
                "backup-operation": Role.BACKUP_OPERATOR,
                "hardware-control": Role.HARDWARE_ADMIN,
                "audit": Role.AUDITOR,
            }.get(review["departmentId"], Role.SUPER_ADMIN)
            controller.approvals.mark_department_reviewed(
                request["id"],
                review["id"],
                f"{review['departmentId']}-reviewer",
                role,
                "department review completed",
            )
        required = int(request["requiredApprovals"])
        if request_type == "DISK_ONLINE":
            controller.approvals.review_request(request["id"], "security-reviewer", Role.SECURITY_ADMIN, "SECURITY_LOG_REVIEW", "isolation logs reviewed")
            controller.approvals.review_request(request["id"], "hardware-reviewer", Role.HARDWARE_ADMIN, "HARDWARE_STATE_REVIEW", "disk and lock state checked")
            controller.approvals.review_request(request["id"], "manager-reviewer", Role.SUPER_ADMIN, "MANAGER_REVIEW", "team opinions reviewed")
            approvers = [("approver-1", Role.SECURITY_ADMIN), ("approver-2", Role.SUPER_ADMIN)]
        else:
            approvers = [
                ("approver-1", Role.SUPER_ADMIN),
                ("approver-2", Role.SECURITY_ADMIN),
                ("approver-3", Role.HARDWARE_ADMIN),
            ]
        result = {"request": request}
        for approver_id, role in approvers[:required]:
            result = controller.approvals.decide(request["id"], approver_id, role, "APPROVED")
        return result["request"]

    def complete_department_reviews(self, store: ApprovalStore, request: dict) -> None:
        for review in store.department_reviews_for(request["id"]):
            role = {
                "security": Role.SECURITY_ADMIN,
                "backup-operation": Role.BACKUP_OPERATOR,
                "hardware-control": Role.HARDWARE_ADMIN,
                "audit": Role.AUDITOR,
            }.get(review["departmentId"], Role.SUPER_ADMIN)
            store.mark_department_reviewed(
                request["id"],
                review["id"],
                f"{review['departmentId']}-reviewer",
                role,
                "department review completed",
            )

    def test_compute_uid_is_stable(self) -> None:
        self.assertEqual(
            compute_uid("S1", "M1", "W1", "BAY-01"),
            compute_uid("S1", "M1", "W1", "BAY-01"),
        )

    def test_config_loader_accepts_utf8_bom(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = config_path.read_text(encoding="utf-8")
        config_path.write_text("\ufeff" + raw, encoding="utf-8")

        config = load_config(config_path)

        self.assertEqual(config.slot("BAY-01").device, "D:\\")

    def test_operation_mode_defaults_and_aliases(self) -> None:
        self.assertEqual(normalize_operation_mode(None, False), "commercial")
        self.assertEqual(normalize_operation_mode("live", False), "commercial")
        self.assertEqual(normalize_operation_mode("production", False), "commercial")
        self.assertEqual(normalize_operation_mode("poc", True), "poc")
        self.assertEqual(normalize_operation_mode("dry_run", True), "poc")
        self.assertEqual(normalize_operation_mode("delivery", False), "delivery")
        self.assertEqual(normalize_operation_mode(None, True), "poc")

    def test_agent_service_document_includes_delivery_permission_table(self) -> None:
        text = Path("docs/agent_service_architecture.md").read_text(encoding="utf-8")

        self.assertIn("권한 요구사항 / 제한 기능 / 해결 방법", text)
        self.assertIn("Disk Offline", text)
        self.assertIn("Veeam REST API", text)
        self.assertIn("승인 워크플로우", text)

    def test_webui_inline_fallback_is_poc_only(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        context = webui.WebContext(config_path)
        self.assertEqual(context.operation_mode(), "poc")
        self.assertTrue(context.agent_service.allow_inline_fallback)

        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["operation_mode"] = "commercial"
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        context = webui.WebContext(config_path)
        self.assertEqual(context.operation_mode(), "commercial")
        self.assertFalse(context.agent_service.allow_inline_fallback)

    def test_inline_fallback_audits_poc_admin_execution(self) -> None:
        tmp_path = self.make_workspace()
        context = webui.WebContext(write_config(tmp_path))

        with patch("webui.run_veeam_diagnostics", return_value={"success": True}):
            context.execute_inline_agent_operation("veeam.diagnostics", {})

        audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event": "poc.admin_execution"', audit_text)

    def test_rbac_policy_has_required_roles_and_no_audit_delete_permission(self) -> None:
        policy = load_role_permissions(Path("config/rbac_policy.json"))

        self.assertEqual(set(policy), set(Role))
        self.assertEqual(
            [role.value for role in Role],
            [
                "SUPER_ADMIN",
                "SECURITY_ADMIN",
                "BACKUP_OPERATOR",
                "HARDWARE_ADMIN",
                "AUDITOR",
                "UI_DESIGNER",
                "DEVELOPER",
            ],
        )
        self.assertEqual(
            [permission.value for permission in Permission],
            [
                "DASHBOARD_VIEW",
                "USER_MANAGE",
                "ROLE_MANAGE",
                "VEEAM_VIEW",
                "VEEAM_MANAGE",
                "AIRGAP_POLICY_VIEW",
                "AIRGAP_POLICY_MANAGE",
                "DISK_OFFLINE_REQUEST",
                "DISK_OFFLINE_EXECUTE",
                "DISK_ONLINE_REQUEST",
                "DISK_ONLINE_APPROVE",
                "HARDWARE_CONTROL",
                "APPROVAL_REQUEST_VIEW",
                "APPROVAL_REQUEST_CREATE",
                "APPROVAL_REQUEST_APPROVE",
                "DEPARTMENT_REVIEW",
                "AUDIT_LOG_VIEW",
                "REPORT_EXPORT",
                "SYSTEM_SETTING_MANAGE",
            ],
        )
        self.assertNotIn("AUDIT_LOG_DELETE", {permission.value for permission in Permission})
        self.assertNotIn("AUDIT_LOG_DELETE", json.dumps(default_policy_document()))
        self.assertTrue(has_permission(Role.SUPER_ADMIN, Permission.AUDIT_LOG_VIEW, policy))
        self.assertFalse(has_permission(Role.SUPER_ADMIN, Permission("AUDIT_LOG_VIEW"), {Role.SUPER_ADMIN: set()}))
        self.assertTrue(all(has_permission(Role.SUPER_ADMIN, permission, policy) for permission in Permission))
        self.assertTrue(has_permission(Role.BACKUP_OPERATOR, Permission.APPROVAL_REQUEST_CREATE, policy))
        self.assertTrue(has_permission(Role.BACKUP_OPERATOR, Permission.APPROVAL_REQUEST_VIEW, policy))
        self.assertFalse(has_permission(Role.BACKUP_OPERATOR, Permission.APPROVAL_REQUEST_APPROVE, policy))
        self.assertTrue(has_permission(Role.AUDITOR, Permission.APPROVAL_REQUEST_VIEW, policy))
        self.assertFalse(has_permission(Role.AUDITOR, Permission.APPROVAL_REQUEST_CREATE, policy))
        self.assertFalse(has_permission(Role.AUDITOR, Permission.DEPARTMENT_REVIEW, policy))
        self.assertEqual(
            {role.value: sorted(permission.value for permission in permissions) for role, permissions in policy.items()},
            default_policy_document(),
        )

    def test_approval_api_guards_use_dedicated_rbac_permissions(self) -> None:
        source = (Path.cwd() / "webui.py").read_text(encoding="utf-8")

        self.assertIn("Permission.APPROVAL_REQUEST_VIEW", source)
        self.assertIn("Permission.APPROVAL_REQUEST_CREATE", source)
        self.assertIn("Permission.APPROVAL_REQUEST_APPROVE", source)
        self.assertIn("Permission.DEPARTMENT_REVIEW", source)

    def test_rbac_denies_missing_api_permission_with_forbidden_error(self) -> None:
        tmp_path = self.make_workspace()
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(write_config(tmp_path))
        handler.headers = {"Cookie": "lockfix_session=test-token"}
        handler.context.sessions["test-token"] = handler.session_record("auditor", Role.AUDITOR)

        with self.assertRaises(AuthorizationError) as raised:
            handler.require_auth(Permission.DISK_OFFLINE_EXECUTE)

        self.assertEqual(raised.exception.permission, Permission.DISK_OFFLINE_EXECUTE)
        self.assertEqual(raised.exception.role, Role.AUDITOR)

    def test_rbac_permission_denied_is_audited_for_api_guard(self) -> None:
        tmp_path = self.make_workspace()
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(write_config(tmp_path))
        handler.headers = {"Cookie": "lockfix_session=test-token", "User-Agent": "unit-test"}
        handler.path = "/api/isolate?slot=BAY-01"
        handler.client_address = ("127.0.0.1", 12345)
        handler.context.sessions["test-token"] = handler.session_record("auditor", Role.AUDITOR)

        try:
            handler.require_auth(Permission.DISK_OFFLINE_EXECUTE)
        except AuthorizationError as exc:
            handler.audit_access_denied(exc)

        audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event": "security.permission_denied"', audit_text)
        self.assertIn('"resourceType": "API"', audit_text)
        self.assertIn('"resourceId": "/api/isolate?slot=BAY-01"', audit_text)
        self.assertIn('"role": "AUDITOR"', audit_text)
        self.assertIn('"permission": "DISK_OFFLINE_EXECUTE"', audit_text)
        self.assertIn('"result": "FAILED"', audit_text)

    def test_webui_remote_console_attempt_is_blocked_and_audited(self) -> None:
        tmp_path = self.make_workspace()
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(write_config(tmp_path))
        handler.headers = {
            "Host": "192.168.219.230:8088",
            "User-Agent": "unit-test",
            "X-Forwarded-For": "127.0.0.1",
        }
        handler.path = "/"
        handler.command = "GET"
        handler.client_address = ("192.168.219.55", 54321)
        response = {}
        handler.send_json = lambda payload, status=200, headers=None: response.update({"payload": payload, "status": status})

        self.assertFalse(handler.enforce_local_console_access())

        self.assertEqual(response["status"], 403)
        self.assertIn("local-only", response["payload"]["error"])
        audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event": "security.remote_console_access.blocked"', audit_text)
        self.assertIn('"resourceType": "WEB_CONSOLE"', audit_text)
        self.assertIn('"resourceId": "/"', audit_text)
        self.assertIn('"ipAddress": "192.168.219.55"', audit_text)
        self.assertIn('"host_header": "192.168.219.230:8088"', audit_text)
        self.assertIn('"forwarded_for": "127.0.0.1"', audit_text)
        self.assertIn('"result": "BLOCKED"', audit_text)

    def test_webui_local_console_policy_uses_socket_peer_not_forwarded_header(self) -> None:
        self.assertTrue(webui.LockFixWebHandler.is_loopback_ip("127.0.0.1"))
        self.assertTrue(webui.LockFixWebHandler.is_loopback_ip("::1"))
        self.assertTrue(webui.LockFixWebHandler.is_loopback_ip("::ffff:127.0.0.1"))
        self.assertFalse(webui.LockFixWebHandler.is_loopback_ip("192.168.219.55"))

        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.headers = {"X-Forwarded-For": "127.0.0.1"}
        handler.client_address = ("192.168.219.55", 54321)

        self.assertFalse(handler.is_local_console_request())

    def test_rbac_allows_super_admin_existing_session_format(self) -> None:
        tmp_path = self.make_workspace()
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(write_config(tmp_path))
        handler.headers = {"Cookie": "lockfix_session=legacy-token"}
        handler.context.sessions["legacy-token"] = 9999999999.0

        handler.require_auth(Permission.DISK_OFFLINE_EXECUTE)

        self.assertEqual(handler.current_role(), Role.SUPER_ADMIN)

    def test_user_directory_seeds_default_departments(self) -> None:
        tmp_path = self.make_workspace()
        directory = UserDirectory(tmp_path / "users.json")

        departments = directory.departments()

        self.assertEqual(
            [department["name"] for department in departments],
            ["Management", "Security", "Backup Operation", "Hardware Control", "Audit", "Development", "Web Design"],
        )
        self.assertEqual({"id", "name", "description", "createdAt", "updatedAt"}, set(departments[0]))

    def test_lockfix_database_schema_matches_required_tables(self) -> None:
        expected = {
            "users": (
                "id",
                "email",
                "name",
                "password_hash",
                "department_id",
                "role",
                "disabled",
                "created_at",
                "updated_at",
            ),
            "departments": ("id", "name", "description", "created_at", "updated_at"),
            "role_permissions": ("id", "role", "permission"),
            "approval_requests": (
                "id",
                "request_type",
                "requested_by_user_id",
                "target_resource_type",
                "target_resource_id",
                "reason",
                "review_departments",
                "status",
                "created_at",
                "updated_at",
            ),
            "approval_policies": (
                "id",
                "request_type",
                "required_approvals",
                "allowed_approver_roles",
                "expires_in_minutes",
                "enabled",
            ),
            "department_reviews": (
                "id",
                "approval_request_id",
                "department_id",
                "reviewer_user_id",
                "status",
                "comment",
                "created_at",
                "updated_at",
            ),
            "review_comments": (
                "id",
                "approval_request_id",
                "department_review_id",
                "author_user_id",
                "comment",
                "created_at",
            ),
            "notifications": (
                "id",
                "user_id",
                "title",
                "message",
                "target_type",
                "target_id",
                "read_at",
                "created_at",
            ),
            "approval_decisions": ("id", "approval_request_id", "approver_user_id", "decision", "comment", "created_at"),
            "audit_logs": (
                "id",
                "actor_user_id",
                "action",
                "resource_type",
                "resource_id",
                "ip_address",
                "user_agent",
                "result",
                "before_value",
                "after_value",
                "created_at",
            ),
        }
        schema_sql = load_schema_sql()
        migration_sql = (Path.cwd() / "migrations" / "001_lockfix_rbac_approval_audit.sql").read_text(encoding="utf-8")

        self.assertEqual(expected, LOCKFIX_TABLE_SCHEMA)
        for table, fields in expected.items():
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", schema_sql)
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", migration_sql)
            for field in fields:
                self.assertIn(field, schema_sql)
                self.assertIn(field, migration_sql)
        self.assertNotIn("audit_log_delete", schema_sql.lower())
        self.assertNotIn("audit_log_delete", migration_sql.lower())

    def test_schema_row_mappers_preserve_snake_case_contract(self) -> None:
        policy = load_role_permissions(Path("config/rbac_policy.json"))
        user = users_row(
            {
                "id": "u1",
                "email": "backup@example.test",
                "name": "Backup Lead",
                "passwordHash": "hash",
                "departmentId": "backup-operation",
                "role": "BACKUP_OPERATOR",
                "disabled": False,
                "createdAt": "2026-05-11T00:00:00Z",
                "updatedAt": "2026-05-11T00:00:00Z",
            }
        )
        department = departments_row({"id": "backup-operation", "name": "Backup Operation", "createdAt": "c", "updatedAt": "u"})
        approval_policy = approval_policy_row(
            {
                "id": "disk-online",
                "requestType": "DISK_ONLINE",
                "requiredApprovals": 2,
                "allowedApproverRoles": ["SUPER_ADMIN"],
                "expiresInMinutes": 30,
                "enabled": True,
            }
        )
        approval_request = approval_request_row(
            {
                "id": "req1",
                "requestType": "DISK_ONLINE",
                "requesterUserId": "u1",
                "targetId": "BAY-01",
                "status": "PENDING",
                "createdAt": "c",
                "updatedAt": "u",
                "reviewDepartments": ["Security", "Hardware Control"],
                "metadata": {"targetResourceType": "DISK", "reason": "maintenance"},
            }
        )
        approval_decision = approval_decision_row(
            {"id": "dec1", "approvalRequestId": "req1", "approverUserId": "u2", "decision": "APPROVED", "createdAt": "c"}
        )
        department_review = department_review_row(
            {
                "id": "review1",
                "approvalRequestId": "req1",
                "departmentId": "security",
                "reviewerUserId": "security-reviewer",
                "status": "REVIEWED",
                "comment": "checked",
                "createdAt": "c",
                "updatedAt": "u",
            }
        )
        review_comment = review_comment_row(
            {
                "id": "comment1",
                "approvalRequestId": "req1",
                "departmentReviewId": "review1",
                "authorUserId": "security-reviewer",
                "comment": "checked",
                "createdAt": "c",
            }
        )
        notification = notification_row(
            {
                "id": "notice1",
                "userId": "department:security",
                "title": "Review required",
                "message": "Security review required",
                "targetType": "APPROVAL_REQUEST",
                "targetId": "req1",
                "readAt": "",
                "createdAt": "c",
            }
        )
        audit_log = audit_log_row(
            {
                "id": "log1",
                "actorUserId": "u1",
                "action": "admin.user.created",
                "resourceType": "USER",
                "resourceId": "u1",
                "ipAddress": "127.0.0.1",
                "userAgent": "unit-test",
                "result": "SUCCESS",
                "beforeValue": {},
                "afterValue": {"id": "u1"},
                "createdAt": "c",
            }
        )

        self.assertEqual(set(LOCKFIX_TABLE_SCHEMA["users"]), set(user))
        self.assertEqual("backup-operation", user["department_id"])
        self.assertEqual(set(LOCKFIX_TABLE_SCHEMA["departments"]), set(department))
        self.assertTrue(role_permissions_rows(policy))
        self.assertEqual("DISK_ONLINE", approval_policy["request_type"])
        self.assertEqual("u1", approval_request["requested_by_user_id"])
        self.assertEqual("DISK", approval_request["target_resource_type"])
        self.assertIn("Security", approval_request["review_departments"])
        self.assertEqual("security", department_review["department_id"])
        self.assertEqual("review1", review_comment["department_review_id"])
        self.assertEqual("department:security", notification["user_id"])
        self.assertEqual("APPROVAL_REQUEST", notification["target_type"])
        self.assertEqual("u2", approval_decision["approver_user_id"])
        self.assertEqual("127.0.0.1", audit_log["ip_address"])

    def test_super_admin_can_create_update_and_disable_users_with_audit_log(self) -> None:
        tmp_path = self.make_workspace()
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(write_config(tmp_path))
        handler.context.user_directory_path = tmp_path / "users.json"
        handler.headers = {"Cookie": "lockfix_session=admin-token"}
        handler.context.sessions["admin-token"] = handler.session_record("admin", Role.SUPER_ADMIN)

        created = handler.admin_create_user(
            {
                "email": "backup@example.com",
                "name": "Backup Operator",
                "departmentId": "backup-operation",
                "role": "BACKUP_OPERATOR",
            }
        )["user"]
        updated = handler.admin_update_user(
            created["id"],
            {"name": "Backup Lead", "departmentId": "security", "role": "SECURITY_ADMIN"},
        )["user"]
        disabled = handler.admin_disable_user(created["id"])["user"]

        self.assertEqual(created["departmentId"], "backup-operation")
        self.assertEqual(updated["role"], "SECURITY_ADMIN")
        self.assertTrue(disabled["disabled"])
        audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event": "admin.user.created"', audit_text)
        self.assertIn('"event": "admin.user.updated"', audit_text)
        self.assertIn('"event": "admin.user.disabled"', audit_text)

    def test_managed_user_temporary_password_login_uses_assigned_role(self) -> None:
        tmp_path = self.make_workspace()
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(write_config(tmp_path))
        handler.context.user_directory_path = tmp_path / "users.json"
        handler.headers = {"Cookie": "lockfix_session=admin-token"}
        handler.context.sessions["admin-token"] = handler.session_record("admin", Role.SUPER_ADMIN)

        created = handler.admin_create_user(
            {
                "email": "backup-login@example.com",
                "name": "Backup Login",
                "departmentId": "backup-operation",
                "role": "BACKUP_OPERATOR",
            }
        )
        temporary_password = created["temporaryPassword"]

        authenticated = handler.authenticate_managed_user("backup-login@example.com", temporary_password, "127.0.0.1")
        self.assertTrue(authenticated["ok"])
        self.assertEqual(authenticated["user"]["role"], "BACKUP_OPERATOR")
        self.assertTrue(authenticated["passwordChangeRequired"])
        self.assertNotIn("passwordHash", created["user"])

        reused = handler.authenticate_managed_user("backup-login@example.com", temporary_password, "127.0.0.1")
        self.assertEqual(reused["reason"], "temporary_password_used")

        handler.headers = {"Cookie": "lockfix_session=user-token"}
        handler.context.sessions["user-token"] = handler.session_record(
            "backup-login@example.com",
            Role.BACKUP_OPERATOR,
            user_id=created["user"]["id"],
            department_id="backup-operation",
            password_change_required=True,
        )
        changed = handler.change_current_account_password({"newPassword": "StrongPass1"})
        self.assertFalse(changed["user"]["passwordChangeRequired"])
        self.assertTrue(handler.authenticate_managed_user("backup-login@example.com", "StrongPass1", "127.0.0.1")["ok"])

    def test_emergency_reconnect_reauth_verifies_current_session_password(self) -> None:
        tmp_path = self.make_workspace()
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(write_config(tmp_path))
        handler.context.user_directory_path = tmp_path / "users.json"
        handler.headers = {"Cookie": "lockfix_session=admin-token"}
        handler.context.sessions["admin-token"] = handler.session_record("admin", Role.SUPER_ADMIN)

        self.assertTrue(handler.verify_current_session_password("1")["ok"])
        self.assertFalse(handler.verify_current_session_password("wrong")["ok"])

        created = handler.admin_create_user(
            {
                "email": "reauth@example.com",
                "name": "Reauth User",
                "departmentId": "security",
                "role": "SECURITY_ADMIN",
            }
        )
        temporary_password = created["temporaryPassword"]
        handler.authenticate_managed_user("reauth@example.com", temporary_password, "127.0.0.1")
        handler.headers = {"Cookie": "lockfix_session=user-token"}
        handler.context.sessions["user-token"] = handler.session_record(
            "reauth@example.com",
            Role.SECURITY_ADMIN,
            user_id=created["user"]["id"],
            department_id="security",
            password_change_required=True,
        )
        handler.change_current_account_password({"newPassword": "StrongPass1"})

        self.assertTrue(handler.verify_current_session_password("StrongPass1")["ok"])
        self.assertEqual(handler.verify_current_session_password("bad")["reason"], "password_mismatch")

    def test_emergency_reconnect_approval_request_endpoint_is_removed(self) -> None:
        source = (Path.cwd() / "webui.py").read_text(encoding="utf-8")
        app_source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertNotIn("/api/emergency-reconnect/approval-requests", source)
        self.assertNotIn("/api/emergency-reconnect/approval-requests", app_source)
        self.assertNotIn("재접속 승인이 필요합니다", app_source)
        self.assertNotIn("승인 요청 생성", app_source)

    def test_admin_archive_user_soft_deletes_and_redacts_sensitive_fields(self) -> None:
        tmp_path = self.make_workspace()
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(write_config(tmp_path))
        handler.context.user_directory_path = tmp_path / "users.json"
        handler.headers = {"Cookie": "lockfix_session=admin-token"}
        handler.context.sessions["admin-token"] = handler.session_record("admin", Role.SUPER_ADMIN)

        created = handler.admin_create_user(
            {
                "email": "delete-me@example.com",
                "name": "Delete Me",
                "departmentId": "audit",
                "role": "AUDITOR",
            }
        )
        temporary_password = created["temporaryPassword"]
        archived = handler.admin_archive_user(created["user"]["id"])["user"]

        self.assertTrue(archived["deleted"])
        self.assertTrue(archived["disabled"])
        self.assertEqual(handler.admin_users(), [])
        audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event": "admin.user.archived"', audit_text)
        self.assertNotIn(temporary_password, audit_text)
        self.assertNotIn("passwordHash", json.dumps(created["user"]))

    def test_windows_admin_status_is_status_only_and_audited(self) -> None:
        tmp_path = self.make_workspace()
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(write_config(tmp_path))
        handler.headers = {"Cookie": "lockfix_session=admin-token"}
        handler.context.sessions["admin-token"] = handler.session_record("admin", Role.SUPER_ADMIN)

        status = handler.windows_admin_status()

        self.assertEqual(status["mode"], "status_only")
        self.assertIn("isAdministrator", status)
        audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn('"event": "admin.windows_admin_status.checked"', audit_text)

    def test_non_super_admin_cannot_manage_users(self) -> None:
        tmp_path = self.make_workspace()
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(write_config(tmp_path))
        handler.headers = {"Cookie": "lockfix_session=security-token"}
        handler.context.sessions["security-token"] = handler.session_record("security-admin", Role.SECURITY_ADMIN)

        with self.assertRaises(AuthorizationError):
            handler.require_super_admin()

    def test_monitoring_chart_uses_compact_height(self) -> None:
        root = Path.cwd()
        html = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="monitoringChart" viewBox="0 0 920 250"', html)
        self.assertIn('class="date-range monitoring-date-range"', html)
        self.assertIn("const height = 250;", app)
        self.assertIn("const pad = { left: 96, right: 22, top: 8, bottom: 34 };", app)
        self.assertIn("min-height: 210px;", css)
        self.assertIn(".monitoring-date-range {", css)
        self.assertIn("grid-template-columns: minmax(138px, auto) minmax(138px, auto) auto 38px;", css)
        self.assertIn(".monitoring-date-range label {", css)
        self.assertIn("grid-template-columns: auto minmax(92px, auto);", css)
        self.assertIn('.monitoring-date-range input[type="date"]::-webkit-calendar-picker-indicator', css)
        self.assertIn("width: 18px;", css)
        self.assertIn("height: 18px;", css)

    def test_report_signature_pad_is_compact_without_guide_line(self) -> None:
        root = Path.cwd()
        html = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        css = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="engineerSignaturePad" class="signature-pad" width="560" height="120"', html)
        self.assertIn('id="managerSignaturePad" class="signature-pad" width="560" height="120"', html)
        self.assertIn("height: 104px;", css)
        self.assertIn("background: #ffffff;", css)
        self.assertNotIn("linear-gradient(transparent calc(100% - 34px)", css)

    def test_report_signature_attach_opens_draw_modal(self) -> None:
        root = Path.cwd()
        html = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('data-signature-open="engineerSignaturePad"', html)
        self.assertIn('data-signature-open="managerSignaturePad"', html)
        self.assertNotIn('data-signature-upload="engineerSignaturePad"', html)
        self.assertIn('id="signatureDrawModal"', html)
        self.assertIn('id="signatureDrawPad" class="signature-draw-pad" width="760" height="220"', html)
        self.assertIn('id="signatureDrawUpload"', html)
        self.assertIn("function openSignatureDrawModal", app)
        self.assertIn("function setupSignatureDrawModal", app)
        self.assertIn("drawImage(signatureDrawPad, 0, 0, activeSignatureCanvas.width, activeSignatureCanvas.height)", app)
        self.assertIn('"report.signatureUpload": "업로드"', app)
        self.assertIn(".signature-draw-pad", css)

    def test_report_export_buttons_use_file_icons_and_pdf(self) -> None:
        root = Path.cwd()
        html = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")
        webui_source = (root / "webui.py").read_text(encoding="utf-8")

        report_header = html.split('class="report-export-actions"', 1)[1].split("</div>", 1)[0]
        self.assertIn('href="/api/report.xlsx"', report_header)
        self.assertIn('class="file-icon file-csv"', report_header)
        self.assertIn('href="/api/report.pdf"', report_header)
        self.assertIn('class="file-icon file-pdf"', report_header)
        self.assertIn('href="/api/report.docx"', report_header)
        self.assertIn('class="file-icon file-word"', report_header)
        self.assertNotIn('href="/api/report.csv"', report_header)
        self.assertIn('data-i18n="report.exportExcel"', report_header)
        self.assertIn('"report.exportPdf": "PDF"', app)
        self.assertIn('background-image: url("/static/excel-export-logo.png");', css)
        self.assertIn('background-image: url("/static/pdf-export-logo.png");', css)
        self.assertIn('background-image: url("/static/word-export-logo.png");', css)
        self.assertIn('elif parsed.path == "/api/report.pdf":', webui_source)
        self.assertIn("def send_report_pdf", webui_source)
        self.assertIn("application/pdf", webui_source)
        self.assertIn("LOCK-FIX System Inspection Report", webui_source)
        self.assertIn("Resource Summary", webui_source)
        self.assertIn("Server Inspection Checklist", webui_source)
        self.assertIn("xl/styles.xml", webui_source)
        self.assertIn("pane ySplit", webui_source)
        self.assertIn("cellXfs", webui_source)
        self.assertNotIn('"LOCK-FIX Report"', webui_source)
        self.assertIn("20260520-sidebar-account-actions", html)

    def test_qr_login_button_has_visible_icon_treatment(self) -> None:
        root = Path.cwd()
        html = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        css = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('class="qr-submit"', html)
        self.assertIn(".qr-submit::before", css)
        self.assertIn("uploaded QR2 image mark", css)
        self.assertIn("width: 32px;", css)
        self.assertIn('url("/static/qr-login-icon.png?v=20260520-qr2") center / contain no-repeat', css)
        self.assertIn("qr-login-icon.png", css)
        self.assertIn("filter: opacity(0.42)", css)
        self.assertIn("saturate(0.86)", css)
        self.assertIn(".qr-submit:hover::before", css)
        self.assertIn("filter: opacity(1)", css)
        self.assertIn("rgba(11, 121, 255, 0.2)", css)
        self.assertIn("background: #ffffff;", css)
        self.assertIn("color: #d6e8fb;", css)
        self.assertIn("font-size: 18px;", css)
        self.assertIn("font-weight: 600;", css)
        self.assertIn(".qr-submit:hover,", css)
        self.assertIn("20260520-qr2-image-logo", html)
        self.assertTrue((root / "web" / "static" / "qr-login-icon.png").exists())

    def test_sidebar_user_menu_has_logout_and_account_switch(self) -> None:
        root = Path.cwd()
        html = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="sidebarAccountSwitchButton"', html)
        self.assertIn('id="sidebarUserLogoutButton"', html)
        self.assertIn('data-i18n="userMenu.switchAccount"', html)
        self.assertIn('data-i18n="userMenu.logout"', html)
        self.assertIn('const sidebarAccountSwitchButton = document.querySelector("#sidebarAccountSwitchButton");', app)
        self.assertIn("async function switchAccount()", app)
        self.assertIn("await logout();", app)
        self.assertIn('"/api/logout"', app)
        self.assertIn('"userMenu.switchAccount": "계정 전환"', app)
        self.assertIn('"userMenu.logout": "로그아웃"', app)
        self.assertIn(".sidebar-user-actions", css)
        self.assertIn(".sidebar-user-logout", css)

    def test_report_inspection_result_badges_are_centered(self) -> None:
        root = Path.cwd()
        html = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        css = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")
        checklist_panel = html.split('data-i18n="report.checklist"', 1)[1].split('id="reportInspectionTable"', 1)[0]
        usage_panel = html.split('data-i18n="report.usageDetails"', 1)[1].split('id="reportTable"', 1)[0]

        self.assertLess(html.index('class="report-table-panel report-inspection-panel"'), html.index('data-i18n="report.checklist"'))
        self.assertIn('class="report-table report-inspection-table"', checklist_panel)
        self.assertNotIn("report-inspection-panel", usage_panel)
        self.assertNotIn("report-inspection-table", usage_panel)
        self.assertIn(".report-table td:last-child {\n  text-align: left;", css)
        self.assertIn(".report-inspection-panel .report-table-wrap {", css)
        self.assertIn("padding: 0 12px 14px;", css)
        self.assertIn(".report-inspection-table th:first-child,", css)
        self.assertIn(".report-inspection-table th:last-child,", css)
        self.assertIn("width: 130px;", css)
        self.assertIn("text-align: center;", css)
        self.assertIn(".report-inspection-table .report-result-badge {", css)
        self.assertIn("margin-left: auto;", css)
        self.assertIn("margin-right: auto;", css)

    def test_user_management_ui_has_i18n_actions_and_cache_bust(self) -> None:
        root = Path.cwd()
        html = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        for token in [
            'data-i18n="userManagement.title"',
            'id="userManagementForm"',
            'id="userManagementBackButton"',
            'data-i18n="userManagement.actions"',
            'v=20260520-sidebar-account-actions',
            'class="rbac-chip-list user-management-department-list"',
            'data-i18n="department.backupOperation"',
            '<option value="SECURITY_ADMIN">SECURITY_ADMIN</option>',
            'data-i18n="department.hardwareControl"',
        ]:
            self.assertIn(token, html)
        for token in [
            '"/api/admin/windows-admin-status"',
            '"/api/account/password"',
            '"/api/admin/users"',
            '"/api/admin/departments"',
            "Promise.allSettled",
            "USER_MANAGEMENT_DEFAULT_DEPARTMENTS",
            'data-user-archive',
            '"userManagement.title": "사용자/권한 관리"',
            '"userManagement.title": "User & Role Management"',
            '"userManagement.windowsUnavailable": "상태 확인 지연"',
            '"userManagement.errorDuplicateEmail": "이미 등록된 이메일입니다.',
            '"userManagement.createdAfterTimeout": "{email} 사용자는 등록되었지만',
            "function userManagementErrorMessage",
            "function hasUserManagementDuplicateEmail",
            "setUserManagementStatus(t(\"userManagement.errorDuplicateEmail\"), \"error\")",
            'timeoutMs: 60000',
            'error?.code === "REQUEST_TIMEOUT"',
        ]:
            self.assertIn(token, app)
        for token in [
            ".user-management-department-list",
            "align-items: flex-start;",
            "align-content: flex-start;",
            "white-space: nowrap;",
            ".user-management-windows-status .status-neutral",
        ]:
            self.assertIn(token, css)

    def test_audit_log_model_normalizes_existing_jsonl_records(self) -> None:
        tmp_path = self.make_workspace()
        audit_path = tmp_path / "audit.jsonl"
        AuditLogger(audit_path).write(
            "auth.login.success",
            actorUserId="admin",
            ipAddress="127.0.0.1",
            userAgent="unit-test",
            result="SUCCESS",
        )

        logs = read_audit_logs(audit_path)

        self.assertEqual(set(AUDIT_LOG_FIELDS), set(logs[0]) - {"raw"})
        self.assertEqual(logs[0]["actorUserId"], "admin")
        self.assertEqual(logs[0]["action"], "auth.login.success")
        self.assertEqual(logs[0]["resourceType"], "AUTH")
        self.assertEqual(logs[0]["result"], "SUCCESS")

    def test_audit_log_reader_tails_large_files_without_full_scan(self) -> None:
        tmp_path = self.make_workspace()
        audit_path = tmp_path / "audit.jsonl"
        rows = [
            json.dumps({"event": "old.event", "actorUserId": "old"}, ensure_ascii=False),
            *[
                json.dumps({"event": f"recent.event.{index}", "actorUserId": f"user-{index}"}, ensure_ascii=False)
                for index in range(5)
            ],
        ]
        audit_path.write_text("\n".join(rows) + "\n", encoding="utf-8")

        tail = tail_text_lines(audit_path, limit=3, chunk_size=32)
        logs = read_audit_logs(audit_path, limit=3)

        self.assertEqual(len(tail), 3)
        self.assertIn("recent.event.4", tail[-1])
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[0]["action"], "recent.event.4")
        self.assertEqual(logs[-1]["action"], "recent.event.2")

    def test_audit_log_view_is_limited_to_auditor_security_and_super_admin(self) -> None:
        tmp_path = self.make_workspace()
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(write_config(tmp_path))
        handler.headers = {"Cookie": "lockfix_session=auditor-token", "User-Agent": "unit-test"}
        handler.path = "/api/audit-logs"
        handler.client_address = ("127.0.0.1", 12345)
        handler.context.sessions["auditor-token"] = handler.session_record("auditor", Role.AUDITOR)

        handler.require_audit_log_view()

        handler.context.sessions["auditor-token"] = handler.session_record("developer", Role.DEVELOPER)
        with self.assertRaises(AuthorizationError):
            handler.require_audit_log_view()

    def test_audit_log_export_is_csv_and_no_delete_api_is_defined(self) -> None:
        tmp_path = self.make_workspace()
        audit_path = tmp_path / "audit.jsonl"
        AuditLogger(audit_path).write("admin.user.disabled", actorUserId="admin", resourceId="user-1")
        logs = read_audit_logs(audit_path)
        csv_body = audit_logs_to_csv(logs).decode("utf-8-sig")
        webui_source = Path("webui.py").read_text(encoding="utf-8")

        self.assertIn("actorUserId,action,resourceType", csv_body)
        self.assertIn("admin.user.disabled", csv_body)
        self.assertNotIn("def do_DELETE", webui_source)

    def test_approval_policy_defaults_and_two_person_approval(self) -> None:
        tmp_path = self.make_workspace()
        audit = AuditLogger(tmp_path / "audit.jsonl")
        store = ApprovalStore(tmp_path / "approvals.json", audit)

        policy = store.policy_for("DISK_ONLINE")
        request = store.create_repository_online_request("creator", target_id="BAY-01", reason="Repository Online requested")
        store.review_request(request["id"], "security-reviewer", Role.SECURITY_ADMIN, "SECURITY_LOG_REVIEW", "isolation period logs checked")
        store.review_request(request["id"], "hardware-reviewer", Role.HARDWARE_ADMIN, "HARDWARE_STATE_REVIEW", "JBOD lock state checked")
        store.review_request(request["id"], "manager-reviewer", Role.SUPER_ADMIN, "MANAGER_REVIEW", "team opinions confirmed")
        first = store.decide(request["id"], "approver-a", Role.SECURITY_ADMIN, "APPROVED")
        second = store.decide(request["id"], "approver-b", Role.SUPER_ADMIN, "APPROVED")

        self.assertEqual(policy["requiredApprovals"], 2)
        self.assertEqual(first["request"]["status"], "PENDING")
        self.assertEqual(second["request"]["status"], "APPROVED")
        self.assertIsNotNone(store.approved_request_for("DISK_ONLINE", "BAY-01"))

    def test_repository_online_workflow_requires_team_reviews_and_ordered_approval(self) -> None:
        tmp_path = self.make_workspace()
        store = ApprovalStore(tmp_path / "approvals.json", AuditLogger(tmp_path / "audit.jsonl"))
        request = store.create_repository_online_request("backup-operator", "BAY-01", "restore repository access")

        with self.assertRaisesRegex(PermissionError, "review required"):
            store.decide(request["id"], "security-admin", Role.SECURITY_ADMIN, "APPROVED")

        store.review_request(request["id"], "security-reviewer", Role.SECURITY_ADMIN, "SECURITY_LOG_REVIEW", "격리 기간 로그 정상")
        store.review_request(request["id"], "hardware-reviewer", Role.HARDWARE_ADMIN, "HARDWARE_STATE_REVIEW", "디스크/JBOD/락 정상")
        reviewed = store.review_request(request["id"], "manager", Role.SUPER_ADMIN, "MANAGER_REVIEW", "두 팀 의견 확인")

        self.assertEqual(reviewed["request"]["metadata"]["workflowStatus"], "AWAITING_SECURITY_ADMIN_APPROVAL")
        with self.assertRaisesRegex(PermissionError, "SECURITY_ADMIN"):
            store.decide(request["id"], "super-admin", Role.SUPER_ADMIN, "APPROVED")

        first = store.decide(request["id"], "security-admin", Role.SECURITY_ADMIN, "APPROVED")
        self.assertEqual(first["request"]["metadata"]["workflowStatus"], "AWAITING_SUPER_ADMIN_APPROVAL")
        second = store.decide(request["id"], "super-admin", Role.SUPER_ADMIN, "APPROVED")

        self.assertEqual(second["request"]["status"], "APPROVED")
        self.assertEqual(second["request"]["metadata"]["workflowStatus"], "APPROVED_READY_TO_EXECUTE")
        audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn("approval.notification.sent", audit_text)
        self.assertIn("approval.review.created", audit_text)

    def test_department_reviews_are_assigned_and_gate_final_approval(self) -> None:
        tmp_path = self.make_workspace()
        store = ApprovalStore(tmp_path / "approvals.json", AuditLogger(tmp_path / "audit.jsonl"))
        request = store.create_request("POLICY_CHANGE", requester_user_id="developer", target_id="rbac-policy")
        reviews = store.department_reviews_for(request["id"])

        self.assertEqual(["Security", "Audit"], request["reviewDepartments"])
        self.assertEqual({"security", "audit"}, {review["departmentId"] for review in reviews})
        with self.assertRaisesRegex(PermissionError, "department review required"):
            store.decide(request["id"], "security-admin", Role.SECURITY_ADMIN, "APPROVED")

        security_review = next(review for review in reviews if review["departmentId"] == "security")
        audit_review = next(review for review in reviews if review["departmentId"] == "audit")
        store.comment_department_review(request["id"], security_review["id"], "security-admin", Role.SECURITY_ADMIN, "logs look clean")
        store.mark_department_reviewed(request["id"], security_review["id"], "security-admin", Role.SECURITY_ADMIN, "security reviewed")
        store.mark_department_reviewed(request["id"], audit_review["id"], "auditor", Role.AUDITOR, "audit reviewed")
        data = store.load()
        self.assertEqual(3, len(data["reviewComments"]))
        self.assertTrue(data["notifications"])
        self.assertEqual("APPROVAL_REQUEST", data["notifications"][0]["targetType"])
        self.assertEqual(f"department:{data['notifications'][0]['departmentId']}", data["notifications"][0]["userId"])
        first = store.decide(request["id"], "security-approver", Role.SECURITY_ADMIN, "APPROVED")

        self.assertEqual(first["request"]["status"], "PENDING")
        audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
        self.assertIn("department.review.assigned", audit_text)
        self.assertIn("department.review.comment.created", audit_text)
        self.assertIn("department.review.marked_reviewed", audit_text)

    def test_department_review_needs_changes_and_blocked_rules(self) -> None:
        tmp_path = self.make_workspace()
        store = ApprovalStore(tmp_path / "approvals.json", AuditLogger(tmp_path / "audit.jsonl"))
        request = store.create_request("DISK_OFFLINE", requester_user_id="backup-operator", target_id="BAY-01")
        reviews = store.department_reviews_for(request["id"])
        backup_review = next(review for review in reviews if review["departmentId"] == "backup-operation")
        security_review = next(review for review in reviews if review["departmentId"] == "security")

        store.mark_department_needs_changes(request["id"], backup_review["id"], "backup-reviewer", Role.BACKUP_OPERATOR, "add isolation evidence")
        with self.assertRaisesRegex(PermissionError, "needs changes"):
            store.decide(request["id"], "security-admin", Role.SECURITY_ADMIN, "APPROVED")

        store.block_department_review(request["id"], security_review["id"], "security-admin", Role.SECURITY_ADMIN, "security incident open")
        with self.assertRaisesRegex(PermissionError, "Super Admin"):
            store.mark_department_reviewed(request["id"], security_review["id"], "security-admin", Role.SECURITY_ADMIN, "try to override")
        override = store.mark_department_reviewed(request["id"], security_review["id"], "super-admin", Role.SUPER_ADMIN, "exception review started")

        self.assertEqual(override["review"]["status"], "REVIEWED")

    def test_approval_blocks_duplicate_and_creator_self_approval(self) -> None:
        tmp_path = self.make_workspace()
        store = ApprovalStore(tmp_path / "approvals.json", AuditLogger(tmp_path / "audit.jsonl"))
        request = store.create_request("POLICY_CHANGE", requester_user_id="creator", target_id="policy")

        with self.assertRaisesRegex(PermissionError, "creator cannot approve"):
            store.decide(request["id"], "creator", Role.SECURITY_ADMIN, "APPROVED")
        with self.assertRaisesRegex(PermissionError, "creator cannot approve"):
            store.decide(request["id"], "Creator", Role.SECURITY_ADMIN, "APPROVED")

        self.complete_department_reviews(store, request)
        store.decide(request["id"], "approver-a", Role.SECURITY_ADMIN, "APPROVED")
        with self.assertRaisesRegex(PermissionError, "duplicate"):
            store.decide(request["id"], "approver-a", Role.SECURITY_ADMIN, "APPROVED")
        with self.assertRaisesRegex(PermissionError, "duplicate"):
            store.decide(request["id"], "APPROVER-A", Role.SECURITY_ADMIN, "APPROVED")

    def test_emergency_unlock_approval_requires_reason_and_two_approvers(self) -> None:
        tmp_path = self.make_workspace()
        store = ApprovalStore(tmp_path / "approvals.json", AuditLogger(tmp_path / "audit.jsonl"))

        with self.assertRaisesRegex(ValueError, "reason is required"):
            store.create_request("EMERGENCY_UNLOCK", requester_user_id="creator", target_id="BAY-01")

        request = store.create_request(
            "EMERGENCY_UNLOCK",
            requester_user_id="creator",
            target_id="BAY-01",
            metadata={"reason": "recover locked backup volume"},
        )
        self.complete_department_reviews(store, request)
        first = store.decide(request["id"], "approver-a", Role.SUPER_ADMIN, "APPROVED")
        second = store.decide(request["id"], "approver-b", Role.SECURITY_ADMIN, "APPROVED")

        self.assertEqual(request["requiredApprovals"], 2)
        self.assertEqual(first["request"]["status"], "PENDING")
        self.assertEqual(second["request"]["status"], "APPROVED")
        self.assertIn("recover locked backup volume", json.dumps(second["request"], ensure_ascii=False))

    def test_approval_expiration_updates_status_and_audit_log(self) -> None:
        tmp_path = self.make_workspace()
        store = ApprovalStore(tmp_path / "approvals.json", AuditLogger(tmp_path / "audit.jsonl"))
        request = store.create_request("HARDWARE_POWER_ON", requester_user_id="creator", target_id="BAY-01")
        data = store.load()
        data["requests"][0]["expiresAt"] = "2000-01-01T00:00:00+00:00"
        store.save(data)

        expired = store.expire_pending_requests()

        self.assertEqual(expired[0]["id"], request["id"])
        self.assertEqual(expired[0]["status"], "EXPIRED")
        self.assertIn("approval.request.expired", (tmp_path / "audit.jsonl").read_text(encoding="utf-8"))

    def test_controller_blocks_disk_online_until_approval_is_complete(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))

        with self.assertRaisesRegex(PermissionError, "approval required"):
            controller.reconnect("BAY-01")

        self.approve_operation(controller, "DISK_ONLINE")
        state = controller.reconnect("BAY-01")

        self.assertIn(state, {LockFixState.ONLINE_VERIFIED_RW, LockFixState.QUARANTINE})

    def test_controller_blocks_policy_and_hardware_power_until_approval_is_complete(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))

        with self.assertRaisesRegex(PermissionError, "approval required"):
            controller.require_policy_change_approval("rbac-policy")
        with self.assertRaisesRegex(PermissionError, "approval required"):
            controller.hardware_power_on("BAY-01")
        with self.assertRaisesRegex(PermissionError, "approval required"):
            controller.hardware_power_off("BAY-01")

        self.approve_operation(controller, "POLICY_CHANGE", "rbac-policy")
        self.approve_operation(controller, "HARDWARE_POWER_ON")
        self.approve_operation(controller, "HARDWARE_POWER_OFF")

        self.assertEqual(controller.require_policy_change_approval("rbac-policy")["status"], "APPROVED")
        controller.hardware_power_on("BAY-01")
        controller.hardware_power_off("BAY-01")

    def test_offline_reconnect_validation_writes_report_and_checks_agent_portability(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)

        summary = run_offline_reconnect_validation(config_path, report_dir=tmp_path / "reports", json_log_dir=tmp_path / "runtime")

        self.assertIn(summary["overall_status"], {"OK", "ISSUE_DETECTED"})
        self.assertTrue(Path(summary["html_report_path"]).exists())
        self.assertTrue(Path(summary["json_log_path"]).exists())
        finding_ids = {item["id"] for item in summary["findings"]}
        self.assertIn("offline.proof", finding_ids)
        self.assertIn("emergency.approval.gate", finding_ids)
        self.assertIn("reconnect.blocked.until.approved", finding_ids)
        self.assertIn("agent.os.backend", finding_ids)
        self.assertIn("offline.reconnect.validation.completed", (tmp_path / "audit.jsonl").read_text(encoding="utf-8"))

    def test_webui_permission_errors_return_403_and_emergency_uses_password_reauth(self) -> None:
        source = Path("webui.py").read_text(encoding="utf-8")
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)

        self.assertEqual(handler.permission_error_status(PermissionError("approval required: DISK_ONLINE")), 403)
        self.assertEqual(handler.permission_error_status(PermissionError("authentication required")), 401)
        self.assertIn("verify_current_session_password", source)
        self.assertIn("emergency.reconnect.password_approval_bypass", source)
        self.assertIn('approval_bypass_reason = "password_reauth"', source)
        self.assertNotIn('self.context.controller.approvals.require_approved("EMERGENCY_UNLOCK", slot_id)', source)
        self.assertNotIn('self.context.controller.approvals.require_approved("DISK_ONLINE", slot_id)', source)
        self.assertNotIn("reason=\"admin_emergency_reconnect_requested\"", source)

    def test_install_properties_can_enable_live_operation_mode(self) -> None:
        tmp_path = self.make_workspace()
        source_config = write_config(tmp_path)
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_path = config_dir / "lockfix.example.json"
        config_path.write_text(source_config.read_text(encoding="utf-8"), encoding="utf-8")
        runtime_dir = tmp_path / "runtime"
        runtime_dir.mkdir()
        (runtime_dir / "install.properties").write_text(
            "operation_mode=live\n"
            "dry_run=false\n",
            encoding="utf-8",
        )

        config = load_config(config_path)

        self.assertFalse(config.dry_run)

    def test_install_properties_override_stale_veeam_endpoint_in_loaded_config(self) -> None:
        tmp_path = self.make_workspace()
        source_config = write_config(tmp_path)
        install_root = tmp_path / "install"
        config_dir = install_root / "config"
        runtime_dir = install_root / "runtime"
        config_dir.mkdir(parents=True)
        runtime_dir.mkdir()
        config_path = config_dir / "lockfix.example.json"
        raw = json.loads(source_config.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "base_url": "https://192.168.219.165:9419",
            "discovery_candidates": ["https://192.168.219.165:9419"],
            "username": "old-user",
            "api_version": "1.2-rev1",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        (runtime_dir / "install.properties").write_text(
            "veeam_host=192.168.219.230\n"
            "veeam_port=9419\n"
            "veeam_base_url=https://192.168.219.230:9419\n"
            "veeam_api_version=1.2-rev1\n"
            "veeam_user=administrator\n",
            encoding="utf-8",
        )

        config = load_config(config_path)

        self.assertEqual(config.veeam.base_url, "https://192.168.219.230:9419")
        self.assertEqual(config.veeam.discovery_candidates[0], "https://192.168.219.230:9419")
        self.assertEqual(config.veeam.username, "administrator")

    def test_power_command_paths_are_resolved_from_install_root(self) -> None:
        tmp_path = self.make_workspace()
        source_config = write_config(tmp_path)
        install_root = tmp_path / "install"
        config_dir = install_root / "config"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "lockfix.example.json"
        raw = json.loads(source_config.read_text(encoding="utf-8"))
        raw["slots"][0]["power"] = {
            "type": "command",
            "off_command": [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "{app_root}\\tools\\lockfix_power_control.ps1",
                "-Action",
                "Off",
                "-SlotId",
                "BAY-01",
            ],
            "on_command": [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "tools\\lockfix_power_control.ps1",
                "-Action",
                "On",
                "-SlotId",
                "BAY-01",
            ],
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)
        power = config.slot("BAY-01").power

        self.assertEqual(power.type, "command")
        self.assertIn(str(install_root / "tools" / "lockfix_power_control.ps1"), power.off_command)
        self.assertIn(str(install_root / "tools" / "lockfix_power_control.ps1"), power.on_command)

    def test_power_status_command_paths_are_resolved_from_install_root(self) -> None:
        tmp_path = self.make_workspace()
        source_config = write_config(tmp_path)
        install_root = tmp_path / "install"
        config_dir = install_root / "config"
        config_dir.mkdir(parents=True)
        config_path = config_dir / "lockfix.example.json"
        raw = json.loads(source_config.read_text(encoding="utf-8"))
        raw["slots"][0]["power"] = {
            "type": "command",
            "off_command": [],
            "on_command": [],
            "status_command": [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "tools\\lockfix_power_control.ps1",
                "-Action",
                "Status",
                "-SlotId",
                "BAY-01",
            ],
            "off_status_values": ["off", "powered_off"],
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)
        power = config.slot("BAY-01").power

        self.assertIn(str(install_root / "tools" / "lockfix_power_control.ps1"), power.status_command)
        self.assertEqual(power.off_status_values, ["off", "powered_off"])

    def test_isolation_proof_reports_volume_and_power_evidence(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))

        result = controller.isolation_proof("BAY-01")

        self.assertEqual(result["slot_id"], "BAY-01")
        self.assertEqual(result["status"], "NOT_PROVED")
        self.assertFalse(result["proved"])
        self.assertEqual(result["volume_unmounted"]["reason"], "dry_run mode cannot prove live Windows volume state")
        self.assertEqual(result["power_off"]["reason"], "mock power controller cannot prove physical power state")
        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn('"event": "disk.unmount.proof"', audit_text)
        self.assertIn('"event": "power.mock.status"', audit_text)
        self.assertIn('"event": "isolation.proof"', audit_text)

    def test_isolate_records_power_off_proof_requirement_when_status_is_unavailable(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))
        self.approve_operation(controller, "DISK_OFFLINE")

        controller.isolate("BAY-01")

        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn('"event": "power.mock.status"', audit_text)
        self.assertIn('"event": "power.off.proof.required"', audit_text)
        self.assertIn("Power OFF can be proved only when the PDU/relay/storage controller status response confirms OFF.", audit_text)

    def test_controller_uses_veeam_backup_copy_repository_volume(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "enabled": True,
            "require_backup_copy": True,
            "target_repository_path": "F:\\Repository\\Copy",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        controller = LockFixController(load_config(config_path))
        self.approve_operation(controller, "DISK_OFFLINE")

        controller.isolate("BAY-01")

        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn('"event": "veeam.repository.volume.target"', audit_text)
        self.assertIn('"repository_path": "F:\\\\Repository\\\\Copy"', audit_text)
        self.assertIn('"target_volume": "F:\\\\"', audit_text)
        self.assertIn('"configured_slot_volume":', audit_text)

    def test_controller_blocks_non_veeam_repository_volume_when_backup_copy_is_required(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "enabled": True,
            "require_backup_copy": True,
            "target_repository_path": "G:\\BackupCopy",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        controller = LockFixController(load_config(config_path))

        with self.assertRaisesRegex(ValueError, "Veeam Backup Copy repository volume"):
            controller.repository_slot(controller.config.slot("BAY-01"), "D:\\OldRepository")

        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn('"event": "veeam.repository.volume.mismatch"', audit_text)
        self.assertIn('"configured_volume": "G:\\\\"', audit_text)
        self.assertIn('"supplied_volume": "D:\\\\"', audit_text)

    def test_repository_volume_root_blocks_c_volume(self) -> None:
        self.assertEqual(repository_volume_root("F:\\Repository\\Copy"), "F:\\")
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "enabled": True,
            "require_backup_copy": True,
            "target_repository_path": "C:\\BackupCopy",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        controller = LockFixController(load_config(config_path))
        self.approve_operation(controller, "DISK_OFFLINE")

        with self.assertRaisesRegex(ValueError, "protected Windows OS volume"):
            controller.isolate("BAY-01")

    def test_agent_service_worker_executes_privileged_disk_operation_from_queue(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        controller = LockFixController(load_config(config_path))
        self.approve_operation(controller, "DISK_OFFLINE")

        queue_root = tmp_path / "agent_service"
        client = AgentServiceClient(queue_root, timeout_seconds=1)
        request_id = "request-disk-isolate"
        request_path = queue_root / "requests" / f"{request_id}.json"
        request_path.parent.mkdir(parents=True)
        request_path.write_text(
            json.dumps(
                {
                    "request_id": request_id,
                    "operation": "disk.isolate",
                    "payload": {"slot_id": "BAY-01"},
                }
            ),
            encoding="utf-8",
        )

        processed = AgentServiceWorker(config_path, queue_root).process_once()
        response = json.loads((queue_root / "responses" / f"{request_id}.json").read_text(encoding="utf-8"))

        self.assertEqual(processed, 1)
        self.assertTrue(response["ok"])
        self.assertEqual(response["state"], "ISOLATED")
        audit_text = load_config(config_path).audit_log_path.read_text(encoding="utf-8")
        self.assertIn('"event": "agent.service.request.received"', audit_text)

    def test_agent_service_worker_runs_prevalidated_emergency_reconnect_without_dual_approval(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        queue_root = tmp_path / "agent_service"
        request_id = "request-emergency-reconnect"
        request_path = queue_root / "requests" / f"{request_id}.json"
        request_path.parent.mkdir(parents=True)
        request_path.write_text(
            json.dumps(
                {
                    "request_id": request_id,
                    "operation": "emergency.reconnect",
                    "payload": {
                        "slot_id": "BAY-01",
                        "repository_path": "D:\\",
                        "job_id": "job-password-reauth",
                        "approval_bypass": True,
                        "approval_bypass_reason": "password_reauth",
                    },
                }
            ),
            encoding="utf-8",
        )

        processed = AgentServiceWorker(config_path, queue_root).process_once()
        response = json.loads((queue_root / "responses" / f"{request_id}.json").read_text(encoding="utf-8"))
        audit_text = load_config(config_path).audit_log_path.read_text(encoding="utf-8")

        self.assertEqual(processed, 1)
        self.assertTrue(response["ok"])
        self.assertEqual(response["state"], "ONLINE_VERIFIED_RW")
        self.assertIn('"event": "emergency.unlock.prevalidated"', audit_text)
        self.assertIn('"event": "disk.online.prevalidated"', audit_text)
        self.assertIn('"job_id": "job-password-reauth"', audit_text)

    def test_agent_service_worker_expires_stale_mutating_requests(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        queue_root = tmp_path / "agent_service"
        request_id = "request-stale-emergency"
        request_path = queue_root / "requests" / f"{request_id}.json"
        request_path.parent.mkdir(parents=True)
        stale_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 3600))
        request_path.write_text(
            json.dumps(
                {
                    "request_id": request_id,
                    "operation": "emergency.reconnect",
                    "payload": {"slot_id": "BAY-01", "repository_path": "D:\\", "job_id": "old-job"},
                    "created_at": stale_time,
                }
            ),
            encoding="utf-8",
        )

        processed = AgentServiceWorker(config_path, queue_root).process_once()
        response = json.loads((queue_root / "responses" / f"{request_id}.json").read_text(encoding="utf-8"))
        audit_text = load_config(config_path).audit_log_path.read_text(encoding="utf-8")

        self.assertEqual(processed, 1)
        self.assertFalse(response["ok"])
        self.assertIn("expired", response["error"])
        self.assertIn("agent.service.request.expired", audit_text)
        self.assertNotIn("emergency.unlock.request", audit_text)

    def test_agent_service_worker_expires_stale_diagnostics_requests(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        queue_root = tmp_path / "agent_service"
        request_id = "request-stale-diagnostics"
        request_path = queue_root / "requests" / f"{request_id}.json"
        request_path.parent.mkdir(parents=True)
        stale_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 3600))
        request_path.write_text(
            json.dumps(
                {
                    "request_id": request_id,
                    "operation": "veeam.diagnostics",
                    "payload": {"timeout_seconds": 8.0},
                    "created_at": stale_time,
                }
            ),
            encoding="utf-8",
        )

        processed = AgentServiceWorker(config_path, queue_root).process_once()
        response = json.loads((queue_root / "responses" / f"{request_id}.json").read_text(encoding="utf-8"))
        audit_text = load_config(config_path).audit_log_path.read_text(encoding="utf-8")

        self.assertEqual(processed, 1)
        self.assertFalse(response["ok"])
        self.assertIn("expired", response["error"])
        self.assertIn("agent.service.request.expired", audit_text)
        self.assertNotIn("agent.service.request.received", audit_text)

    def test_agent_service_client_removes_timed_out_requests(self) -> None:
        tmp_path = self.make_workspace()
        queue_root = tmp_path / "agent_service"
        client = AgentServiceClient(queue_root, timeout_seconds=0.05)

        with self.assertRaises(AgentServiceUnavailable):
            client.submit_and_wait("veeam.diagnostics", {"timeout_seconds": 8.0})

        self.assertEqual([], list((queue_root / "requests").glob("*.json")))

    def test_agent_service_worker_ignores_request_file_removed_after_response(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        queue_root = tmp_path / "agent_service"
        request_path = queue_root / "requests" / "raced-diagnostics.json"
        request_path.parent.mkdir(parents=True)
        request_path.write_text(
            json.dumps(
                {
                    "request_id": "raced-diagnostics",
                    "operation": "veeam.diagnostics",
                    "payload": {"timeout_seconds": 8.0},
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            ),
            encoding="utf-8",
        )
        worker = AgentServiceWorker(config_path, queue_root)

        def remove_request(_request: dict) -> dict:
            request_path.unlink()
            return {"ok": True, "request_id": "raced-diagnostics", "operation": "veeam.diagnostics"}

        with patch.object(worker, "execute_request", side_effect=remove_request):
            processed = worker.process_once(max_requests=1)

        self.assertEqual(processed, 1)
        self.assertTrue((queue_root / "responses" / "raced-diagnostics.json").exists())
        self.assertFalse((queue_root / "processed" / "raced-diagnostics.json").exists())

    def test_agent_service_worker_prunes_large_stale_diagnostics_backlog(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        queue_root = tmp_path / "agent_service"
        requests_dir = queue_root / "requests"
        requests_dir.mkdir(parents=True)
        stale_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 3600))
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        for index in range(105):
            request_id = f"old-diagnostics-{index}"
            (requests_dir / f"{request_id}.json").write_text(
                json.dumps(
                    {
                        "request_id": request_id,
                        "operation": "veeam.diagnostics",
                        "payload": {"timeout_seconds": 8.0},
                        "created_at": stale_time,
                    }
                ),
                encoding="utf-8",
            )
        fresh_path = requests_dir / "fresh-diagnostics.json"
        fresh_path.write_text(
            json.dumps(
                {
                    "request_id": "fresh-diagnostics",
                    "operation": "veeam.diagnostics",
                    "payload": {"timeout_seconds": 8.0},
                    "created_at": current_time,
                }
            ),
            encoding="utf-8",
        )

        with patch(
            "lockfix.agent_service.run_veeam_diagnostics",
            return_value={
                "success": True,
                "latest_configured_session": {
                    "name": "Agent_backup",
                    "repository_name": "D REPO",
                    "repository_path": "D:\\Backup",
                },
            },
        ):
            processed = AgentServiceWorker(config_path, queue_root).process_once(max_requests=1)

        response = json.loads((queue_root / "responses" / "fresh-diagnostics.json").read_text(encoding="utf-8"))
        audit_text = load_config(config_path).audit_log_path.read_text(encoding="utf-8")

        self.assertEqual(processed, 1)
        self.assertTrue(response["ok"])
        self.assertEqual(response["diagnostics"]["latest_configured_session"]["name"], "Agent_backup")
        self.assertEqual(len(list((queue_root / "expired").glob("*.json"))), 105)
        self.assertEqual([], list((queue_root / "requests").glob("*.json")))
        self.assertIn('"event": "agent.service.queue.pruned"', audit_text)

    def test_agent_service_worker_keeps_only_latest_pending_diagnostics(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        queue_root = tmp_path / "agent_service"
        requests_dir = queue_root / "requests"
        requests_dir.mkdir(parents=True)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        for index in range(3):
            request_id = f"diagnostics-{index}"
            request_path = requests_dir / f"{request_id}.json"
            request_path.write_text(
                json.dumps(
                    {
                        "request_id": request_id,
                        "operation": "veeam.diagnostics",
                        "payload": {"timeout_seconds": 8.0},
                        "created_at": current_time,
                    }
                ),
                encoding="utf-8",
            )
            os.utime(request_path, (time.time() + index, time.time() + index))

        with patch("lockfix.agent_service.run_veeam_diagnostics", return_value={"success": True}):
            processed = AgentServiceWorker(config_path, queue_root).process_once(max_requests=1)

        self.assertEqual(processed, 1)
        self.assertTrue((queue_root / "responses" / "diagnostics-2.json").exists())
        self.assertFalse((queue_root / "responses" / "diagnostics-0.json").exists())
        self.assertFalse((queue_root / "responses" / "diagnostics-1.json").exists())
        self.assertEqual(len(list((queue_root / "expired").glob("*.json"))), 2)
        self.assertEqual([], list((queue_root / "requests").glob("*.json")))

    def test_agent_service_worker_prioritizes_emergency_requests_with_backlog(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        queue_root = tmp_path / "agent_service"
        requests_dir = queue_root / "requests"
        requests_dir.mkdir(parents=True)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        emergency_path = requests_dir / "a-emergency.json"
        diagnostics_path = requests_dir / "z-diagnostics.json"
        emergency_path.write_text(
            json.dumps(
                {
                    "request_id": "a-emergency",
                    "operation": "emergency.reconnect",
                    "payload": {
                        "slot_id": "BAY-01",
                        "repository_path": "D:\\",
                        "job_id": "priority-job",
                        "approval_bypass": True,
                        "approval_bypass_reason": "password_reauth",
                    },
                    "created_at": current_time,
                }
            ),
            encoding="utf-8",
        )
        diagnostics_path.write_text(
            json.dumps(
                {
                    "request_id": "z-diagnostics",
                    "operation": "veeam.diagnostics",
                    "payload": {"timeout_seconds": 8.0},
                    "created_at": current_time,
                }
            ),
            encoding="utf-8",
        )
        os.utime(emergency_path, (time.time() - 60, time.time() - 60))
        os.utime(diagnostics_path, None)

        processed = AgentServiceWorker(config_path, queue_root).process_once(max_requests=1)

        self.assertEqual(processed, 1)
        self.assertTrue((queue_root / "responses" / "a-emergency.json").exists())
        self.assertFalse((queue_root / "responses" / "z-diagnostics.json").exists())

    def test_agent_service_preflight_reports_permission_shortage(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["operation_mode"] = "commercial"
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        controller = LockFixController(load_config(config_path))
        worker = AgentServiceWorker(config_path, tmp_path / "agent_service")

        with patch.object(
            worker,
            "current_identity",
            return_value={
                "account": "CUSTOMER\\lockfix-svc",
                "is_local_system": False,
                "is_local_admin": False,
                "groups_probe_ok": True,
                "recommended_accounts": ["LocalSystem", "lockfix-svc"],
            },
        ), patch.object(worker, "powershell_probe", return_value={"ok": False, "error": "Access is denied.", "output": ""}), patch(
            "lockfix.agent_service.run_veeam_diagnostics",
            return_value={"success": True},
        ):
            result = worker.service_preflight({"operation_mode": "commercial"}, controller)

        self.assertFalse(result["ok"])
        self.assertIn("Disk Offline", result["restricted_features"])
        self.assertIn("Get-Disk 실행 불가", result["restricted_features"])
        audit_text = load_config(config_path).audit_log_path.read_text(encoding="utf-8")
        self.assertIn('"event": "service.permission.insufficient"', audit_text)

    def test_webui_requires_agent_service_for_privileged_operation_when_not_dry_run(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["dry_run"] = False
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        context = webui.WebContext(config_path)
        context.agent_service_queue_root = tmp_path / "missing_agent_service"

        with self.assertRaises(AgentServiceUnavailable):
            context.run_agent_service_operation("disk.isolate", {"slot_id": "BAY-01"}, timeout_seconds=0.1)

    def test_webui_starts_agent_worker_before_veeam_diagnostics(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        context = webui.WebContext(config_path)

        with patch.object(context, "start_agent_service_worker") as starter, patch(
            "webui.AgentServiceClient.submit_and_wait",
            return_value={"ok": True, "operation": "veeam.diagnostics", "diagnostics": {"success": True}},
        ):
            result = context.run_agent_service_operation("veeam.diagnostics", {"timeout_seconds": 8.0}, timeout_seconds=0.1)

        self.assertTrue(result["ok"])
        starter.assert_called_once()

    def test_webui_keeps_inline_fallback_only_for_dry_run_compatibility(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        controller = LockFixController(load_config(config_path))
        self.approve_operation(controller, "DISK_OFFLINE")
        context = webui.WebContext(config_path)
        context.agent_service_queue_root = tmp_path / "missing_agent_service"

        result = context.run_agent_service_operation("disk.isolate", {"slot_id": "BAY-01"}, timeout_seconds=0.1)

        self.assertTrue(result["ok"])
        self.assertTrue(result["inline_fallback"])
        self.assertEqual(result["state"], "ISOLATED")

    def test_lockfix_dry_run_environment_override_takes_precedence(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)

        with patch.dict("os.environ", {"LOCKFIX_DRY_RUN": "false"}, clear=False):
            config = load_config(config_path)

        self.assertFalse(config.dry_run)

    def test_default_veeam_config_targets_agent_backup_d_repo(self) -> None:
        config_path = Path(__file__).resolve().parents[1] / "config" / "lockfix.example.json"
        raw = json.loads(config_path.read_text(encoding="utf-8"))

        self.assertEqual(raw["veeam"]["job_name"], "Agent_backup")
        self.assertEqual(raw["veeam"]["target_repository_id"], "88788f9e-d8f5-4eb4-bc4f-9b3f5403bcec")
        self.assertEqual(raw["veeam"]["target_repository_name"], "D REPO")
        self.assertEqual(raw["veeam"]["target_repository_path"], "D:\\Backup")
        self.assertEqual(raw["slots"][0]["device"], "D:\\")
        self.assertEqual(raw["slots"][0]["mount_point"], "D:\\")

    def test_command_runner_handles_windows_output_decode_failures_safely(self) -> None:
        class Result:
            returncode = 1
            stdout = None
            stderr = None

        with patch("subprocess.run", return_value=Result()) as run:
            with self.assertRaisesRegex(CommandError, "exit code 1"):
                CommandRunner(dry_run=False).run(["powershell", "-Command", "Write-Error 실패"])

        kwargs = run.call_args.kwargs
        self.assertEqual(kwargs["encoding"], "utf-8")
        self.assertEqual(kwargs["errors"], "replace")

    def test_detect_fingerprint_uses_configured_identity_fields(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["slots"][0]["identity"].update(
            {
                "unique_id": "DISK-UNIQUE-01",
                "disk_size": "4 TB",
                "firmware": "FW-9001",
                "controller_location": "PCIROOT(0)#SLOT(2)",
            }
        )
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        config = load_config(config_path)
        slot = config.slot("BAY-01")

        parts = {part["key"]: part["value"] for part in fingerprint_parts(slot)}

        self.assertEqual(parts["unique_id"], "DISK-UNIQUE-01")
        self.assertEqual(parts["size"], "4 TB")
        self.assertEqual(parts["firmware"], "FW-9001")
        self.assertEqual(parts["controller_location"], "PCIROOT(0)#SLOT(2)")

        raw["slots"][0]["identity"]["firmware"] = "FW-9002"
        changed_path = tmp_path / "changed.json"
        changed_path.write_text(json.dumps(raw), encoding="utf-8")
        changed_slot = load_config(changed_path).slot("BAY-01")

        self.assertNotEqual(slot_uid(slot), slot_uid(changed_slot))

    def test_detect_disk_size_fallback_uses_volume_capacity_not_path(self) -> None:
        tmp_path = self.make_workspace()
        config = load_config(write_config(tmp_path))
        slot = config.slot("BAY-01")

        parts = {part["key"]: part["value"] for part in fingerprint_parts(slot)}

        self.assertNotEqual(parts["size"], str(slot.mount_point))
        self.assertNotEqual(parts["size"], slot.device)
        self.assertRegex(parts["size"], r"^[\d,]+ GB$")

    def test_webui_detect_summary_is_backed_by_fingerprint_parts(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["slots"][0]["identity"].update({"disk_size": "8 TB", "firmware": "FW-WEB"})
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def emergency_access_summary(self):
                return webui.LockFixWebHandler.emergency_access_summary(self)

            def detect_veeam_repository_summary(self):
                return webui.LockFixWebHandler.detect_veeam_repository_summary(self)

        summary = webui.LockFixWebHandler.detect_summary(Probe())
        parts = {part["key"]: part["value"] for part in summary["fingerprint"]["parts"]}

        self.assertEqual(parts["size"], "8 TB")
        self.assertEqual(parts["firmware"], "FW-WEB")
        self.assertIn("Disk Size", summary["fingerprint"]["formula"])

    def test_webui_detect_summary_marks_isolated_unmounted_volume_as_waiting(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)

        class Probe:
            context = webui.WebContext(config_path)

            def emergency_access_summary(self):
                return {
                    "slot": {
                        "slot_id": "BAY-01",
                        "state": "ISOLATED",
                        "hash_status": "WAITING_FOR_MOUNT",
                    },
                    "slots": [],
                }

            def detect_veeam_repository_summary(self):
                return {"repository_name": "D REPO", "repository_path": "D:\\Backup", "eligible": True}

        summary = webui.LockFixWebHandler.detect_summary(Probe())
        fingerprint = summary["fingerprint"]

        self.assertEqual(fingerprint["status"], "ISOLATED")
        self.assertFalse(fingerprint["match"])
        self.assertIn("오프라인/언마운트", fingerprint["conclusion"])

    def test_webui_detect_summary_includes_veeam_repository_from_rest(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "enabled": True,
            "base_url": "https://192.168.219.230:9419",
            "job_name": "Backup Copy Job 1",
            "target_repository_name": "DREPO",
            "target_repository_path": "G:\\",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def emergency_access_summary(self):
                return webui.LockFixWebHandler.emergency_access_summary(self)

            def detect_veeam_repository_summary(self):
                return webui.LockFixWebHandler.detect_veeam_repository_summary(self)

            def run_veeam_diagnostics_limited(self, veeam_config, timeout_seconds=3.0):
                return {
                    "source": "python_veeam_client",
                    "latest_configured_session": {
                        "source": "python_veeam_client",
                        "job_name": "Backup Copy Job 1",
                        "repository_name": "DREPO",
                        "repository_path": "G:\\",
                    },
                }

        summary = webui.LockFixWebHandler.detect_summary(Probe())
        repository = summary["veeam_repository"]

        self.assertEqual(repository["repository_name"], "DREPO")
        self.assertEqual(repository["repository_path"], "G:\\")
        self.assertTrue(repository["api_synced"])

    def test_webui_detect_summary_never_exposes_c_volume_as_veeam_repository(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "enabled": True,
            "base_url": "https://192.168.219.230:9419",
            "job_name": "Backup Copy Job 1",
            "target_repository_name": "OS",
            "target_repository_path": "C:\\",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def emergency_access_summary(self):
                return webui.LockFixWebHandler.emergency_access_summary(self)

            def detect_veeam_repository_summary(self):
                return webui.LockFixWebHandler.detect_veeam_repository_summary(self)

            def run_veeam_diagnostics_limited(self, veeam_config, timeout_seconds=3.0):
                return {
                    "source": "python_veeam_client",
                    "latest_configured_session": {
                        "source": "python_veeam_client",
                        "job_name": "Backup Copy Job 1",
                        "repository_name": "OS",
                        "repository_path": "C:\\",
                    },
                }

        summary = webui.LockFixWebHandler.detect_summary(Probe())
        repository = summary["veeam_repository"]

        self.assertEqual(repository["repository_path"], "-")
        self.assertFalse(repository["eligible"])
        self.assertNotIn("C:", json.dumps(repository))

    def test_detect_webui_uses_judgement_module_layout(self) -> None:
        root = Path.cwd()
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("디스크 식별 판정", app_source)
        self.assertIn("detect-action-row", app_source)
        self.assertIn('data-detect-action="logs"', app_source)
        self.assertIn('logsRange.highlight = keyword;', app_source)
        self.assertIn('showView("logs2");', app_source)
        self.assertIn("logs-highlight-row", css_source)
        self.assertIn('const isIsolated = status === "ISOLATED";', app_source)
        self.assertIn('statusClass = isNormal || isIsolated ? "normal" : "abnormal"', app_source)
        self.assertIn('isIsolated ? "ISOLATED"', app_source)
        self.assertIn('isIsolated ? "격리 볼륨"', app_source)
        self.assertIn('ISOLATED - VERIFICATION WAITING', app_source)
        self.assertIn(".detect-judgement-normal", css_source)
        self.assertIn(".detect-judgement-abnormal", css_source)
        self.assertIn(".detect-state-row", css_source)
        self.assertIn(".detect-action-primary", css_source)
        self.assertIn("background: #ffffff;", css_source)
        self.assertIn("color: #16a34a", css_source)
        self.assertIn("color: #ef4444", css_source)
        self.assertIn(".detect-fingerprint-root {\n  width: 100%;", css_source)
        self.assertIn(".detect-judgement-page {\n  width: 100%;\n  max-width: none;", css_source)
        self.assertIn(".detect-judgement-panel {\n  width: 100%;", css_source)
        self.assertIn("VEEAM REPOSITORY", app_source)
        self.assertIn("detect-veeam-repository-card", css_source)

    def test_customer_sidebar_uses_simplified_navigation_icons(self) -> None:
        root = Path.cwd()
        index_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('class="nav-icon detect-nav-icon"', index_source)
        self.assertIn('class="nav-icon settings-nav-icon"', index_source)
        self.assertIn('class="nav-icon logout-nav-icon"', index_source)
        self.assertIn('class="nav-icon logs-nav-icon"', index_source)
        self.assertIn('data-view="logs2"', index_source)
        self.assertIn(".detect-nav-icon svg", css_source)
        self.assertIn(".settings-nav-icon svg", css_source)
        self.assertIn(".logout-nav-icon svg", css_source)
        self.assertIn("width: 28px;", css_source)
        self.assertIn("height: 28px;", css_source)
        self.assertNotIn("transform: scale(2.25);", css_source)

    def test_security_audit_menu_is_separate_operational_view(self) -> None:
        root = Path.cwd()
        index_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertNotIn('data-view="securityAudit"', index_source)
        self.assertIn('id="securityAuditView"', index_source)
        self.assertIn('id="securityAuditSummary"', index_source)
        self.assertIn('id="securityAuditTable"', index_source)
        self.assertIn('id="securityAuditDetail"', index_source)
        self.assertIn('"nav.securityAudit": "보안 감사"', app_source)
        self.assertIn("function renderSecurityAudit", app_source)
        self.assertIn("function normalizeSecurityAuditRecord", app_source)
        self.assertIn("로그인 실패 횟수", app_source)
        self.assertIn("auth.login.locked", app_source)
        self.assertIn(".security-audit-layout", css_source)
        self.assertIn(".security-audit-detail-panel", css_source)

    def test_login_security_thresholds_issue_admin_approval_temporary_password(self) -> None:
        tmp_path = self.make_workspace()
        context = webui.WebContext(write_config(tmp_path))
        context.login_security_path = tmp_path / "login_security.json"

        first = context.register_login_failure("admin", "127.0.0.1")
        second = context.register_login_failure("admin", "127.0.0.1")
        third = context.register_login_failure("admin", "127.0.0.1")
        fourth = context.register_login_failure("admin", "127.0.0.1")
        fifth = context.register_login_failure("admin", "127.0.0.1")

        self.assertEqual(first["failure_count"], 1)
        self.assertFalse(second["warning"])
        self.assertTrue(third["warning"])
        self.assertFalse(fourth.get("locked", False) and bool(fourth.get("approval_token")))
        self.assertTrue(fifth["locked"])
        self.assertEqual(fifth["approval_status"], "PENDING")
        self.assertIn("approval_token", fifth)
        self.assertIn("temporary_password", fifth)
        self.assertEqual(context.verify_login_temp_password("admin", fifth["temporary_password"])["reason"], "approval_pending")

        approved = context.approve_login_temp_password(
            "admin",
            fifth["approval_token"],
            approved_by="administrator",
            client_ip="127.0.0.1",
        )
        self.assertTrue(approved["ok"])
        self.assertTrue(context.verify_login_temp_password("admin", fifth["temporary_password"])["ok"])

    def test_webui_sidebar_is_compact_to_prioritize_content(self) -> None:
        root = Path.cwd()
        index_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("width: min(1280px, calc(100% - 20px));", css_source)
        self.assertIn("grid-template-columns: 124px minmax(0, 1fr);", css_source)
        self.assertIn("grid-template-columns: 46px minmax(0, 1fr);", css_source)
        self.assertIn("padding: 28px 12px 22px;", css_source)
        self.assertIn("padding: 32px 34px 42px;", css_source)
        self.assertIn('id="sidebarToggle"', index_source)
        self.assertTrue((root / "web" / "static" / "oam-brand-mark.svg").exists())
        self.assertIn('class="sidebar-logo-mark"', index_source)
        self.assertIn('src="/static/oam-brand-mark.svg"', index_source)
        self.assertIn("lockfix.sidebarCollapsed", app_source)
        self.assertIn("applySidebarState", app_source)
        self.assertIn(".sidebar-collapsed .sidebar-logo-full", css_source)
        self.assertIn(".sidebar-collapsed .sidebar-logo-mark", css_source)
        self.assertIn("width: 24px;", css_source)
        self.assertIn(".sidebar-collapsed .side-item > span:not(.nav-icon)", css_source)
        self.assertIn("grid-template-columns: 1fr;", css_source)
        self.assertIn("grid-template-columns: repeat(6, 28px);", css_source)
        self.assertIn("pointer-events: auto;", css_source)
        self.assertIn("box-shadow: none;", css_source)

    def test_sidebar_user_menu_shows_current_session_without_navigation(self) -> None:
        root = Path.cwd()
        index_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="sidebarUserToggle"', index_source)
        self.assertIn('id="sidebarUserPanel"', index_source)
        self.assertIn('class="sidebar-user-chevron"', index_source)
        self.assertNotIn('id="sidebarUserToggle" data-view=', index_source)
        self.assertIn('"userMenu.title": "로그인 사용자"', app_source)
        self.assertIn("function renderSidebarUserMenu", app_source)
        self.assertIn("function setSidebarUserPanel", app_source)
        self.assertIn("currentSession.userId || currentSession.user", app_source)
        self.assertIn(".sidebar-user-menu", css_source)
        self.assertIn(".sidebar-user-chevron::before", css_source)
        self.assertIn(".sidebar-user-panel[hidden]", css_source)
        self.assertIn(".sidebar-user-toggle {", css_source)
        self.assertIn("border: 0;", css_source)
        self.assertNotIn("border: 1px solid rgba(196, 211, 225, 0.72);", css_source)
        self.assertNotIn("border: 1px solid rgba(121, 158, 206, 0.48);", css_source)
        self.assertIn("20260520-sidebar-account-actions", index_source)

    def test_isolate_reaches_isolated(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))
        self.approve_operation(controller, "DISK_OFFLINE")

        state = controller.isolate("BAY-01")

        self.assertEqual(state, LockFixState.ISOLATED)
        self.assertEqual(controller.status()["BAY-01"], "ISOLATED")

    def test_reconnect_uid_mismatch_quarantines(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path, expected_uid="wrong")))
        self.approve_operation(controller, "DISK_ONLINE")

        state = controller.reconnect("BAY-01")

        self.assertEqual(state, LockFixState.QUARANTINE)
        self.assertEqual(controller.status()["BAY-01"], "QUARANTINE")

    def test_reconnect_recovers_access_path_when_power_on_fails_but_disk_is_visible(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))
        self.approve_operation(controller, "DISK_ONLINE")

        class FailingPower:
            def on(self, slot_id: str) -> None:
                raise RuntimeError("invalid PDU URL")

            def off(self, slot_id: str) -> None:
                return None

            def status(self, slot_id: str) -> dict[str, object]:
                return {"ok": None}

        with patch("lockfix.controller.build_power_controller", return_value=FailingPower()), patch.object(
            controller.disk, "partition_visible", return_value=True
        ):
            state = controller.reconnect("BAY-01")

        self.assertEqual(state, LockFixState.ONLINE_VERIFIED_RW)
        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn("power.on.reconnect.warning", audit_text)
        self.assertIn("power.on.reconnect.continue_disk_visible", audit_text)
        self.assertIn("disk.access_path", audit_text)

    def test_emergency_reconnect_requires_matching_disk_hash(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))
        self.approve_operation(controller, "EMERGENCY_UNLOCK")

        with self.assertRaises(PermissionError):
            controller.emergency_reconnect("BAY-01", "wrong-hash")

        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn("emergency.reconnect.denied", audit_text)
        self.assertNotIn("wrong-hash", audit_text)
        self.assertIn("provided_hash_digest", audit_text)
        self.assertIn("expected_hash_digest", audit_text)
        self.assertNotIn("expected_hash_prefix", audit_text)

    def test_emergency_reconnect_verifies_then_reconnects_volume(self) -> None:
        tmp_path = self.make_workspace()
        controller = LockFixController(load_config(write_config(tmp_path)))
        self.approve_operation(controller, "EMERGENCY_UNLOCK")
        self.approve_operation(controller, "DISK_ONLINE")

        state = controller.emergency_reconnect("BAY-01", controller.emergency_access_hash("BAY-01"))

        self.assertEqual(state, LockFixState.ONLINE_VERIFIED_RW)
        self.assertEqual(controller.status()["BAY-01"], "ONLINE_VERIFIED_RW")
        audit_text = controller.config.audit_log_path.read_text(encoding="utf-8")
        self.assertIn("emergency.reconnect.approved", audit_text)
        self.assertIn("disk.safety.preflight.start", audit_text)
        self.assertIn("disk.mount_ro.start", audit_text)
        self.assertIn("Set-Disk -Number $disk.Number -IsReadOnly $true", audit_text)
        self.assertIn("Mount-Volume -DriveLetter $drive", audit_text)
        self.assertIn("Repair-Volume -DriveLetter $drive -Scan", audit_text)
        self.assertIn("Set-Disk -Number $disk.Number -IsReadOnly $false", audit_text)
        self.assertIn("disk.access_path.start", audit_text)
        self.assertIn("disk.access_path", audit_text)
        self.assertIn("disk.mount_rw", audit_text)
        self.assertIn("emergency.reconnect.complete", audit_text)

    def test_windows_disk_offline_requires_strict_offline_verification(self) -> None:
        tmp_path = self.make_workspace()
        config = load_config(write_config(tmp_path))
        base_slot = config.slot("BAY-01")
        slot = type(base_slot)(
            slot_id=base_slot.slot_id,
            device="D:\\",
            mount_point=Path("D:\\"),
            expected_uid=base_slot.expected_uid,
            identity=base_slot.identity,
            manifest_path=base_slot.manifest_path,
            power=base_slot.power,
        )
        audit_path = tmp_path / "offline-strict-audit.jsonl"

        class OfflineRunner(CommandRunner):
            def __init__(self) -> None:
                super().__init__(dry_run=False)

            def run(self, args: list[str], timeout: int = 120) -> str:
                command = " ".join(args)
                if "Set-Disk -Number $disk.Number -IsOffline $true" in command:
                    return (
                        'LOCKFIX_STORAGE_STATE={"drive":"D","accessPath":"D:\\\\","diskNumber":3,'
                        '"diskUniqueId":"TEST-DISK","isOffline":true,"method":"Set-Disk -IsOffline true"}\n'
                        "Disk 3: offline isolation completed for D:"
                    )
                if "Get-Disk -Number $diskNumber" in command:
                    return (
                        '{"drive":"D","diskNumber":3,"diskUniqueId":"TEST-DISK",'
                        '"isOffline":true,"pathReachable":false,'
                        '"accessPath":"D:\\\\","method":"Get-Disk + Test-Path strict offline verification"}'
                    )
                raise AssertionError(f"unexpected command: {command}")

        disk = DiskOperator(OfflineRunner(), AuditLogger(audit_path))

        disk.offline(slot)

        audit_text = audit_path.read_text(encoding="utf-8")
        self.assertIn("disk.offline.verify.start", audit_text)
        self.assertIn("disk.offline.verify", audit_text)
        self.assertIn('"is_offline": true', audit_text)
        self.assertIn('"path_reachable": false', audit_text)

    def test_windows_disk_offline_fails_when_disk_remains_online(self) -> None:
        tmp_path = self.make_workspace()
        config = load_config(write_config(tmp_path))
        base_slot = config.slot("BAY-01")
        slot = type(base_slot)(
            slot_id=base_slot.slot_id,
            device="D:\\",
            mount_point=Path("D:\\"),
            expected_uid=base_slot.expected_uid,
            identity=base_slot.identity,
            manifest_path=base_slot.manifest_path,
            power=base_slot.power,
        )
        audit_path = tmp_path / "offline-online-failure-audit.jsonl"

        class OnlineRunner(CommandRunner):
            def __init__(self) -> None:
                super().__init__(dry_run=False)

            def run(self, args: list[str], timeout: int = 120) -> str:
                command = " ".join(args)
                if "Set-Disk -Number $disk.Number -IsOffline $true" in command:
                    return (
                        'LOCKFIX_STORAGE_STATE={"drive":"D","accessPath":"D:\\\\","diskNumber":3,'
                        '"diskUniqueId":"TEST-DISK","isOffline":true,"method":"Set-Disk -IsOffline true"}\n'
                        "Disk 3: offline isolation completed for D:"
                    )
                if "Get-Disk -Number $diskNumber" in command:
                    raise CommandError("Disk 3 is still Online; Veeam-completed isolation requires IsOffline=True")
                raise AssertionError(f"unexpected command: {command}")

        disk = DiskOperator(OnlineRunner(), AuditLogger(audit_path))

        with self.assertRaises(CommandError):
            disk.offline(slot)

        audit_text = audit_path.read_text(encoding="utf-8")
        self.assertIn("disk.offline.verify.error", audit_text)
        self.assertIn("still Online", audit_text)

    def test_airgap_summary_exposes_emergency_volume_access_state(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)

        class Probe:
            context = webui.WebContext(config_path)

        summary = webui.LockFixWebHandler.emergency_access_summary(Probe(), {})
        emergency = summary["slot"]

        self.assertEqual(emergency["slot_id"], "BAY-01")
        self.assertNotIn("authorization_hash", emergency)
        self.assertNotIn("current_uid", emergency)
        self.assertNotIn("manifest_hash", emergency)
        self.assertEqual(emergency["authorization_hash_short"], f"{slot_uid(Probe.context.config.slot('BAY-01'))[:16]}...{slot_uid(Probe.context.config.slot('BAY-01'))[-8:]}")
        self.assertTrue(emergency["authorization_hash_protected"])
        self.assertIn("current_uid_short", emergency)
        self.assertIn("hash_status", emergency)

    def test_airgap_summary_does_not_block_on_unmounted_emergency_volume(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["slots"][0]["device"] = str(tmp_path / "missing-drive")
        raw["slots"][0]["mount_point"] = str(tmp_path / "missing-drive")
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

        summary = webui.LockFixWebHandler.emergency_access_summary(Probe(), {})
        emergency = summary["slot"]

        self.assertEqual(emergency["hash_status"], "WAITING_FOR_MOUNT")
        self.assertEqual(emergency["current_uid_short"], "")
        self.assertTrue(emergency["eligible"])

    def test_emergency_reconnect_status_returns_live_detail_logs(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        context = webui.WebContext(config_path)
        job_id = "job-live-status"
        with context.emergency_jobs_lock:
            context.emergency_jobs["BAY-01"] = {
                "job_id": job_id,
                "slot_id": "BAY-01",
                "repository_path": "D:\\",
                "status": "running",
                "started_at": webui.datetime.now().isoformat(timespec="seconds"),
                "background_started_at": webui.datetime.now().isoformat(timespec="seconds"),
                "approved_until": webui.datetime.now().isoformat(timespec="seconds"),
                "message": "Emergency reconnect background worker is running.",
            }
        context.controller.audit.write("state.transition", slot_id="BAY-01", state="WAITING_DISK")
        context.controller.audit.write(
            "emergency.reconnect.background.error",
            slot_id="BAY-01",
            job_id=job_id,
            error="LOCK-FIX Agent/Service is not responding.",
            resolution="LOCK-FIX Agent/Service 워커를 실행하세요.",
        )
        context.controller.audit.write(
            "emergency.reconnect.background.timeout",
            slot_id="BAY-01",
            job_id=job_id,
            elapsed_seconds=182,
            timeout_seconds=180,
            message="재접속 작업 제한 시간을 초과했습니다.",
            resolution="Get-Disk/Get-Partition 권한을 확인하세요.",
        )

        result = context.emergency_reconnect_status("BAY-01", job_id)
        audit_text = context.config.audit_log_path.read_text(encoding="utf-8")

        self.assertEqual(result["status"], "running")
        self.assertEqual(result["flow_state"], "WAITING_DISK")
        self.assertTrue(any("WAITING_DISK" in line for line in result["detail_logs"]))
        self.assertTrue(any("Agent/Service is not responding" in line for line in result["detail_logs"]))
        self.assertTrue(any("BACKGROUND TIMEOUT" in line for line in result["detail_logs"]))
        self.assertTrue(any("Get-Disk/Get-Partition" in line for line in result["detail_logs"]))
        self.assertIn("emergency.reconnect.heartbeat", audit_text)

    def test_emergency_reconnect_status_fails_fast_when_agent_worker_never_picks_up_request(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        context = webui.WebContext(config_path)
        job_id = "job-missing-agent"
        started_at = (webui.datetime.now() - webui.timedelta(seconds=webui.EMERGENCY_RECONNECT_AGENT_START_TIMEOUT_SECONDS + 1)).isoformat(timespec="seconds")
        with context.emergency_jobs_lock:
            context.emergency_jobs["BAY-01"] = {
                "job_id": job_id,
                "slot_id": "BAY-01",
                "repository_path": "D:\\",
                "status": "running",
                "started_at": started_at,
                "background_started_at": started_at,
                "message": "Emergency reconnect background worker is running.",
            }

        result = context.emergency_reconnect_status("BAY-01", job_id)
        audit_text = context.config.audit_log_path.read_text(encoding="utf-8")

        self.assertEqual(result["status"], "error")
        self.assertIn("Agent/Service is not responding", result["error"])
        self.assertTrue(any("Agent/Service is not responding" in line for line in result["detail_logs"]))
        self.assertIn("emergency.reconnect.background.error", audit_text)

    def test_logs_menu_formats_emergency_reconnect_history(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)

        class Probe:
            context = webui.WebContext(config_path)

        record = {
            "event": "emergency.reconnect.heartbeat",
            "slot_id": "BAY-01",
            "background_started": True,
            "message": "Emergency reconnect background worker is running.",
        }

        message = webui.LockFixWebHandler.format_log_audit_record(Probe(), record)

        self.assertIn("LOCK-FIX Reconnect HEARTBEAT", message)
        self.assertIn("BAY-01", message)

    def test_webui_audit_readers_tolerate_windows_non_utf8_output(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        config = load_config(config_path)
        config.audit_log_path.write_bytes(
            b'{"ts":"2026-05-05T13:14:09+00:00","event":"disk.unmount","slot_id":"BAY-01","output":"ok"}\n'
            b'{"ts":"2026-05-05T13:14:16+00:00","event":"disk.unmount.error","slot_id":"BAY-01","error":"\xbd"}\n'
        )

        class Probe:
            context = webui.WebContext(config_path)

        latest = webui.LockFixWebHandler.latest_audit_record(Probe(), "BAY-01", {"disk.unmount", "disk.unmount.error"})
        items = webui.LockFixWebHandler.audit_items(Probe())

        self.assertEqual(latest["event"], "disk.unmount.error")
        self.assertEqual(items[0]["event"], "disk.unmount.error")
        self.assertIn("�", items[0]["error"])

    def test_state_store_repairs_trailing_json_garbage(self) -> None:
        tmp_path = self.make_workspace()
        state_path = tmp_path / "state.json"
        state_path.write_text('{\n  "BAY-01": "UNMOUNTING"\n}\n}\n', encoding="utf-8")
        store = StateStore(state_path)

        self.assertEqual(store.read_all(), {"BAY-01": "UNMOUNTING"})
        self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), {"BAY-01": "UNMOUNTING"})
        self.assertTrue(state_path.with_suffix(".json.corrupt").exists())

    def test_windows_c_volume_is_never_unmount_target(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        config = load_config(config_path)
        slot = config.slot("BAY-01")
        protected_slot = type(slot)(
            slot_id=slot.slot_id,
            device="C:\\",
            mount_point=Path("C:\\"),
            expected_uid=slot.expected_uid,
            identity=slot.identity,
            manifest_path=slot.manifest_path,
            power=slot.power,
        )
        disk = DiskOperator(CommandRunner(dry_run=True), AuditLogger(tmp_path / "audit-c-block.jsonl"))

        with self.assertRaises(ValueError):
            disk.unmount(protected_slot)

    def test_unmount_uses_preflight_cache_flush_and_non_force_dismount(self) -> None:
        tmp_path = self.make_workspace()
        config = load_config(write_config(tmp_path))
        audit_path = tmp_path / "safe-unmount-audit.jsonl"
        disk = DiskOperator(CommandRunner(dry_run=True), AuditLogger(audit_path))

        disk.unmount(config.slot("BAY-01"))

        audit_text = audit_path.read_text(encoding="utf-8")
        self.assertIn("disk.safety.preflight.start", audit_text)
        self.assertIn("disk.safety.preflight.ok", audit_text)
        self.assertIn("disk.cache.flush.start", audit_text)
        self.assertIn("disk.cache.flush", audit_text)
        self.assertIn("disk.dismount.start", audit_text)
        self.assertIn("disk.dismount", audit_text)
        self.assertIn("disk.drive_letter.remove.start", audit_text)
        self.assertIn("disk.drive_letter.remove", audit_text)
        self.assertIn("Dismount-Volume -DriveLetter $drive -ErrorAction Stop", audit_text)
        self.assertIn("Remove-PartitionAccessPath", audit_text)
        self.assertIn("access path removed and no longer reachable", audit_text)
        self.assertIn("disk.unmount.verify", audit_text)
        self.assertNotIn("-Force", audit_text)

    def test_windows_offline_records_drive_path_verification(self) -> None:
        tmp_path = self.make_workspace()
        config = load_config(write_config(tmp_path))
        base_slot = config.slot("BAY-01")
        slot = type(base_slot)(
            slot_id=base_slot.slot_id,
            device="D:\\",
            mount_point=Path("D:\\"),
            expected_uid=base_slot.expected_uid,
            identity=base_slot.identity,
            manifest_path=base_slot.manifest_path,
            power=base_slot.power,
        )
        audit_path = tmp_path / "offline-verify-audit.jsonl"

        class StorageRunner(CommandRunner):
            def __init__(self) -> None:
                super().__init__(dry_run=False)

            def run(self, args: list[str], timeout: int = 120) -> str:
                command = " ".join(args)
                if "Set-Disk -Number $disk.Number -IsOffline $true" in command:
                    return (
                        'LOCKFIX_STORAGE_STATE={"drive":"D","accessPath":"D:\\\\","diskNumber":3,'
                        '"diskUniqueId":"TEST-DISK","isOffline":true,"method":"Set-Disk -IsOffline true"}\n'
                        "Disk 3: offline isolation completed for D:"
                    )
                if "Get-Disk -Number $diskNumber" in command:
                    return (
                        '{"drive":"D","diskNumber":3,"diskUniqueId":"TEST-DISK",'
                        '"isOffline":true,"pathReachable":false,'
                        '"accessPath":"D:\\\\","method":"Get-Disk + Test-Path offline verification"}'
                    )
                raise AssertionError(f"unexpected command: {command}")

        disk = DiskOperator(StorageRunner(), AuditLogger(audit_path))

        disk.offline(slot)

        audit_text = audit_path.read_text(encoding="utf-8")
        self.assertIn("disk.offline.start", audit_text)
        self.assertIn("disk.offline", audit_text)
        self.assertIn("disk.offline.verify.start", audit_text)
        self.assertIn("disk.offline.verify", audit_text)
        self.assertIn('"path_reachable": false', audit_text)
        self.assertIn('"is_offline": true', audit_text)

    def test_removable_reblock_removes_current_drive_letter_when_set_disk_offline_is_unsupported(self) -> None:
        tmp_path = self.make_workspace()
        config = load_config(write_config(tmp_path))
        base_slot = config.slot("BAY-01")
        slot = type(base_slot)(
            slot_id=base_slot.slot_id,
            device="G:\\",
            mount_point=Path("G:\\"),
            expected_uid=base_slot.expected_uid,
            identity=base_slot.identity,
            manifest_path=base_slot.manifest_path,
            power=base_slot.power,
        )
        audit_path = tmp_path / "removable-reblock-audit.jsonl"
        (tmp_path / "storage-BAY-01.json").write_text(
            json.dumps(
                {
                    "accessPath": "G:\\",
                    "diskNumber": 1,
                    "partitionNumber": 1,
                    "diskUniqueId": "USB-DISK",
                    "isOffline": False,
                    "offlineEquivalent": True,
                    "setDiskOfflineSupported": False,
                    "pathReachable": False,
                }
            ),
            encoding="utf-8",
        )

        class RemovableRunner(CommandRunner):
            def __init__(self) -> None:
                super().__init__(dry_run=False)

            def run(self, args: list[str], timeout: int = 120) -> str:
                command = " ".join(args)
                if "Set-Disk -Number $disk.Number -IsOffline $true" in command:
                    raise CommandError("Set-Disk : Not Supported. Removable media cannot be set to offline.")
                if "Unauthorized removable-media online state was reblocked" in command:
                    if "Remove-PartitionAccessPath" not in command:
                        raise AssertionError(f"expected access path removal command: {command}")
                    return (
                        'LOCKFIX_STORAGE_STATE={"drive":"G","accessPath":"G:\\\\","diskNumber":1,'
                        '"diskUniqueId":"USB-DISK","isOffline":false,"offlineEquivalent":true,'
                        '"setDiskOfflineSupported":false,"pathReachable":false,'
                        '"removedAccessPaths":["F:\\\\"],"currentDriveLetters":[],"remainingAccessPaths":[],'
                        '"method":"Unauthorized removable-media drive letter/access path removed"}\n'
                        "Unauthorized removable-media online state was reblocked by removing access paths"
                    )
                raise AssertionError(f"unexpected command: {command}")

        disk = DiskOperator(RemovableRunner(), AuditLogger(audit_path))

        self.assertTrue(disk.enforce_offline_unless_approved(slot, approved=False, reason="unit_test_guard"))

        audit_text = audit_path.read_text(encoding="utf-8")
        self.assertIn("disk.online.unauthorized.reblock.error", audit_text)
        self.assertIn("disk.online.unauthorized.reblock.removable_fallback.start", audit_text)
        self.assertIn("disk.online.unauthorized.reblock.removable_fallback", audit_text)
        self.assertIn("disk.online.unauthorized.reblock", audit_text)
        self.assertIn("F:\\\\", audit_text)

    def test_storage_permission_denied_uses_system_fallback(self) -> None:
        tmp_path = self.make_workspace()
        audit_path = tmp_path / "system-fallback-audit.jsonl"

        class DeniedRunner(CommandRunner):
            def __init__(self) -> None:
                super().__init__(dry_run=False)

            def run(self, args: list[str], timeout: int = 120) -> str:
                raise CommandError("Get-Volume : 액세스가 거부되었습니다.")

        class FallbackDisk(DiskOperator):
            def run_storage_command_as_system(self, command_text: str, timeout: int = 120) -> str:
                self.audit.write("test.system_fallback.invoked", command=command_text)
                return "SYSTEM fallback OK"

        disk = FallbackDisk(DeniedRunner(), AuditLogger(audit_path))

        output = disk.storage_run([
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-Volume -DriveLetter D",
        ])

        self.assertEqual(output, "SYSTEM fallback OK")
        audit_text = audit_path.read_text(encoding="utf-8")
        self.assertIn('"event": "storage.command.primary_denied"', audit_text)
        self.assertIn('"event": "test.system_fallback.invoked"', audit_text)

    def test_non_storage_permission_denied_does_not_use_system_fallback(self) -> None:
        tmp_path = self.make_workspace()

        class DeniedRunner(CommandRunner):
            def __init__(self) -> None:
                super().__init__(dry_run=False)

            def run(self, args: list[str], timeout: int = 120) -> str:
                raise CommandError("access is denied")

        class FallbackDisk(DiskOperator):
            def run_storage_command_as_system(self, command_text: str, timeout: int = 120) -> str:
                raise AssertionError("fallback should not run for non-storage commands")

        disk = FallbackDisk(DeniedRunner(), AuditLogger(tmp_path / "non-storage-audit.jsonl"))

        with self.assertRaisesRegex(CommandError, "access is denied"):
            disk.storage_run([
                "powershell",
                "-NoProfile",
                "-Command",
                "Write-Output 'hello'",
            ])

    def test_veeam_api_version_defaults_to_vbr_reference_version(self) -> None:
        tmp_path = self.make_workspace()

        config = load_config(write_config(tmp_path))
        settings = VeeamSettings.from_config(config.veeam)

        self.assertEqual(config.veeam.api_version, "1.2-rev1")
        self.assertEqual(settings.api_version, "1.2-rev1")

    def test_veeam_api_version_can_be_overridden_by_config(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {"api_version": "1.3-rev0"}
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)
        settings = VeeamSettings.from_config(config.veeam)

        self.assertEqual(config.veeam.api_version, "1.3-rev0")
        self.assertEqual(settings.api_version, "1.3-rev0")

    def test_veeam_auto_discovery_settings_are_loaded(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "auto_discover": True,
            "discovery_candidates": ["https://192.168.219.230:9419"],
            "discovery_scan_local_subnet": False,
            "discovery_timeout_seconds": 0.2,
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)
        settings = VeeamSettings.from_config(config.veeam)

        self.assertTrue(config.veeam.auto_discover)
        self.assertEqual(config.veeam.discovery_candidates, ["https://192.168.219.230:9419"])
        self.assertFalse(settings.discovery_scan_local_subnet)
        self.assertEqual(settings.discovery_timeout_seconds, 0.2)

    def test_veeam_auto_discovery_selects_working_backup_server(self) -> None:
        with patch.dict("os.environ", {"LOCKFIX_TEST_VEEAM_PASSWORD": "secret"}, clear=False):
            client = create_veeam_client(
                {
                    "username": "administrator",
                    "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
                    "base_url": "https://127.0.0.1:9419",
                    "auto_discover": True,
                    "discovery_candidates": ["https://192.168.219.230:9419"],
                    "discovery_scan_local_subnet": False,
                }
            )
        with patch(
            "lockfix.veeam_client.discover_veeam_base_url",
            return_value=("https://192.168.219.230:9419", [{"base_url": "https://192.168.219.230:9419", "ok": True}]),
        ):
            client.ensure_discovered_base_url()

        self.assertEqual(client.settings.base_url, "https://192.168.219.230:9419")
        self.assertEqual(client.discovery_result["selected"], "https://192.168.219.230:9419")

    def test_only_config_veeam_section_is_used_for_veeam_settings(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {"job_name": "OriginalJob", "api_version": "1.2-rev1"}
        raw["veeam_backup"] = {
            "job_name": "Agent_backup",
            "api_version": "1.3-rev0",
            "target_repository_name": "DREPO",
            "target_repository_path": "D:\\copy",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)

        self.assertEqual(config.veeam.job_name, "OriginalJob")
        self.assertEqual(config.veeam.api_version, "1.2-rev1")
        self.assertEqual(config.veeam.target_repository_name, "")
        self.assertEqual(config.veeam.target_repository_path, "")

    def test_veeam_verify_ssl_string_false_becomes_boolean_false(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "username": "administrator",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
            "verify_ssl": "false",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        config = load_config(config_path)
        with patch.dict("os.environ", {"LOCKFIX_TEST_VEEAM_PASSWORD": "secret"}, clear=False):
            client = create_veeam_client({"username": "administrator", "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD", "verify_ssl": "false"})

        self.assertIs(config.veeam.verify_ssl, False)
        self.assertIs(client.settings.verify_ssl, False)

    def test_veeam_entrypoints_use_shared_client_factory(self) -> None:
        root = Path.cwd()
        entrypoints = [
            root / "lockfixctl.py",
            root / "webui.py",
            root / "lockfix" / "veeam_diagnostics.py",
            root / "lockfix" / "veeam_watcher.py",
        ]

        for path in entrypoints:
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("VeeamClient(", source, f"{path} must not construct VeeamClient directly")

        self.assertIn("run_veeam_diagnostics(self.context.config, self.context.controller)", (root / "webui.py").read_text(encoding="utf-8"))
        self.assertIn("create_veeam_client(veeam_config)", (root / "lockfix" / "veeam_diagnostics.py").read_text(encoding="utf-8"))
        self.assertIn("run_veeam_diagnostics(self.config, self.controller)", (root / "lockfix" / "veeam_watcher.py").read_text(encoding="utf-8"))
        self.assertIn("VeeamClient(settings)", (root / "lockfix" / "veeam_factory.py").read_text(encoding="utf-8"))
        self.assertIn('veeam_config = config.get("veeam", {})', (root / "webui.py").read_text(encoding="utf-8"))

    def test_webui_treats_console_log_veeam_state_as_synced(self) -> None:
        source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn("function isVeeamSynced", source)
        self.assertIn('stateSource.startsWith("veeam_rest_api")', source)

    def test_airgap_ui_exposes_emergency_volume_access_button(self) -> None:
        source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css = (Path.cwd() / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("emergency_access", source)
        self.assertIn("/api/emergency-reconnect", source)
        self.assertIn("긴급 볼륨 접속", source)
        self.assertIn("Reconnect History", source)
        self.assertIn("Reconnect State Flow", source)
        self.assertIn("ONLINE_VERIFIED_RW", source)
        self.assertIn("RECONNECT_REQUESTED", source)
        self.assertIn("const reconnectIsComplete = isEmergencyReconnectCompleteState(reconnectReportedState)", source)
        self.assertIn("emergencyReconnectDetailLogs.length > 0 || reconnectIsComplete", source)
        self.assertIn("index <= reconnectCurrentIndex) return \"done\"", source)
        self.assertIn("emergency-reconnect-flow", source)
        self.assertIn("completeEmergencyReconnectWatch", source)
        self.assertIn("긴급 접속 완료", source)
        self.assertIn("긴급 접속이 완료되었다", source)
        self.assertIn("완료 이력 저장됨", source)
        self.assertIn("재접속 작업이 현재 서비스에 등록되어 있지 않습니다", source)
        self.assertIn("로그인 세션이 만료되어 긴급 재접속 요청이 서비스에 전달되지 않았습니다", source)
        self.assertIn('credentials: "same-origin"', source)
        self.assertIn("requestEmergencyReconnectPassword", source)
        self.assertIn("reauth_password", source)
        self.assertIn("비밀번호 재인증", source)
        self.assertNotIn("requestEmergencyApprovalPassword", source)
        self.assertNotIn("승인 비밀번호", source)
        self.assertNotIn("approval_password", source)
        self.assertIn(".emergency-approval-modal", css)
        self.assertIn(".emergency-approval-card", css)
        self.assertIn(".emergency-reauth-card", css)
        self.assertIn("인증 해시값 전체를 입력하세요", source)
        self.assertNotIn("data-hash=", source)
        self.assertIn("last_reconnect", source)
        self.assertIn("reconnect_history", source)
        self.assertIn("data-lock-disabled", source)
        self.assertIn(".emergency-access-panel", css)
        self.assertIn(".emergency-access-button", css)
        self.assertIn(".emergency-reconnect-flow", css)
        self.assertIn(".emergency-reconnect-arrow", css)
        self.assertIn(".emergency-access-grid .emergency-history", css)
        self.assertNotIn("자동 승인 검증", source)
        self.assertNotIn("airgap-approval-verification", source)
        self.assertNotIn("airgap-approval-grid", css)

    def test_webui_has_local_package_folder_open_endpoint(self) -> None:
        source = (Path.cwd() / "webui.py").read_text(encoding="utf-8")

        self.assertIn("/open-latest-package-folder", source)
        self.assertIn("os.startfile", source)
        self.assertIn("local access only", source)

    def test_webui_starts_automatic_veeam_steering_worker(self) -> None:
        source = (Path.cwd() / "webui.py").read_text(encoding="utf-8")

        self.assertIn("def start_veeam_steering_worker", source)
        self.assertIn("LOCKFIXVeeamSteeringWorker", source)
        self.assertIn("run_veeam_steering_once", source)
        self.assertIn("veeam_steering_state.json", source)
        self.assertIn("context.start_veeam_steering_worker()", source)
        self.assertIn("LOCKFIX_DISABLE_VEEAM_STEERING", source)
        self.assertIn("veeam_interlock_runtime(probe, time.time(), poll_api=True)", source)

    def test_webui_uses_password_reauth_only_for_emergency_reconnect(self) -> None:
        source = (Path.cwd() / "webui.py").read_text(encoding="utf-8")
        app_source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn("def verify_current_session_password", source)
        self.assertIn('payload.get("reauth_password")', source)
        self.assertIn("emergency.reconnect.reauth.success", source)
        self.assertIn("emergency.reconnect.reauth.failed", source)
        self.assertIn("emergency.reconnect.password_approval_bypass", source)
        self.assertIn("approval_bypass = True", source)
        self.assertIn('"approval_bypass": bool(approval_bypass)', source)
        self.assertIn("password_reauth", source)
        self.assertIn("start_agent_service_worker", source)
        self.assertIn("LOCKFIXAgentServiceWorker", source)
        self.assertNotIn("emergency.reconnect.approval.required", source)
        self.assertNotIn("missing_emergency_reconnect_approvals", source)
        self.assertNotIn("create_emergency_reconnect_approval_requests", source)
        self.assertNotIn("showEmergencyReconnectApprovalRequired", app_source)
        self.assertNotIn("approval required:", app_source)
        self.assertNotIn("approval_password_failed", source)
        self.assertNotIn("긴급 재접속 승인 비밀번호가 일치하지 않습니다.", source)

    def test_airgap_live_reconnect_errors_are_visible_in_current_log(self) -> None:
        app_source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")
        html_source = (Path.cwd() / "web" / "static" / "index.html").read_text(encoding="utf-8")
        webui_source = (Path.cwd() / "webui.py").read_text(encoding="utf-8")

        self.assertIn("20260520-alert-link-routing", html_source)
        self.assertIn("emergency.reconnect.background.timeout", webui_source)
        self.assertIn("EMERGENCY_RECONNECT_AGENT_START_TIMEOUT_SECONDS", webui_source)
        self.assertIn("emergency_reconnect_agent_started", webui_source)
        self.assertIn("BACKGROUND TIMEOUT", webui_source)
        self.assertIn("해결 안내: ${emergencyReconnectResolutionText(result)}", app_source)
        self.assertIn("if (text) return text;", app_source)
        self.assertNotIn("상세 오류는 백그라운드 로그 이력에 저장됨", app_source)
        self.assertNotIn("<span>실시간 작업 로그</span>", app_source)
        self.assertNotIn("request accepted; live detail logging started", app_source)
        self.assertNotIn("background job accepted", app_source)
        self.assertNotIn("긴급 접속 작업이 백그라운드에서 시작되었습니다.", app_source)

    def test_login_success_shows_two_second_loading_splash(self) -> None:
        app_source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")
        html_source = (Path.cwd() / "web" / "static" / "index.html").read_text(encoding="utf-8")
        css_source = (Path.cwd() / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("const LOGIN_SPLASH_DURATION_MS = 2000;", app_source)
        self.assertIn("showLoginSplashThenEnter", app_source)
        self.assertIn("setTimeout(resolve, LOGIN_SPLASH_DURATION_MS)", app_source)
        self.assertIn('class="splash-stage"', html_source)
        self.assertIn('class="splash-loader"', html_source)
        self.assertIn("@keyframes splashProgress", css_source)
        self.assertIn("animation: splashProgress 2000ms", css_source)
        self.assertIn("@keyframes splashBreath", css_source)

    def test_ops_events_panel_is_hidden_while_background_collection_remains(self) -> None:
        html_source = (Path.cwd() / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (Path.cwd() / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('class="ops-events ops-events-hidden" hidden aria-hidden="true"', html_source)
        self.assertIn(".ops-events[hidden]", css_source)
        self.assertIn("display: none !important;", css_source)
        self.assertIn("latestOpsEvents", app_source)
        self.assertIn("opsEventList.innerHTML", app_source)
        self.assertIn("dashboardLogs", app_source)
        self.assertIn("latestLogsData", app_source)
        self.assertIn("opsEventsToggle?.addEventListener", app_source)
        self.assertIn("v=20260521-hide-ops-events-panel", html_source)

    def test_network_detail_cards_use_subtle_show_toggles(self) -> None:
        root = Path.cwd()
        html_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="networkPathToggle" data-i18n="network.pathBadgeCollapsed">Show</button>', html_source)
        self.assertIn('id="networkPortToggle" data-i18n="network.portBadgeCollapsed">Show</button>', html_source)
        self.assertIn('id="networkInsightToggle" data-i18n="network.insightBadgeCollapsed">Show</button>', html_source)
        self.assertNotIn('data-i18n="network.pathBadgeCollapsed">보기</button>', html_source)
        self.assertNotIn('data-i18n="network.portBadgeCollapsed">보기</button>', html_source)
        self.assertIn('"network.pathBadgeCollapsed": "Show"', app_source)
        self.assertIn('"network.portBadgeCollapsed": "Show"', app_source)
        self.assertIn('"network.insightBadgeCollapsed": "Show"', app_source)
        self.assertIn('"network.pathBadge": "Hide"', app_source)
        self.assertIn('"network.portBadge": "Hide"', app_source)
        self.assertIn('"network.insightBadgeExpanded": "Hide"', app_source)
        self.assertNotIn('"network.pathBadgeCollapsed": "보기"', app_source)
        self.assertNotIn('"network.portBadgeCollapsed": "보기"', app_source)
        self.assertIn(".network-insight-toggle::after", css_source)
        self.assertIn("content: none !important;", css_source)
        self.assertIn("font-weight: 400 !important;", css_source)
        self.assertIn("opacity: 0.6 !important;", css_source)
        self.assertIn('[data-network-card="path"]:has(.network-path-list-collapsed)', css_source)
        self.assertIn('[data-network-card="ports"]:has(.network-port-list-collapsed)', css_source)
        self.assertIn('[data-network-card="insights"]:has(.network-insight-list-collapsed)', css_source)
        self.assertIn("height: 68px !important;", css_source)
        self.assertIn("min-height: 36px !important;", css_source)
        self.assertIn("border-bottom: 0 !important;", css_source)
        self.assertIn("20260520-sidebar-account-actions", html_source)

    def test_logs_summary_cards_render_above_filter_bar(self) -> None:
        html_source = (Path.cwd() / "web" / "static" / "index.html").read_text(encoding="utf-8")
        logs_view = html_source.split('id="logs2View"', 1)[1].split('id="license2View"', 1)[0]

        self.assertLess(logs_view.index('id="logsSummaryCards"'), logs_view.index('class="logs-range"'))
        self.assertLess(logs_view.index('id="logsSummaryCards"'), logs_view.index('id="logsStart"'))
        self.assertNotIn('data-i18n="logs.filteredView"', logs_view)
        self.assertIn("20260520-sidebar-account-actions", html_source)

    def test_settings_view_uses_full_width_balanced_grid(self) -> None:
        root = Path.cwd()
        html_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('settings-card settings-language-card', html_source)
        self.assertIn('settings-card settings-theme-card', html_source)
        self.assertIn('settings-card settings-log-retention-card', html_source)
        self.assertIn("max-width: none;", css_source)
        self.assertIn("grid-template-columns: repeat(12, minmax(0, 1fr));", css_source)
        self.assertIn(".settings-notification-card", css_source)
        self.assertIn("grid-column: span 7;", css_source)
        self.assertIn(".settings-navigation-card", css_source)
        self.assertIn("grid-column: span 5;", css_source)
        self.assertIn(".settings-actions", css_source)
        self.assertIn("grid-column: 1 / -1;", css_source)
        self.assertIn("@media (max-width: 1280px)", css_source)
        self.assertIn("20260520-sidebar-account-actions", html_source)

    def test_settings_service_policy_card_is_not_rendered(self) -> None:
        html_source = (Path.cwd() / "web" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertNotIn("settings-service-card", html_source)
        self.assertNotIn("serviceControlStatus", html_source)
        self.assertNotIn("servicePreflightStatus", html_source)
        self.assertNotIn("권한 운영 정책", html_source)

    def test_settings_hardware_shortcut_is_not_rendered(self) -> None:
        html_source = (Path.cwd() / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertNotIn('data-settings-view="hardware"', html_source)
        self.assertNotIn("settingsHardwareStatus", html_source)
        self.assertIn("settingsHardwareStatus", app_source)
        self.assertIn('id="hardwareView"', html_source)

    def test_static_web_ui_text_uses_language_bindings(self) -> None:
        root = Path.cwd()
        html_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")

        for token in [
            'data-i18n="login.email"',
            'data-i18n-placeholder="login.email"',
            'data-i18n-aria-label="login.qrConfirm"',
            'data-i18n-title="monitoring.download"',
            'data-i18n="ops.eventsDesc"',
            'data-i18n="logs.title"',
            'data-i18n="notification.title"',
            'data-i18n="auditLogs.title"',
            'data-i18n="accessDenied.message"',
            'data-i18n="threatPolicy.title"',
            'data-i18n="licenseModal.title"',
            'data-i18n="accountGuide.body"',
            'data-i18n="airgapConfirm.ok"',
            'data-i18n="department.backupOperation"',
        ]:
            self.assertIn(token, html_source)
        for token in [
            'node.setAttribute("placeholder", t(node.dataset.i18nPlaceholder))',
            'node.setAttribute("title", t(node.dataset.i18nTitle))',
            'node.setAttribute("aria-label", t(node.dataset.i18nAriaLabel))',
            '"login.email": "이메일"',
            '"login.email": "Email"',
            '"notification.title": "보안 알림 게이트웨이"',
            '"notification.title": "Security Notification Gateway"',
            '"auditLogs.title": "감사 로그"',
            '"auditLogs.title": "Audit Logs"',
            '"threatPolicy.title": "위협 탐지 정책"',
            '"threatPolicy.title": "Threat Detection Policy"',
            '"licenseModal.register": "라이선스 등록"',
            '"licenseModal.register": "Register License"',
            '"department.hardwareControl": "하드웨어 제어"',
            '"department.hardwareControl": "Hardware Control"',
            "departmentDisplayName(department.id)",
        ]:
            self.assertIn(token, app_source)
        self.assertIn("20260520-sidebar-account-actions", html_source)

    def test_monitoring_header_copy_is_hidden_while_polling_remains(self) -> None:
        root = Path.cwd()
        html_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertNotIn('data-i18n="monitoring.title">Monitoring', html_source)
        self.assertNotIn("Hardware usage status is updated every 5 seconds.", html_source)
        self.assertIn('"monitoring.title": ""', app_source)
        self.assertIn('"monitoring.subtitle": ""', app_source)
        self.assertIn('setOpsOverviewLivePolling(targetView === "monitoring")', app_source)
        self.assertIn("setInterval(pollOpsOverviewLive, REALTIME_POLL_INTERVAL_MS)", app_source)

    def test_network_header_copy_is_hidden_while_network_rendering_remains(self) -> None:
        root = Path.cwd()
        html_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertNotIn('id="networkStatusTitle">실시간 네트워크', html_source)
        self.assertNotIn("송신/수신 속도와 포트 정책, 손실 분석을 한 화면에서 확인합니다.", html_source)
        self.assertIn('class="network-heading-spacer" aria-hidden="true"', html_source)
        self.assertIn('"network.title": ""', app_source)
        self.assertIn('"network.subtitle": ""', app_source)
        self.assertIn("const networkSelectedNic", app_source)
        self.assertIn("function renderNetworkStatus", app_source)

    def test_dashboard_summary_uses_storage_snapshot_without_slow_powershell(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        (tmp_path / "state.json").write_text(json.dumps({"BAY-01": "ISOLATED"}), encoding="utf-8")
        (tmp_path / "veeam_auto_isolate.json").write_text(json.dumps({"slot_id": "BAY-01", "state": "ISOLATED"}), encoding="utf-8")
        (tmp_path / "storage-BAY-01.json").write_text(
            json.dumps(
                {
                    "diskNumber": 1,
                    "drive": "G",
                    "accessPath": "G:\\",
                    "isOffline": False,
                    "offlineEquivalent": True,
                    "pathReachable": False,
                }
            ),
            encoding="utf-8",
        )
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(config_path)
        handler.threat_detection_summary = lambda: {"summary": {"status": "정상", "score": 0, "last_scan_at": "-", "suspicious_count": 0}}

        with patch.object(webui.subprocess, "run", side_effect=AssertionError("PowerShell probe should not run")), patch.object(
            webui.LockFixWebHandler,
            "safe_text_lines",
            side_effect=AssertionError("Dashboard should read an audit tail, not the full audit log"),
        ):
            summary = handler.dashboard_summary()
            summary_cached = handler.dashboard_summary()
            summary_live = handler.dashboard_summary(live=True)

        self.assertEqual(summary["security_kpis"][2]["value"], "Offline")
        self.assertEqual(summary["alerts"][2]["value"], "Not visible")
        self.assertEqual(summary["backup"]["result"], "Offline Complete")
        self.assertFalse(summary["live_status"]["cache_hit"])
        self.assertTrue(summary_cached["live_status"]["cache_hit"])
        self.assertFalse(summary_live["live_status"]["cache_hit"])

    def test_dashboard_reload_deduplicates_slow_requests(self) -> None:
        app_source = (Path.cwd() / "web" / "static" / "app.js").read_text(encoding="utf-8")
        webui_source = (Path.cwd() / "webui.py").read_text(encoding="utf-8")

        self.assertIn("let dashboardReloadInFlight = null;", app_source)
        self.assertIn("if (dashboardReloadInFlight) return dashboardReloadInFlight;", app_source)
        self.assertIn('requestJson(live ? "/api/dashboard?live=1" : "/api/dashboard", { timeoutMs: 30000, live })', app_source)
        self.assertIn("if (latestDashboardData)", app_source)
        self.assertIn("DASHBOARD_CACHE_TTL_SECONDS = 0.8", webui_source)
        self.assertIn("DASHBOARD_PROBE_TIMEOUT_SECONDS = 1.2", webui_source)
        self.assertIn("SOURCES_CACHE_TTL_SECONDS = 0.8", webui_source)
        self.assertIn("SOURCE_INVENTORY_CACHE_TTL_SECONDS = 30.0", webui_source)
        self.assertIn("DETECT_CACHE_TTL_SECONDS = 2.0", webui_source)
        self.assertIn("VEEAM_DIAGNOSTICS_WAIT_BUFFER_SECONDS = 0.5", webui_source)
        self.assertIn("dashboard_cache_by_key", webui_source)
        self.assertIn("sources_cache_by_key", webui_source)
        self.assertIn("detect_cache_by_key", webui_source)
        self.assertIn('"generated_at": generated_at', webui_source)
        self.assertIn("def dashboard_summary(self, live: bool = False) -> dict:", webui_source)
        self.assertIn("def sources_summary(self, live: bool = False) -> dict:", webui_source)
        self.assertIn("def cached_integrated_source_inventory(self) -> dict:", webui_source)
        self.assertIn("def detect_summary(self, live: bool = False) -> dict:", webui_source)
        self.assertIn("def veeam_interlock_runtime(self, now: float, poll_api: bool = True) -> dict:", webui_source)
        self.assertIn("self.air_gap_summary(fast=True)", webui_source)
        self.assertIn("fast=isinstance(self, LockFixWebHandler)", webui_source)
        self.assertIn("if not live and cached", webui_source)
        self.assertIn('"cache_hit": True', webui_source)
        self.assertIn('"source_age_seconds": round(now_monotonic - cached[0], 3)', webui_source)
        self.assertIn('"cache_hit": False', webui_source)
        self.assertIn('live_request = (params.get("live") or [""])[0] == "1"', webui_source)
        self.assertIn("diagnostics_timeout + VEEAM_DIAGNOSTICS_WAIT_BUFFER_SECONDS", webui_source)
        self.assertIn("const REALTIME_POLL_INTERVAL_MS = 1000;", app_source)
        self.assertIn("dashboardPollTimer = setInterval(pollDashboardLive, REALTIME_POLL_INTERVAL_MS);", app_source)
        self.assertIn("let sourcesLiveInFlight = null;", app_source)
        self.assertIn("let opsOverviewLiveInFlight = null;", app_source)
        self.assertIn("let detectReloadInFlight = null;", app_source)
        self.assertIn("if (sourcesLiveInFlight) return sourcesLiveInFlight;", app_source)
        self.assertIn("if (opsOverviewLiveInFlight) return opsOverviewLiveInFlight;", app_source)
        self.assertIn('requestJson("/api/detect?live=1", { live: true, timeoutMs: 2500 })', app_source)
        self.assertIn("function reloadDetect(attempt = 0)", app_source)
        self.assertIn("reloadDetect(attempt + 1)", app_source)
        self.assertIn('function refreshAllInBackground(reason = "background refresh")', app_source)
        self.assertIn('refreshAllInBackground("session bootstrap");', app_source)
        self.assertIn('refreshAllInBackground("login bootstrap");', app_source)
        self.assertIn("요청 시간이 초과되었습니다. 최신 상태를 다시 확인 중입니다.", app_source)
        self.assertNotIn("WebUI 서버 응답이 지연되어 중단했습니다", app_source)
        self.assertNotIn("await loadAll();\n    showView(initialRouteView());", app_source)
        index_source = (Path.cwd() / "web" / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("20260520-sidebar-account-actions", index_source)
        self.assertIn('requestJson("/api/sources", { timeoutMs: 8000 })', app_source)
        self.assertNotIn('detect: requestJson("/api/detect")', app_source)
        self.assertIn("fetchOptions.cache = \"no-store\";", app_source)
        self.assertIn('headers.set("Cache-Control", "no-store");', app_source)
        self.assertIn("markLiveFailure(dashboardLiveState, error)", app_source)
        self.assertIn("copy.liveStale", app_source)
        self.assertIn("copy.liveError", app_source)
        self.assertIn("markLiveFailure(opsOverviewLiveState", app_source)
        self.assertIn("liveStateMeta(opsOverviewLiveState)", app_source)
        self.assertIn('self.send_header("Cache-Control", "no-store, max-age=0")', webui_source)
        self.assertIn("def audit_log_tail_lines", webui_source)
        self.assertIn("audit_log_tail_lines(self, limit=1000", webui_source)

    def test_dashboard_cards_drag_resize_without_edit_button(self) -> None:
        root = Path.cwd()
        html_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("dashboardPanelOrderKey", app_source)
        self.assertIn("dashboardPanelSizeKey", app_source)
        self.assertIn('const dashboardKpiSizeKey = "lockfix.dashboard.kpiSize.v4";', app_source)
        self.assertIn('const dashboardPanelOrderKey = "lockfix.dashboard.panelOrder.v2";', app_source)
        self.assertIn('const dashboardPanelSizeKey = "lockfix.dashboard.panelSize.v3";', app_source)
        self.assertIn("enableDashboardPanelDrag", app_source)
        self.assertIn("function clampDashboardPixels", app_source)
        self.assertIn("function dashboardResizeBounds", app_source)
        self.assertIn("function dashboardSpanFromPixels", app_source)
        self.assertIn("function dashboardRowsFromPixels", app_source)
        self.assertIn("dashboard-live-badge", app_source)
        self.assertIn("LIVE 1초", app_source)
        self.assertIn("function dashboardHealthValueClass(label, value)", app_source)
        self.assertIn("function dashboardAlertTarget(label, value)", app_source)
        self.assertIn("function bindDashboardAlertLinks()", app_source)
        self.assertIn('return "health-value-danger";', app_source)
        self.assertIn('return "health-value-ok";', app_source)
        self.assertIn('data-alert-target="${escapeHtml(target)}"', app_source)
        self.assertIn('showView(row.dataset.alertTarget || "monitoring")', app_source)
        self.assertIn('valueClass === "health-value-danger" ? "health-row health-row-danger" : "health-row"', app_source)
        self.assertIn(".health-value-danger", css_source)
        self.assertIn("color: #b91c1c !important;", css_source)
        self.assertIn(".health-row-danger", css_source)
        self.assertIn("box-shadow: inset 3px 0 0 #b91c1c;", css_source)
        self.assertIn(".health-value-ok", css_source)
        self.assertIn("20260520-alert-link-routing", html_source)
        self.assertNotIn('alerts.some((item) => String(item.value || "").match(/Failed|Detected|Error/i)) ? "확인 필요" : copy.noCritical', app_source)
        self.assertIn('class="dashboard-kpi-grip" draggable="true"', app_source)
        self.assertIn('class="dashboard-panel-grip" draggable="true"', app_source)
        self.assertIn('data-drag-axis="xy"', app_source)
        self.assertIn('data-drag-axis="y"', app_source)
        self.assertIn('title="Drag card up or down"', app_source)
        self.assertIn('data-dashboard-panel="events"', app_source)
        self.assertIn('data-dashboard-panel="alerts"', app_source)
        self.assertIn('data-dashboard-panel="audit"', app_source)
        self.assertIn('data-dashboard-panel="protection" data-panel-resizable="true"', app_source)
        self.assertIn('data-dashboard-panel="backup" data-panel-resizable="true"', app_source)
        self.assertIn('data-dashboard-panel="protection" data-panel-resizable="true" data-cols="12"', app_source)
        self.assertIn('data-dashboard-panel="backup" data-panel-resizable="true" data-cols="12" data-rows="2"', app_source)
        self.assertIn("const insertBefore = event.clientY < rect.top + rect.height / 2;", app_source)
        self.assertIn('data-panel-resizable="true"', app_source)
        self.assertNotIn('class="security-icon security-icon-${icon}"', app_source)
        self.assertNotIn('class="security-icon security-icon-${icon} security-tone-${tone}"', app_source)
        self.assertNotIn('panel-title-icon protection-title-icon', app_source)
        self.assertNotIn('panel-title-icon backup-title-icon', app_source)
        self.assertNotIn('panel-title-icon event-title-icon', app_source)
        self.assertNotIn('panel-title-icon alert-title-icon', app_source)
        self.assertNotIn('panel-title-icon audit-title-icon', app_source)
        self.assertIn("dashboard-kpi-resize-line-x", app_source)
        self.assertIn("dashboard-kpi-resize-line-y", app_source)
        self.assertIn("dashboard-panel-resize-line-x", app_source)
        self.assertIn("dashboard-panel-resize-line-y", app_source)
        self.assertIn('data-resize-axis="x"', app_source)
        self.assertIn('data-resize-axis="y"', app_source)
        self.assertIn("startWidth: card.getBoundingClientRect().width", app_source)
        self.assertIn("startHeight: card.getBoundingClientRect().height", app_source)
        self.assertIn("startWidth: panel.getBoundingClientRect().width", app_source)
        self.assertIn("startHeight: panel.getBoundingClientRect().height", app_source)
        self.assertIn("resizing.startWidth + dx", app_source)
        self.assertIn("resizing.startHeight + dy", app_source)
        self.assertIn("dashboardSpanFromPixels(board, nextWidth, 5, 1, 3)", app_source)
        self.assertIn("dashboardSpanFromPixels(board, nextWidth, 12, 3, 12)", app_source)
        self.assertIn("dashboardRowsFromPixels(nextHeight, 108, 1, 2)", app_source)
        self.assertIn("dashboardRowsFromPixels(nextHeight, 78, 1, 5)", app_source)
        self.assertIn("card.style.width = `${card.dataset.width}px`;", app_source)
        self.assertIn("card.style.height = `${card.dataset.height}px`;", app_source)
        self.assertIn("panel.style.width = `${panel.dataset.width}px`;", app_source)
        self.assertIn("panel.style.height = `${panel.dataset.height}px`;", app_source)
        self.assertNotIn("Math.round(dx / 120)", app_source)
        self.assertNotIn("Math.round(dy / 72)", app_source)
        self.assertNotIn("Math.round(dx / 140)", app_source)
        self.assertNotIn("Math.round(dy / 70)", app_source)
        self.assertNotIn("dashboard-kpi-resize-handle", app_source)
        self.assertNotIn("dashboard-panel-resize-handle", app_source)
        self.assertNotIn('data-resize-axis="both"', app_source)
        self.assertIn("dashboard-empty-row", app_source)
        self.assertIn("auditSummary", app_source)
        self.assertIn("audit-link-state", app_source)
        self.assertNotIn("dashboardEditToggle", app_source)
        self.assertNotIn("dashboard-edit-button", app_source)
        self.assertNotIn("편집 열기", app_source)
        self.assertIn(".dashboard-panel-grip", css_source)
        self.assertIn(".dashboard-live-badge", css_source)
        self.assertIn("box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.12);", css_source)
        self.assertNotIn(".dashboard-panel-resize-handle", css_source)
        self.assertNotIn(".dashboard-kpi-resize-handle", css_source)
        self.assertIn(".dashboard-kpi-resize-line-x", css_source)
        self.assertIn(".dashboard-kpi-resize-line-y", css_source)
        self.assertIn(".dashboard-panel-resize-line-x", css_source)
        self.assertIn(".dashboard-panel-resize-line-y", css_source)
        self.assertIn("cursor: ew-resize;", css_source)
        self.assertIn("cursor: ns-resize;", css_source)
        self.assertIn(".dashboard-panel-drop-target", css_source)
        self.assertIn(".security-kpi:hover .dashboard-kpi-grip", css_source)
        self.assertIn(".security-panel[data-dashboard-panel]:hover .dashboard-panel-resize-line", css_source)
        self.assertIn(".dashboard-kpi-board-resizing-x", css_source)
        self.assertIn(".dashboard-kpi-board-resizing-y", css_source)
        self.assertIn(".dashboard-panel-board-resizing-x", css_source)
        self.assertIn(".dashboard-panel-board-resizing-y", css_source)
        self.assertIn("event-panel-hidden", css_source)
        self.assertIn("min-height: 46px !important;", css_source)
        self.assertIn("const dashboardEventsVisible = true;", app_source)
        self.assertIn("const dashboardAlertsVisible = true;", app_source)
        self.assertNotIn('data-dashboard-reveal="events"', app_source)
        self.assertNotIn('data-dashboard-reveal="alerts"', app_source)
        self.assertNotIn("dashboard-reveal-button", app_source)
        self.assertNotIn("bindDashboardRevealToggles();", app_source)
        self.assertIn("function dashboardKpiDisplay", app_source)
        self.assertIn("function dashboardKpiTone", app_source)
        self.assertIn('normalized === "OFFLINE"', app_source)
        self.assertIn('normalized === "ISOLATED"', app_source)
        self.assertIn('["SUCCESS", "NORMAL", "OK", "OFFLINE_COMPLETE"].includes(normalized)', app_source)
        self.assertIn("ONLINE_VERIFIED_RW: \"검증 완료\"", app_source)
        self.assertIn("UNKNOWN: \"확인 중\"", app_source)
        self.assertIn('title="${escapeHtml(valueTitle)}"', app_source)
        self.assertIn('security-kpi-tone-${tone}', app_source)
        self.assertIn('data-tone="${escapeHtml(tone || "dark")}"', app_source)
        self.assertIn("grid-template-columns: repeat(5, minmax(0, 1fr));", css_source)
        self.assertIn("@media (max-width: 1360px)", css_source)
        self.assertIn("@media (max-width: 1360px) {\n  .security-kpi-grid {\n    grid-template-columns: repeat(5, minmax(0, 1fr));\n    gap: 10px;", css_source)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", css_source)
        self.assertIn("grid-auto-rows: minmax(108px, auto);", css_source)
        self.assertIn("white-space: nowrap;", css_source)
        self.assertIn("overflow-wrap: normal;", css_source)
        self.assertIn("border-left: 4px solid var(--kpi-tone);", css_source)
        self.assertIn(".security-kpi-tone-green", css_source)
        self.assertIn(".security-kpi-tone-orange", css_source)
        self.assertIn(".security-kpi-tone-red", css_source)
        self.assertIn(".security-kpi strong.security-value-green", css_source)
        self.assertIn(".security-kpi strong.security-value-red", css_source)
        self.assertIn("border-left-color: var(--kpi-tone);", css_source)
        self.assertIn(".security-value-orange", css_source)
        self.assertIn(".security-value-red", css_source)
        self.assertIn("color: #dc2626;", css_source)
        self.assertIn("color: #64748b;", css_source)
        self.assertIn("box-shadow: 0 5px 0 #52606d, 0 10px 0 #52606d;", css_source)
        self.assertIn("clip-path: polygon(50% 0, 100% 100%, 0 100%);", css_source)
        self.assertIn("background: #ffffff;", css_source)
        self.assertIn("opacity: 0.66;", css_source)
        self.assertIn("font-weight: 400", css_source)
        self.assertIn("20260520-sidebar-account-actions", html_source)
        self.assertIn("grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));", css_source)
        self.assertIn(".security-dashboard-grid .backup-panel .panel-body > dl", css_source)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr));", css_source)
        self.assertIn(".backup-panel .panel-body", css_source)
        self.assertIn("min-width: 0;", css_source)
        self.assertIn("justify-content: stretch;", css_source)
        self.assertIn("min-height: 54px;", css_source)
        self.assertIn("border: 1px solid #e1e9f2;", css_source)
        self.assertIn(".backup-panel dt,", css_source)
        self.assertIn("font-size: 12.5px;", css_source)
        self.assertIn("line-height: 1.45;", css_source)
        self.assertIn("grid-template-columns: 112px 1fr;", css_source)
        self.assertIn("font-size: 11.5px;", css_source)
        self.assertIn("font-size: 12px;", css_source)
        self.assertIn("width: 16px;", css_source)
        self.assertIn("height: 16px;", css_source)
        self.assertIn("border: 2px solid #52606d;", css_source)
        self.assertIn("font-size: 14.5px;", css_source)
        self.assertIn("font-size: 20px;", css_source)
        self.assertIn("function dashboardFlowLabel", app_source)
        self.assertIn("Backup Done", app_source)
        self.assertIn("I/O Check", app_source)
        self.assertIn("Unmount", app_source)
        self.assertIn("Offline", app_source)
        self.assertIn('class="flow-step-card ${state === "done" ? "flow-step-card-active" : ""}"', app_source)
        self.assertIn('class="flow-step-number"', app_source)
        self.assertIn('copy.protectedMessage.replace("Offline", "<b>Offline</b>")', app_source)
        self.assertIn("--flow-gap: clamp(28px, 4vw, 72px);", css_source)
        self.assertIn("grid-template-columns: repeat(5, minmax(154px, 1fr));", css_source)
        self.assertIn("width: 100%;", css_source)
        self.assertIn("max-width: none;", css_source)
        self.assertIn("word-break: keep-all;", css_source)
        self.assertIn(".emergency-access-copy p", css_source)
        self.assertIn("white-space: nowrap;", css_source)
        self.assertIn("20260521-hide-ops-events-panel", html_source)
        self.assertIn("justify-content: stretch;", css_source)
        self.assertIn("padding: 0 8px;", css_source)
        self.assertIn(".flow-step-card {", css_source)
        self.assertIn("min-height: 104px;", css_source)
        self.assertIn(".flow-step-card:not(:last-child)::after", css_source)
        self.assertIn("clip-path: polygon(0 28%, 66% 28%, 66% 0, 100% 50%, 66% 100%, 66% 72%, 0 72%);", css_source)
        self.assertIn(".flow-step-number {", css_source)
        self.assertIn("background: linear-gradient(180deg, #9fb3c8 0%, #7f97af 100%);", css_source)
        self.assertIn(".flow-step-card strong", css_source)
        self.assertIn("@media (max-width: 1180px)", css_source)
        self.assertIn("@media (max-width: 640px)", css_source)

    def test_dashboard_route_does_not_show_legacy_notification_markup(self) -> None:
        root = Path.cwd()
        html_source = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app_source = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css_source = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")
        dashboard_html = html_source.split('id="dashboardView"', 1)[1].split('id="legacyView"', 1)[0]

        self.assertNotIn("Security Notification Gateway", dashboard_html)
        self.assertNotIn("dashboardNotificationTable", dashboard_html)
        self.assertNotIn("dashboardLogsTable", dashboard_html)
        self.assertIn("dashboard-load-state", dashboard_html)
        self.assertIn("reloadDashboard", app_source)
        self.assertIn('if (targetView === "dashboard")', app_source)
        self.assertIn("renderDashboardFallback", app_source)
        self.assertIn("대시보드 데이터를 불러올 수 없습니다.", app_source)
        self.assertIn(".dashboard-load-error", css_source)
        self.assertIn("20260520-sidebar-account-actions", html_source)

    def test_dashboard_audit_summary_is_linked_to_audit_log(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit = AuditLogger(tmp_path / "audit.jsonl")
        audit.write("admin.manual_operation", actorUserId="admin")
        audit.write("policy.change.requested", actorUserId="admin")
        audit.write("approval.request.created", actorUserId="backup-operator", approvalRequestId="req-1")
        audit.write("auth.login.failed", actorUserId="unknown", result="FAILED")
        handler = webui.LockFixWebHandler.__new__(webui.LockFixWebHandler)
        handler.context = webui.WebContext(config_path)
        handler.notification_items = lambda: []
        handler.threat_detection_summary = lambda: {"summary": {"status": "정상", "score": 0, "last_scan_at": "-", "suspicious_count": 0}}

        summary = handler.dashboard_summary()["audit_summary"]

        self.assertTrue(summary["linked"])
        self.assertGreaterEqual(summary["total_records"], 4)
        self.assertEqual(summary["manual_operations"], 1)
        self.assertEqual(summary["policy_changes"], 1)
        self.assertEqual(summary["approval_requests"], 1)
        self.assertEqual(summary["login_failures"], 1)
        self.assertNotEqual(summary["latest_at"], "-")

    def test_admin_update_script_can_apply_live_operation_mode(self) -> None:
        source = (Path.cwd() / "tools" / "apply_latest_webui_update_admin.ps1").read_text(encoding="utf-8")

        self.assertIn('[ValidateSet("simulation", "live")]', source)
        self.assertIn('[string]$OperationMode = "live"', source)
        self.assertIn('$props["operation_mode"] = $OperationMode', source)
        self.assertIn('$props["dry_run"] = if ($OperationMode -eq "live") { "false" } else { "true" }', source)
        self.assertIn("Set-ObjectProperty -Object $config -Name dry_run -Value $effectiveDryRun", source)
        self.assertIn('"lockfix\\command.py"', source)

    def test_readme_documents_rbac_approval_audit_automation(self) -> None:
        source = (Path.cwd() / "README.md").read_text(encoding="utf-8")

        self.assertIn("RBAC, Approval, and Audit Automation", source)
        self.assertIn("migrations/001_lockfix_rbac_approval_audit.sql", source)
        self.assertIn("The request creator cannot approve their own request.", source)
        self.assertIn("Emergency unlock requires a reason, dual approval, and audit logging.", source)
        self.assertIn("Repository Online workflow", source)
        self.assertIn("Collaboration workflow menu", source)
        self.assertIn("Department collaboration workflow", source)
        self.assertIn("ApprovalRequest.reviewDepartments", source)
        self.assertIn("DepartmentReview statuses", source)
        self.assertIn("GET /api/approval-requests/:id/reviews", source)
        self.assertIn("협업/승인 워크플로우", source)

    def test_web_ui_rbac_menu_and_direct_access_guards_are_present(self) -> None:
        root = Path.cwd()
        html = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        server = (root / "webui.py").read_text(encoding="utf-8")

        for label in [
            "Dashboard",
            "Hardware Detect",
            "Air-Gap",
            "Reports",
            "License",
            "Settings",
            "Logout",
            "Operation",
            "Hardware",
            "User & Role",
            "Audit Logs",
        ]:
            self.assertIn(label, html)

        self.assertNotIn("Air-Gap Policy", html)
        self.assertNotIn("Veeam Integration</span>", html)

        self.assertIn("menuDefinitions", app)
        self.assertIn('roles: ["SUPER_ADMIN"]', app)
        self.assertIn("visibleMenuDefinitions", app)
        self.assertIn("canAccessView", app)
        self.assertIn("showAccessDenied", app)
        self.assertIn("accessDeniedView", html)
        self.assertIn("window.addEventListener(\"hashchange\"", app)
        self.assertIn('"permissions": self.current_permissions()', server)
        self.assertIn("permissions_for_role", server)
        self.assertIn("/api/approval-requests/([^/]+)/reviews", server)
        self.assertIn("comment|mark-reviewed|needs-changes|block", server)

    def test_web_ui_approval_tabs_and_button_visibility_are_testable(self) -> None:
        root = Path.cwd()
        html = (root / "web" / "static" / "index.html").read_text(encoding="utf-8")
        app = (root / "web" / "static" / "app.js").read_text(encoding="utf-8")
        css = (root / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertNotIn('id="approvalsView"', html)
        self.assertNotIn("협업/승인 워크플로우", html)
        self.assertNotIn('data-settings-view="approvals"', html)
        self.assertNotIn('view: "approvals"', app)
        self.assertNotIn('showView("approvals")', app)
        self.assertNotIn('settingsApprovalStatus', app)
        self.assertNotIn('update(requestJson("/api/approvals")', app)
        self.assertIn("approvalDecisionSummary", app)
        self.assertIn("repositoryOnlineWorkflowSummary", app)
        self.assertIn("departmentReviewsFor", app)
        self.assertIn("departmentReviewStatus", app)
        self.assertIn("departmentReviewSummary", app)
        self.assertIn("renderRepositoryOnlineRequestPanel", app)
        self.assertIn("renderFinalApprovalPanel", app)
        self.assertIn("[최종 승인 대기]", app)
        self.assertIn("승인 상태:", app)
        self.assertIn("승인 완료", app)
        self.assertIn("data-reject-id", app)
        self.assertIn('decision: "REJECTED"', app)
        self.assertIn("[Repository Online 요청]", app)
        self.assertIn("백업 검증을 위해 Repository Online 필요", app)
        self.assertIn("□", app)
        self.assertIn("보안팀", app)
        self.assertIn("하드웨어팀", app)
        self.assertIn("부서 검토 진행 중", app)
        self.assertIn("pendingDepartmentReviewsForSession", app)
        self.assertIn("data-department-review-id", app)
        self.assertIn("data-review-action", app)
        self.assertIn("/api/approval-requests/", app)
        self.assertIn("approval-review-state", css)
        self.assertIn("repository-online-request-card", css)
        self.assertIn("final-approval-wait-card", css)
        self.assertIn("rbac-danger-action", css)
        self.assertIn("workflowHistoryItems", app)
        self.assertIn("renderWorkflowHistory", app)
        self.assertIn("canShowReviewButton", app)
        self.assertIn('data-review-id', app)
        self.assertIn("approvalRequestBox", app)
        self.assertIn("departmentReviewBox", app)
        self.assertIn("myApprovalPending", app)
        self.assertIn("approvalWorkflowStages", app)
        self.assertIn("renderApprovalWorkflowPipeline", app)
        self.assertIn("completedHistory", app)
        self.assertIn("auditRecord", app)
        self.assertIn("workflow-history-list", css)
        self.assertIn("canShowApprovalButton", app)
        self.assertIn('`${approved} / ${required} approved`', app)
        self.assertIn('hasPermission("DISK_ONLINE_APPROVE"', app)
        self.assertIn("request.allowedApproverRoles.includes(session.role)", app)
        self.assertIn('request.requesterUserId || "") === String(session.user || "")', app)
        self.assertIn("data-approval-id", app)
        self.assertIn("window.lockfixUiAuth", app)

    def test_airgap_detail_log_area_scrolls_inside_blue_left_border(self) -> None:
        css = (Path.cwd() / "web" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn(".veeam-log-wrap", css)
        self.assertIn("box-sizing: border-box;", css)
        self.assertIn("min-height: 132px;", css)
        self.assertIn("max-height: 300px;", css)
        self.assertIn("border: 1px solid #c8d8ea;", css)
        self.assertIn("direction: ltr;", css)
        self.assertIn("overflow-x: auto;", css)
        self.assertIn("overflow-y: auto;", css)
        self.assertIn("overscroll-behavior: contain;", css)
        self.assertIn("scrollbar-width: thin;", css)
        self.assertIn("scrollbar-color: #aeb7c3 #f1f5f9;", css)
        self.assertIn(".veeam-log-wrap:hover", css)
        self.assertIn("scrollbar-color: #7f8a98 #f1f5f9;", css)
        self.assertIn(".veeam-log-wrap::-webkit-scrollbar-button", css)
        self.assertIn(".veeam-log-wrap::-webkit-scrollbar-track-piece", css)
        self.assertIn(".veeam-log-wrap::-webkit-scrollbar-corner", css)
        self.assertIn("min-height: 112px;", css)
        self.assertIn("border: 3px solid #f1f5f9;", css)
        self.assertIn("background-clip: padding-box;", css)
        self.assertIn("background: #aeb7c3;", css)
        self.assertIn("background: #7f8a98;", css)
        self.assertIn("background: #697586;", css)
        self.assertIn(".veeam-log-wrap:hover::-webkit-scrollbar-thumb", css)
        self.assertIn("position: sticky;", css)

    def test_airgap_monitoring_heading_has_no_underline(self) -> None:
        source = (Path.cwd() / "web" / "static" / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".veeam-monitoring-panel h2", source)
        self.assertIn("border-bottom: 0;", source)
        self.assertIn(".veeam-log-meta span", source)
        self.assertIn("overflow-wrap: anywhere;", source)
        self.assertNotIn("margin: -31px 12px 18px 0;", source)

    def test_veeam_client_from_config_and_get_backup_status(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "username": "administrator",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
            "job_name": "Agent_backup",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        config = load_config(config_path)

        with patch.dict("os.environ", {"LOCKFIX_TEST_VEEAM_PASSWORD": "secret"}, clear=False):
            client = VeeamClient.from_config(config.veeam)

        with patch.object(client, "latest_session_summary", return_value={"api_synced": True}) as summary:
            result = client.get_backup_status()

        summary.assert_called_once_with("Agent_backup", "")
        self.assertTrue(result["api_synced"])
        self.assertEqual(client.settings.username, "administrator")
        self.assertEqual(client.settings.password, "secret")

    def test_veeam_username_env_and_password_env_are_supported(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "username_env": "LOCKFIX_TEST_VEEAM_USER",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        with patch.dict(
            "os.environ",
            {"LOCKFIX_TEST_VEEAM_USER": "env-user", "LOCKFIX_TEST_VEEAM_PASSWORD": "secret"},
            clear=False,
        ):
            config = load_config(config_path)
            client = VeeamClient.from_config(config.veeam)
            helper_client = create_veeam_client(
                {
                    "username_env": "LOCKFIX_TEST_VEEAM_USER",
                    "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
                    "base_url": "https://127.0.0.1:9419",
                }
            )

        self.assertEqual(config.veeam.username_env, "LOCKFIX_TEST_VEEAM_USER")
        self.assertEqual(client.settings.username, "env-user")
        self.assertEqual(client.settings.password, "secret")
        self.assertEqual(helper_client.settings.username, "env-user")
        self.assertEqual(helper_client.settings.password, "secret")

    def test_veeam_login_reports_missing_username_or_password_env(self) -> None:
        missing_user = VeeamClient(VeeamSettings(username="", password="secret"))
        with self.assertRaisesRegex(VeeamAuthenticationError, "username is not configured"):
            missing_user.login()

        missing_password = VeeamClient(
            VeeamSettings(username="administrator", password="", password_env="LOCKFIX_MISSING_PASSWORD")
        )
        with self.assertRaisesRegex(VeeamAuthenticationError, "LOCKFIX_MISSING_PASSWORD"):
            missing_password.login()

        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "Veeam username is not configured"):
                create_veeam_client({"password_env": "LOCKFIX_MISSING_PASSWORD"})
            with self.assertRaisesRegex(ValueError, "LOCKFIX_MISSING_PASSWORD"):
                create_veeam_client({"username": "administrator", "password_env": "LOCKFIX_MISSING_PASSWORD"})

    def test_backup_copy_match_uses_non_c_target_repository(self) -> None:
        repositories = [
            {"id": "repo-c", "name": "CREPO", "repository": {"path": "C:\\backup"}},
            {"id": "repo-d", "name": "DREPO", "repository": {"path": "D:\\copy"}},
        ]
        backups = [
            {"id": "source-backup", "name": "Agent_backup - 192.168.219.102", "repositoryId": "repo-c"},
            {"id": "copy-backup", "name": "Backup Copy Job 2", "repositoryId": "repo-d"},
        ]

        eligible = filter_target_repositories(repositories, target_name="DREPO", target_path="D:\\copy")
        match = match_backups(backups, job_name="Agent_backup", eligible_repositories=eligible)
        restore_point = {
            "id": "restore-point-1",
            "sessionId": "session-1",
            "creationTime": "2026-05-01T07:00:00+09:00",
            "_backup": match["matches"][0],
            "_repository": eligible[0],
        }
        summary = restore_point_summary(restore_point)

        self.assertEqual(match["strategy"], "target_repository_backup_copy")
        self.assertEqual(match["matches"][0]["id"], "copy-backup")
        self.assertEqual(summary["repository_path"], "D:\\copy")
        self.assertEqual(summary["current_step"], 2)

    def test_backup_copy_job_id_priority_records_restore_point_scope(self) -> None:
        repositories = [
            {"id": "repo-d", "name": "DREPO", "repository": {"path": "D:\\copy"}},
        ]
        backups = [
            {
                "id": "copy-backup",
                "name": "Backup Copy Job 2",
                "jobId": "a61d20b5-2555-4635-ab65-86b6fc2bf449",
                "policyUniqueId": "a61d20b5-2555-4635-ab65-86b6fc2bf449",
                "repositoryId": "repo-d",
            }
        ]

        eligible = filter_target_repositories(repositories, target_id="repo-d")
        match = match_backups(
            backups,
            job_name="Agent_backup",
            job_id="a61d20b5-2555-4635-ab65-86b6fc2bf449",
            eligible_repositories=eligible,
        )
        restore_point = {
            "id": "restore-point-1",
            "sessionId": "session-1",
            "creationTime": "2026-05-01T07:00:00+09:00",
            "_backup": match["matches"][0],
            "_backup_object": {"id": "object-1", "name": "192.168.219.102"},
            "_repository": eligible[0],
            "_configured_job_name": "Agent_backup",
            "_configured_job_id": "a61d20b5-2555-4635-ab65-86b6fc2bf449",
            "_backup_match_strategy": match["strategy"],
        }
        summary = restore_point_summary(restore_point)

        self.assertEqual(match["strategy"], "backup_job_id")
        self.assertEqual(summary["job_id"], "a61d20b5-2555-4635-ab65-86b6fc2bf449")
        self.assertEqual(summary["backup_match_strategy"], "backup_job_id")

    def test_latest_backup_restore_point_auto_discovers_backup_copy_when_config_filter_is_stale(self) -> None:
        client = VeeamClient(
            VeeamSettings(
                username="administrator",
                password="secret",
                job_name="Backup Copy Job 1",
                target_repository_id="old-repo",
                target_repository_name="G",
                target_repository_path="G:\\",
                require_backup_copy=True,
            )
        )
        repositories = [
            {"id": "repo-d", "name": "DREPO", "repository": {"path": "D:\\copy"}},
        ]
        backups = [
            {"id": "copy-backup", "name": "Backup Copy Job 2", "repositoryId": "repo-d"},
        ]
        restore_points = [
            {"id": "restore-point-1", "sessionId": "session-1", "creationTime": "2026-05-16T07:00:00+09:00"},
        ]

        with patch.object(client, "get_backups", return_value=backups):
            with patch.object(client, "get_repositories", return_value=repositories):
                with patch.object(client, "get_backup_objects", return_value=[{"id": "object-1", "name": "192.168.219.102"}]):
                    with patch.object(client, "get_restore_points", return_value=restore_points):
                        restore_point = client.latest_backup_restore_point()

        self.assertIsNotNone(restore_point)
        self.assertEqual(restore_point["_backup"]["id"], "copy-backup")
        self.assertEqual(restore_point["_backup_match_strategy"], "auto_discovered_backup_copy")
        summary = restore_point_summary(restore_point)
        self.assertEqual(summary["restore_point_scope"]["backup_id"], "copy-backup")
        self.assertEqual(summary["restore_point_scope"]["repository_id"], "repo-d")

    def test_veeam_console_log_fallback_reads_latest_backup_copy_time(self) -> None:
        root = self.make_workspace() / "logs"
        job_dir = root / "Backup_Copy_Job_2" / "Agent_backup"
        job_dir.mkdir(parents=True)
        (job_dir / "Job.Agent_backup.log").write_text(
            "\n".join(
                [
                    "[04.05.2026 12:48:53.381]    Info    [JobSession] Update session [parent-1] CreationTime: 2026-05-04 오후 12:48:53",
                    "[04.05.2026 12:48:53.893]    Info    JobId=a61d20b5-2555-4635-ab65-86b6fc2bf449, JobName=Backup Copy Job 2",
                    "[04.05.2026 12:49:16.269]    Info    Job session 'parent-worker' has been completed, status: 'Success', '0 B' of '0 B' bytes",
                    "[04.05.2026 12:49:16.298]    Info    [JobSession] Update session [parent-1] EndTime: 2026-05-04 오후 12:49:16",
                ]
            ),
            encoding="utf-8",
        )
        (job_dir / "Job.192.168.219.102.BackupSync.log").write_text(
            "\n".join(
                [
                    "[04.05.2026 12:48:57.726]    Info    [Session] Id 'child-1', State 'Working'.",
                    "[04.05.2026 12:48:59.767]    Info    [JobSession] Set new totals: TotalObjects '1', TotalSize '479 GB'",
                    "[04.05.2026 12:49:00.543]    Info    [CSimpleCopyPointAlg] Creating incremental point",
                    "[04.05.2026 12:49:05.826]    Info    Job session 'child-1' has been completed, status: 'Success', '0 B' of '0 B' bytes",
                ]
            ),
            encoding="utf-8",
        )

        summary = latest_backup_copy_console_log_summary(
            log_root=str(root),
            backup_copy_name="Backup Copy Job 2",
            job_name="Agent_backup",
            target_name="192.168.219.102",
            policy_job_id="a61d20b5-2555-4635-ab65-86b6fc2bf449",
            repository_id="repo-d",
            repository_name="DREPO",
            repository_path="D:\\copy",
        )

        self.assertEqual(summary["started_at"], "2026-05-04 12:48:57")
        self.assertEqual(summary["ended_at"], "2026-05-04 12:49:05")
        self.assertEqual(summary["job_finished_at"], "2026-05-04 12:49:16")
        self.assertEqual(summary["duration"], "00:08")
        self.assertEqual(summary["backup_size"], "479 GB")
        self.assertEqual(summary["transferred"], "0 B")
        self.assertEqual(summary["session_id"], "child-1")

    def test_veeam_console_log_fallback_reads_parent_realtime_progress(self) -> None:
        root = self.make_workspace() / "logs"
        job_dir = root / "Backup_Copy_Job_1" / "Agent_backup"
        job_dir.mkdir(parents=True)
        (job_dir / "Job.Agent_backup.log").write_text(
            "\n".join(
                [
                    "[10.05.2026 11:13:41.484]    Info    [Session] Id 'parent-1', State 'Working'.",
                    "[10.05.2026 11:13:43.893]    Info    JobId=7cda3ae9-317b-4952-990e-428f7801342f, JobName=Backup Copy Job 1",
                    "[10.05.2026 11:13:44.560]    Info    [JobSession] Set new totals: TotalObjects '1', TotalSize '479 GB'",
                    "[10.05.2026 11:14:08.360]    Info    Job progress: '50%', '257,698,037,760' of '514,319,187,968' bytes, '0' of '0' used bytes, object '0' of '1', totals calculated: No",
                ]
            ),
            encoding="utf-8",
        )
        (job_dir / "Job.192.168.219.102.BackupSync.log").write_text(
            "\n".join(
                [
                    "[10.05.2026 11:13:44.995]    Info    [Session] Id 'child-1', State 'Working'.",
                    "[10.05.2026 11:13:51.364]    Info    [JobSession] Set new totals: TotalObjects '1', TotalSize '479 GB'",
                ]
            ),
            encoding="utf-8",
        )

        summary = latest_backup_copy_console_log_summary(
            log_root=str(root),
            backup_copy_name="Backup Copy Job 1",
            job_name="Agent_backup",
            target_name="192.168.219.102",
            policy_job_id="7cda3ae9-317b-4952-990e-428f7801342f",
            repository_id="repo-d",
            repository_name="DREPO",
            repository_path="D:\\Backup",
        )

        self.assertEqual(summary["progress_percent"], 50)
        self.assertEqual(summary["transferred"], "240.0 GB")
        self.assertEqual(summary["backup_size"], "479.0 GB")
        self.assertIn("progress 50%", "\n".join(summary["session_logs"][0]["actions"]))

    def test_veeam_session_summary_keeps_realtime_progress_size_and_time(self) -> None:
        session = {
            "id": "session-1",
            "name": "Agent_backup",
            "state": "Working",
            "creationTime": "2026-05-01T07:00:00+09:00",
            "progressPercent": 23,
        }
        logs = [
            {
                "title": "Agent_backup - 192.168.219.102 processing",
                "status": "Running",
                "startTime": "2026-05-01T07:00:00+09:00",
                "updateTime": "2026-05-01T07:00:05+09:00",
            }
        ]
        tasks = [
            {
                "name": "Agent_backup - 192.168.219.102",
                "status": "Running",
                "progressPercent": 42,
                "totalBytes": 1024 * 1024 * 1024,
                "transferredBytes": 512 * 1024 * 1024,
                "transferSpeed": 1024 * 1024,
            }
        ]

        summary = enrich_summary_with_logs(session_summary(session), logs, tasks)

        self.assertEqual(summary["progress_percent"], 42)
        self.assertEqual(summary["backup_size"], "1.0 GB")
        self.assertEqual(summary["transferred"], "512.0 MB")
        self.assertEqual(summary["speed"], "1.0 MB/s")
        self.assertIn("512.0 MB / 1.0 GB", "\n".join(summary["session_logs"][0]["actions"]))

    def test_veeam_session_summary_reads_nested_realtime_metrics(self) -> None:
        session = {
            "id": "session-1",
            "name": "Agent_backup",
            "state": "Working",
            "creationTime": "2026-05-01T07:00:00+09:00",
            "endTime": "2026-05-01T07:00:08+09:00",
            "statistics": {
                "progress": "0%",
                "totalBytes": 479 * 1024 * 1024 * 1024,
                "transferredBytes": 0,
                "transferSpeed": "0 KB/s",
            },
        }

        summary = session_summary(session)

        self.assertEqual(summary["progress_percent"], 0)
        self.assertEqual(summary["backup_size"], "479.0 GB")
        self.assertEqual(summary["transferred"], "0 B")
        self.assertEqual(summary["speed"], "0 KB/s")
        self.assertEqual(summary["duration"], "00:08")

    def test_veeam_restore_point_logs_supply_size_and_duration(self) -> None:
        summary = restore_point_summary(
            {
                "id": "restore-point-1",
                "sessionId": "session-1",
                "creationTime": "2026-05-01T07:00:00+09:00",
                "_backup": {"name": "Backup Copy Job 2"},
                "_repository": {"name": "DREPO", "repository": {"path": "D:\\copy"}},
            }
        )
        logs = [
            {
                "status": "Succeeded",
                "title": "Total size: 11.3 GB",
                "startTime": "2026-05-01T07:00:00+09:00",
                "updateTime": "2026-05-01T07:00:00+09:00",
            },
            {
                "status": "Succeeded",
                "title": "Job finished at 2026-05-01 07:00:08",
                "startTime": "2026-05-01T07:00:08+09:00",
                "updateTime": "2026-05-01T07:00:08+09:00",
            },
        ]

        enriched = enrich_summary_with_logs(summary, logs, [])

        self.assertEqual(enriched["backup_size"], "11.3 GB")
        self.assertEqual(enriched["duration"], "00:08")
        self.assertIn("Total size: 11.3 GB", "\n".join(enriched["session_logs"][0]["actions"]))

    def test_veeam_restore_point_console_lines_use_session_log_time(self) -> None:
        summary = restore_point_summary(
            {
                "id": "restore-point-1",
                "sessionId": "session-1",
                "creationTime": "2026-05-01T06:59:58+09:00",
                "_backup": {"name": "Backup Copy Job 2"},
                "_backup_object": {"name": "192.168.219.102"},
                "_repository": {"name": "DREPO", "repository": {"path": "D:\\copy"}},
                "_configured_job_name": "Agent_backup",
            }
        )
        logs = [
            {
                "status": "Succeeded",
                "title": "Job started at 2026-05-01 오전 7:00:01",
                "startTime": "2026-05-01T07:00:01+09:00",
                "updateTime": "2026-05-01T07:00:01+09:00",
            },
            {
                "status": "Succeeded",
                "title": "Job finished at 2026-05-01 오전 7:01:10",
                "startTime": "2026-05-01T07:01:10+09:00",
                "updateTime": "2026-05-01T07:01:10+09:00",
            },
        ]

        enriched = enrich_summary_with_logs(summary, logs, [])
        actions = "\n".join(enriched["session_logs"][0]["actions"])

        self.assertIn("Backup copy for Agent_backup - 192.168.219.102 started at 2026-05-01 07:00:01", actions)
        self.assertIn("Agent_backup - 192.168.219.102 (0 B) processing finished at 2026-05-01 07:01:10", actions)
        self.assertIn("Succeeded - Job started at 2026-05-01 07:00:01", actions)
        self.assertNotIn("06:59:58", actions)
        self.assertNotIn(" 오전 ", actions)

    def test_webui_veeam_backup_uses_context_config(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "base_url": "https://192.168.219.230:9419",
            "enterprise_manager_url": "https://127.0.0.1:9398",
            "api_version": "1.2-rev1",
            "username": "administrator",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
            "verify_ssl": False,
            "job_name": "Agent_backup",
            "require_backup_copy": True,
            "target_repository_name": "DREPO",
            "target_repository_path": "D:\\copy",
            "exclude_os_repository": True,
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return False

        def fake_diagnostics(config, controller):
            veeam_config = config.veeam
            return {
                "latest_configured_session": {
                    "api_synced": True,
                    "job": veeam_config.job_name,
                    "job_id": veeam_config.job_id,
                    "status": "Success",
                    "progress_percent": 100,
                    "current_step": 2,
                    "repository_name": veeam_config.target_repository_name,
                    "repository_path": veeam_config.target_repository_path,
                }
            }

        with patch.dict("os.environ", {"LOCKFIX_TEST_VEEAM_PASSWORD": "secret"}, clear=False):
            with patch.object(webui, "run_veeam_diagnostics", fake_diagnostics):
                result = webui.LockFixWebHandler.poll_veeam_api(Probe(), "127.0.0.1", 9419, {})

        self.assertTrue(result["api_synced"])
        self.assertEqual(result["job"], "Agent_backup")
        self.assertEqual(result["current_step"], 2)
        self.assertEqual(result["server"], "192.168.219.230")
        self.assertEqual(result["port"], 9419)
        self.assertEqual(result["repository_name"], "DREPO")
        self.assertEqual(result["repository_path"], "D:\\copy")

    def test_webui_loads_veeam_password_from_install_properties_into_process_env(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "username_env": "LOCKFIX_TEST_VEEAM_USER",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
            "base_url": "https://127.0.0.1:9419",
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {
                    "veeam_user": "administrator",
                    "veeam_password": "secret",
                    "veeam_base_url": "https://192.168.219.230:9419",
                    "veeam_api_version": "1.2-rev1",
                }

        with patch.dict("os.environ", {}, clear=True):
            webui.LockFixWebHandler.prepare_veeam_process_environment(
                Probe(),
                Probe.context.app_config.get("veeam", {}),
            )
            self.assertEqual(os.environ["LOCKFIX_TEST_VEEAM_USER"], "administrator")
            self.assertEqual(os.environ["LOCKFIX_TEST_VEEAM_PASSWORD"], "secret")
            self.assertEqual(os.environ["LOCKFIX_VEEAM_BASE_URL"], "https://192.168.219.230:9419")

    def test_create_veeam_client_prefers_runtime_endpoint_over_stale_config(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "LOCKFIX_TEST_VEEAM_PASSWORD": "secret",
                "LOCKFIX_VEEAM_BASE_URL": "https://192.168.219.230:9419",
                "LOCKFIX_VEEAM_API_VERSION": "1.2-rev1",
            },
            clear=True,
        ):
            client = create_veeam_client(
                {
                    "base_url": "https://192.168.219.165:9419",
                    "username": "administrator",
                    "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
                }
            )

        self.assertEqual(client.settings.base_url, "https://192.168.219.230:9419")

    def test_webui_veeam_backup_returns_error_without_stale_success(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {"job_name": "Agent_backup"}
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return False

            def poll_veeam_api(self, server, port, local_payload):
                return webui.LockFixWebHandler.poll_veeam_api(self, server, port, local_payload)

        stale_path = webui.ROOT / "runtime" / "veeam_interlock_state.json"
        stale_path.parent.mkdir(parents=True, exist_ok=True)
        old_value = stale_path.read_text(encoding="utf-8") if stale_path.exists() else None
        stale_path.write_text(
            json.dumps({"api_synced": True, "status": "Success", "progress_percent": 100, "current_step": 5}),
            encoding="utf-8",
        )
        try:
            with patch.object(webui, "run_veeam_diagnostics", side_effect=RuntimeError("configured Veeam check failed")):
                result = webui.LockFixWebHandler.veeam_interlock_runtime(Probe(), 0)
        finally:
            if old_value is None:
                stale_path.unlink(missing_ok=True)
            else:
                stale_path.write_text(old_value, encoding="utf-8")

        self.assertFalse(result["api_synced"])
        self.assertEqual(result["progress_percent"], 0)
        self.assertEqual(result["current_step"], 1)
        self.assertEqual(result["state_source"], "veeam_rest_api_error")
        self.assertEqual(result["step_logs"][0]["state"], "PENDING")
        self.assertFalse(result["step_logs"][0]["transition_allowed"])
        self.assertEqual(result["step_logs"][0]["progress_percent"], "")
        self.assertIn("configured Veeam check failed", result["session_logs"][0]["actions"][0])

    def test_webui_promotes_finished_veeam_log_to_100_percent(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {"job_name": "Agent_backup"}
        config_path.write_text(json.dumps(raw), encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return True

            def poll_veeam_api(self, server, port, local_payload):
                return {
                    "api_synced": True,
                    "job": "Backup Copy Job 1",
                    "status": "Running",
                    "result": "Running",
                    "progress_percent": 99,
                    "current_step": 1,
                    "started_at": "2026-05-10 16:45:57",
                    "ended_at": "-",
                    "session_logs": [
                        {
                            "name": "Backup Copy Job 1",
                            "status": "Running",
                            "actions": [
                                "Backup Copy Job 1 - 192.168.219.102 (Incremental) (479.0 GB) is running: 479.0 GB transferred, progress 99%",
                                "Job finished at 2026-05-10 16:46:16",
                            ],
                            "progress_percent": 99,
                        }
                    ],
                }

        result = webui.LockFixWebHandler.veeam_interlock_runtime(Probe(), 0)

        self.assertEqual(result["progress_percent"], 100)
        self.assertEqual(result["payload"]["progress_percent"], 100)
        self.assertEqual(result["session_logs"][0]["progress_percent"], 100)
        self.assertEqual(result["session_logs"][0]["status"], "Success")

    def test_webui_keeps_last_veeam_detail_logs_when_api_waits(self) -> None:
        class Probe:
            pass

        path = webui.ROOT / "runtime" / "veeam_last_session_logs.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        old_value = path.read_text(encoding="utf-8") if path.exists() else None
        log = {
            "name": "Agent_backup",
            "status": "Success",
            "actions": ["Agent_backup processing finished at 2026-05-01T07:00:08+09:00"],
            "duration": "00:08",
            "progress_percent": 100,
            "backup_size": "479.0 GB",
            "transferred": "0 B",
            "speed": "0 KB/s",
        }
        try:
            webui.LockFixWebHandler.save_veeam_last_logs(Probe(), [log], "2026-05-01 07:00:09")
            logs = webui.LockFixWebHandler.load_veeam_last_logs(Probe())
        finally:
            if old_value is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(old_value, encoding="utf-8")

        self.assertEqual(logs[0]["name"], "Agent_backup")
        self.assertTrue(logs[0]["last_known"])
        self.assertEqual(logs[0]["backup_size"], "479.0 GB")
        self.assertIn("Last retained Veeam detail log", logs[0]["actions"][-1])

    def test_webui_auto_isolate_uses_context_controller(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)

        class Probe:
            context = webui.WebContext(config_path)

        self.approve_operation(Probe.context.controller, "DISK_OFFLINE")
        marker_path = webui.ROOT / "runtime" / "veeam_auto_isolate.json"
        old_value = marker_path.read_text(encoding="utf-8") if marker_path.exists() else None
        payload = {
            "slot_id": "BAY-01",
            "session_id": uuid.uuid4().hex,
            "job": "Agent_backup",
            "result": "Success",
            "progress_percent": 100,
            "started_at": "2026-05-01 09:59:50",
            "ended_at": "2026-05-01 10:00:00",
            "session_logs": [
                {
                    "name": "Agent_backup",
                    "status": "Success",
                    "ended_at": "2026-05-01 10:00:00",
                    "progress_percent": 100,
                    "actions": ["Agent_backup processing finished at 2026-05-01 10:00:00"],
                }
            ],
        }
        try:
            result = webui.LockFixWebHandler.auto_isolate_after_veeam_success(Probe(), payload, "Success", "2026-05-01 10:00:00")
            final_marker = {}
            for _ in range(60):
                if marker_path.exists():
                    final_marker = json.loads(marker_path.read_text(encoding="utf-8"))
                    if final_marker.get("state") in {"ISOLATED", "FAILED"}:
                        break
                time.sleep(0.1)
        finally:
            if old_value is None:
                marker_path.unlink(missing_ok=True)
            else:
                marker_path.write_text(old_value, encoding="utf-8")

        self.assertTrue(result["triggered"])
        self.assertEqual(result["state"], "IN_PROGRESS")
        self.assertEqual(final_marker.get("state"), "ISOLATED")

    def test_webui_auto_isolate_recovers_stale_in_progress_marker(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)

        class Probe:
            context = webui.WebContext(config_path)

        marker_path = webui.ROOT / "runtime" / "veeam_auto_isolate.json"
        old_value = marker_path.read_text(encoding="utf-8") if marker_path.exists() else None
        payload = {
            "slot_id": "BAY-01",
            "session_id": uuid.uuid4().hex,
            "job": "Agent_backup",
            "result": "Success",
            "progress_percent": 100,
            "started_at": "2026-05-01 09:59:50",
            "ended_at": "2026-05-01 10:00:00",
            "session_logs": [
                {
                    "name": "Agent_backup",
                    "status": "Success",
                    "ended_at": "2026-05-01 10:00:00",
                    "progress_percent": 100,
                    "actions": ["Agent_backup processing finished at 2026-05-01 10:00:00"],
                }
            ],
        }
        session_key, _ = webui.LockFixWebHandler.veeam_auto_isolate_identity(Probe(), payload)
        stale_started_at = (datetime.now() - timedelta(seconds=webui.AIRGAP_AUTO_ISOLATE_STALE_SECONDS + 30)).isoformat(timespec="seconds")
        try:
            marker_path.parent.mkdir(parents=True, exist_ok=True)
            marker_path.write_text(
                json.dumps(
                    {
                        "session_key": session_key,
                        "processed_session_keys": [],
                        "slot_id": "BAY-01",
                        "state": "IN_PROGRESS",
                        "checked_at": "2026-05-01 10:00:00",
                        "started_at": stale_started_at,
                    }
                ),
                encoding="utf-8",
            )
            result = webui.LockFixWebHandler.auto_isolate_after_veeam_success(Probe(), payload, "Success", "2026-05-01 10:00:00")
            final_marker = {}
            for _ in range(60):
                final_marker = json.loads(marker_path.read_text(encoding="utf-8"))
                if final_marker.get("state") in {"ISOLATED", "FAILED"}:
                    break
                time.sleep(0.1)
            audit_text = load_config(config_path).audit_log_path.read_text(encoding="utf-8")
        finally:
            if old_value is None:
                marker_path.unlink(missing_ok=True)
            else:
                marker_path.write_text(old_value, encoding="utf-8")

        self.assertTrue(result["triggered"])
        self.assertEqual(result["state"], "IN_PROGRESS")
        self.assertEqual(final_marker.get("state"), "ISOLATED")
        self.assertIn('"event": "veeam.auto_isolate.in_progress.recovered"', audit_text)

    def test_webui_airgap_holds_flush_until_veeam_end_time_is_reached(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return True

            def save_veeam_last_logs(self, session_logs, checked_at):
                return None

            def poll_veeam_api(self, server, port, local_payload):
                return {
                    "api_synced": True,
                    "server": "192.168.219.230",
                    "port": 9419,
                    "job": "Agent_backup",
                    "status": "Success",
                    "result": "Success",
                    "progress_percent": 100,
                    "current_step": 2,
                    "slot_id": "BAY-01",
                    "started_at": "2026-05-19 00:44:32",
                    "ended_at": "2026-05-19 00:44:42",
                    "session_logs": [
                        {
                            "name": "Agent_backup",
                            "status": "Success",
                            "ended_at": "2026-05-19 00:44:42",
                            "progress_percent": 100,
                            "actions": [
                                "Backup copy for Agent_backup - 192.168.219.102 started at 2026-05-19 00:44:32",
                                "Agent_backup - 192.168.219.102 (Incremental) (479 GB) is running: 0 B transferred at -, progress 0%",
                            ],
                            "duration": "00:10",
                        }
                    ],
                }

        checked_before_veeam_end = datetime(2026, 5, 19, 0, 44, 40).timestamp()
        result = webui.LockFixWebHandler.veeam_interlock_runtime(Probe(), checked_before_veeam_end)
        actions = "\n".join(result["session_logs"][0]["actions"])

        self.assertEqual(result["current_step"], 1)
        self.assertEqual(result["progress_percent"], 0)
        self.assertEqual(result["step_logs"][1]["state"], "PENDING")
        self.assertFalse(result["step_logs"][1]["transition_allowed"])
        self.assertFalse(result["auto_isolate"]["triggered"])
        self.assertIn("completion is not confirmed", result["auto_isolate"]["message"])
        self.assertNotIn("LOCK-FIX STEP 2 DETAIL", actions)

    def test_webui_airgap_step2_appends_flush_audit_logs_after_veeam_logs(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {
                "ts": "2026-05-04T12:00:01+00:00",
                "event": "disk.flush.start",
                "slot_id": "BAY-01",
                "mount_point": "D:\\copy",
                "device": "D:\\",
            },
            {
                "ts": "2026-05-04T12:00:02+00:00",
                "event": "disk.flush.tick",
                "slot_id": "BAY-01",
                "elapsed_seconds": 1,
                "mount_point": "D:\\copy",
            },
            {
                "ts": "2026-05-04T12:00:03+00:00",
                "event": "disk.flush",
                "slot_id": "BAY-01",
                "output": "Windows Server flush checkpoint completed",
            },
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return True

            def poll_veeam_api(self, server, port, local_payload):
                return {
                    "api_synced": True,
                    "server": "192.168.219.230",
                    "port": 9419,
                    "job": "Agent_backup",
                    "status": "Running",
                    "result": "Running",
                    "progress_percent": 25,
                    "current_step": 2,
                    "slot_id": "BAY-01",
                    "started_at": "2026-05-04 21:10:37",
                    "ended_at": "2026-05-04 21:10:48",
                    "session_logs": [
                        {
                            "name": "Agent_backup",
                            "status": "Running",
                            "ended_at": "2026-05-04 21:10:48",
                            "actions": [
                                "Backup copy for Agent_backup - 192.168.219.102 started at 2026-05-04 21:10:37",
                                "Agent_backup - 192.168.219.102 (0 B) processing finished at 2026-05-04 21:10:48",
                            ],
                            "duration": "-",
                        }
                    ],
                }

        result = webui.LockFixWebHandler.veeam_interlock_runtime(Probe(), 0)
        actions = result["session_logs"][0]["actions"]

        self.assertEqual(actions[0], "Backup copy for Agent_backup - 192.168.219.102 started at 2026-05-04 21:10:37")
        self.assertTrue(any("LOCK-FIX STEP 2 DETAIL" in item for item in actions))
        self.assertGreater(actions.index(next(item for item in actions if "LOCK-FIX Flush GUARD OK" in item)), 0)
        self.assertTrue(any("LOCK-FIX Flush TARGET" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Flush COMMAND" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Flush MONITOR" in item for item in actions))
        self.assertGreater(actions.index(next(item for item in actions if "LOCK-FIX Flush START" in item)), 0)
        self.assertTrue(any("LOCK-FIX Flush TICK 1s" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Flush OK" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 2 COMPLETE" in item for item in actions))

    def test_webui_airgap_step3_appends_io_quiet_logs_after_flush_logs(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {"ts": "2026-05-04T12:00:01+00:00", "event": "disk.flush.start", "slot_id": "BAY-01", "mount_point": "D:\\copy", "device": "D:\\"},
            {"ts": "2026-05-04T12:00:02+00:00", "event": "disk.flush.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:03+00:00", "event": "disk.flush", "slot_id": "BAY-01", "output": "Windows Server flush checkpoint completed"},
            {"ts": "2026-05-04T12:00:04+00:00", "event": "disk.io_quiet.start", "slot_id": "BAY-01", "seconds": 3, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:05+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "remaining_seconds": 2, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:06+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 2, "remaining_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:07+00:00", "event": "disk.io_quiet", "slot_id": "BAY-01", "seconds": 3},
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return True

            def poll_veeam_api(self, server, port, local_payload):
                return {
                    "api_synced": True,
                    "server": "192.168.219.230",
                    "port": 9419,
                    "job": "Agent_backup",
                    "status": "Running",
                    "result": "Running",
                    "progress_percent": 50,
                    "current_step": 3,
                    "slot_id": "BAY-01",
                    "started_at": "2026-05-04 21:10:37",
                    "ended_at": "2026-05-04 21:10:48",
                    "session_logs": [
                        {
                            "name": "Agent_backup",
                            "status": "Running",
                            "ended_at": "2026-05-04 21:10:48",
                            "actions": [
                                "Backup copy for Agent_backup - 192.168.219.102 started at 2026-05-04 21:10:37",
                                "Agent_backup - 192.168.219.102 (0 B) processing finished at 2026-05-04 21:10:48",
                            ],
                            "duration": "-",
                        }
                    ],
                }

        result = webui.LockFixWebHandler.veeam_interlock_runtime(Probe(), 0)
        actions = result["session_logs"][0]["actions"]
        flush_ok_index = actions.index(next(item for item in actions if "LOCK-FIX Flush OK" in item))
        io_start_index = actions.index(next(item for item in actions if "LOCK-FIX I/O Check START" in item))

        self.assertGreater(io_start_index, flush_ok_index)
        self.assertTrue(any("LOCK-FIX STEP 3 DETAIL" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check WINDOW" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check MONITOR" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check GATE" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check TICK 1s" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check TICK 2s" in item for item in actions))
        self.assertTrue(any("LOCK-FIX I/O Check OK" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 3 COMPLETE" in item for item in actions))

    def test_webui_airgap_step3_deduplicates_overlapping_io_ticks(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {"ts": "2026-05-04T12:00:01+00:00", "event": "disk.io_quiet.start", "slot_id": "BAY-01", "seconds": 3, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:02+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 2, "remaining_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:03+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "remaining_seconds": 2, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:04+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 2, "remaining_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:05+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 3, "remaining_seconds": 0, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:06+00:00", "event": "disk.io_quiet.dry_run", "slot_id": "BAY-01", "seconds": 3},
            {"ts": "2026-05-04T12:00:07+00:00", "event": "disk.io_quiet.dry_run", "slot_id": "BAY-01", "seconds": 3},
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

        actions = webui.LockFixWebHandler.veeam_io_quiet_operation_actions(Probe(), "BAY-01", 3)

        self.assertEqual(len([item for item in actions if "I/O Check TICK 2s" in item]), 1)
        self.assertLess(
            actions.index(next(item for item in actions if "I/O Check TICK 1s" in item)),
            actions.index(next(item for item in actions if "I/O Check TICK 3s" in item)),
        )
        self.assertEqual(len([item for item in actions if "I/O Check OK" in item]), 1)

    def test_webui_airgap_step4_and_step5_logs_follow_previous_flow(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {"ts": "2026-05-04T12:00:01+00:00", "event": "disk.flush.start", "slot_id": "BAY-01", "mount_point": "D:\\copy", "device": "D:\\"},
            {"ts": "2026-05-04T12:00:02+00:00", "event": "disk.flush.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:03+00:00", "event": "disk.flush", "slot_id": "BAY-01", "output": "Windows Server flush checkpoint completed"},
            {"ts": "2026-05-04T12:00:04+00:00", "event": "disk.io_quiet.start", "slot_id": "BAY-01", "seconds": 3, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:05+00:00", "event": "disk.io_quiet.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "remaining_seconds": 2, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:06+00:00", "event": "disk.io_quiet", "slot_id": "BAY-01", "seconds": 3},
            {"ts": "2026-05-04T12:00:07+00:00", "event": "disk.unmount.start", "slot_id": "BAY-01", "mount_point": "D:\\copy", "device": "D:\\", "drive_letter": "D", "os_volume_protected": True},
            {"ts": "2026-05-04T12:00:08+00:00", "event": "disk.unmount.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "mount_point": "D:\\copy"},
            {"ts": "2026-05-04T12:00:09+00:00", "event": "disk.unmount", "slot_id": "BAY-01", "output": "Dismount-Volume completed"},
            {"ts": "2026-05-04T12:00:10+00:00", "event": "power.mock.off.start", "slot_id": "BAY-01"},
            {"ts": "2026-05-04T12:00:11+00:00", "event": "power.mock.off.tick", "slot_id": "BAY-01", "elapsed_seconds": 1},
            {"ts": "2026-05-04T12:00:12+00:00", "event": "power.mock.off", "slot_id": "BAY-01"},
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_install_properties(self):
                return {}

            def tcp_port_open(self, host, port, timeout=0.25):
                return True

            def poll_veeam_api(self, server, port, local_payload):
                return {
                    "api_synced": True,
                    "server": "192.168.219.230",
                    "port": 9419,
                    "job": "Agent_backup",
                    "status": "Running",
                    "result": "Running",
                    "progress_percent": 75,
                    "current_step": 5,
                    "slot_id": "BAY-01",
                    "started_at": "2026-05-04 21:10:37",
                    "ended_at": "2026-05-04 21:10:48",
                    "session_logs": [
                        {
                            "name": "Agent_backup",
                            "status": "Running",
                            "ended_at": "2026-05-04 21:10:48",
                            "actions": [
                                "Backup copy for Agent_backup - 192.168.219.102 started at 2026-05-04 21:10:37",
                                "Agent_backup - 192.168.219.102 (0 B) processing finished at 2026-05-04 21:10:48",
                            ],
                            "duration": "-",
                        }
                    ],
                }

        result = webui.LockFixWebHandler.veeam_interlock_runtime(Probe(), 0)
        actions = result["session_logs"][0]["actions"]
        step2_index = actions.index(next(item for item in actions if "LOCK-FIX STEP 2 COMPLETE" in item))
        step3_index = actions.index(next(item for item in actions if "LOCK-FIX STEP 3 COMPLETE" in item))
        step4_index = actions.index(next(item for item in actions if "LOCK-FIX STEP 4 DETAIL" in item))
        step5_index = actions.index(next(item for item in actions if "LOCK-FIX STEP 5 DETAIL" in item))

        self.assertLess(step2_index, step3_index)
        self.assertLess(step3_index, step4_index)
        self.assertLess(step4_index, step5_index)
        self.assertTrue(any("LOCK-FIX Unmount GUARD OK" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Unmount COMMAND" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Unmount OK" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 4 COMPLETE" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 4 HISTORY - Unmount detailed audit trail is retained" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 4 HISTORY DETAIL - slot BAY-01, result OK, records 3" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 4 HISTORY EVENTS - disk.unmount.start, disk.unmount.tick, disk.unmount" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Power OFF TARGET" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Power OFF OK" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 5 COMPLETE" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 5 HISTORY - Power OFF detailed audit trail is retained" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 5 HISTORY DETAIL - slot BAY-01, result OK, records 3" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 5 HISTORY EVENTS - power.mock.off.start, power.mock.off.tick, power.mock.off" in item for item in actions))

    def test_webui_airgap_step5_logs_power_status_proof_requirement(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {"ts": "2026-05-04T12:00:10+00:00", "event": "power.command.off.start", "slot_id": "BAY-01", "command": ["powershell", "-File", "lockfix_power_control.ps1"]},
            {"ts": "2026-05-04T12:00:11+00:00", "event": "power.command.off.tick", "slot_id": "BAY-01", "elapsed_seconds": 1},
            {"ts": "2026-05-04T12:00:12+00:00", "event": "power.command.off", "slot_id": "BAY-01", "output": "OFF command completed"},
            {
                "ts": "2026-05-04T12:00:13+00:00",
                "event": "power.command.status.missing",
                "slot_id": "BAY-01",
                "requirement": "Configure power.status_command or LOCKFIX_POWER_<SLOT>_STATUS_URL/LOCKFIX_POWER_<SLOT>_STATUS_EXE.",
            },
            {
                "ts": "2026-05-04T12:00:14+00:00",
                "event": "power.off.proof.required",
                "slot_id": "BAY-01",
                "reason": "power.status_command is not configured",
                "required_config": "power.status_command or LOCKFIX_POWER_<SLOT>_STATUS_URL/LOCKFIX_POWER_<SLOT>_STATUS_EXE",
            },
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

        actions = webui.LockFixWebHandler.veeam_power_off_operation_actions(Probe(), "BAY-01", 5)

        self.assertTrue(any("LOCK-FIX Power OFF PROOF REQUIRED - actual OFF proof requires a PDU/relay/storage controller status response" in item for item in actions))
        self.assertTrue(any("LOCK-FIX Power OFF PROOF REQUIRED - power.status_command is not configured" in item for item in actions))
        self.assertTrue(any("LOCK-FIX STEP 5 HISTORY EVENTS - power.command.off.start, power.command.off.tick, power.command.off, power.command.status.missing, power.off.proof.required" in item for item in actions))

    def test_webui_airgap_flush_logs_keep_only_latest_flush_cycle(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        audit_path = load_config(config_path).audit_log_path
        audit_records = [
            {"ts": "2026-05-04T11:00:01+00:00", "event": "disk.flush.start", "slot_id": "BAY-01", "mount_point": "D:\\old", "device": "D:\\"},
            {"ts": "2026-05-04T11:00:02+00:00", "event": "disk.flush", "slot_id": "BAY-01", "output": "old flush"},
            {"ts": "2026-05-04T12:00:01+00:00", "event": "disk.flush.start", "slot_id": "BAY-01", "mount_point": "D:\\new", "device": "D:\\"},
            {"ts": "2026-05-04T12:00:02+00:00", "event": "disk.flush.tick", "slot_id": "BAY-01", "elapsed_seconds": 1, "mount_point": "D:\\new"},
            {"ts": "2026-05-04T12:00:03+00:00", "event": "disk.flush", "slot_id": "BAY-01", "output": "new flush"},
        ]
        audit_path.write_text("\n".join(json.dumps(item) for item in audit_records) + "\n", encoding="utf-8")

        class Probe:
            context = webui.WebContext(config_path)

        actions = webui.LockFixWebHandler.veeam_flush_operation_actions(Probe(), "BAY-01", 2)

        self.assertEqual(len(actions), 9)
        self.assertNotIn("old flush", "\n".join(actions))
        self.assertIn("new flush", "\n".join(actions))

    def test_webui_veeam_backup_exposes_same_diagnostics_as_veeam_test(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {"enabled": True, "job_name": "Agent_backup"}
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        expected = {
            "source": "python_veeam_client",
            "diagnostics": {
                "vbr_rest_9419": {"port": {"ok": True, "code": "OK"}},
                "authentication": {"ok": True, "token_received": True, "password_logged": False},
                "jobs": {"ok": True, "count": 0, "items": []},
                "sessions": {"ok": True, "count": 16, "items": []},
                "matching": {"job_id": "", "job_name": "Agent_backup", "strategy": "backup_restore_point", "matched": True},
            },
            "api": {
                "source": "python_veeam_client",
                "jobs": {"ok": True, "count": 0},
                "sessions": {"ok": True, "count": 16},
                "matching": {"job_id": "", "job_name": "Agent_backup", "strategy": "backup_restore_point", "matched": True},
            },
        }

        class Probe:
            context = webui.WebContext(config_path)

            def veeam_interlock_runtime(self, now):
                return {
                    "server": "127.0.0.1",
                    "port": 9419,
                    "connected": True,
                    "api_synced": True,
                    "port_open": True,
                    "api_checks": {},
                    "last_checked": "2026-05-01 10:00:00",
                    "state_source": "veeam_rest_api",
                    "message": "ok",
                    "current_step": 2,
                    "job": "Agent_backup",
                    "progress_percent": 100,
                    "payload": {"status": "Success", "progress_percent": 100},
                    "step_logs": [
                        {"time": "2026-05-01 10:00:00", "transition_allowed": True, "step": 1, "code": "BACKUP_COMPLETED", "detail": "ok", "source": "test"},
                        {"time": "2026-05-01 10:00:00", "transition_allowed": True, "step": 2, "code": "FLUSHING", "detail": "ok", "source": "test"},
                    ],
                    "session_logs": [],
                    "auto_isolate": {},
                }

        with patch.object(webui, "run_veeam_diagnostics", return_value=expected):
            result = webui.LockFixWebHandler.veeam_backup_summary(Probe())

        self.assertEqual(result["diagnostics"]["vbr_rest_9419"], expected["diagnostics"]["vbr_rest_9419"])
        self.assertEqual(result["diagnostics"]["authentication"], expected["diagnostics"]["authentication"])
        self.assertEqual(result["diagnostics"]["jobs"]["count"], expected["diagnostics"]["jobs"]["count"])
        self.assertEqual(result["diagnostics"]["sessions"]["count"], expected["diagnostics"]["sessions"]["count"])
        self.assertEqual(result["diagnostics"]["matching"], expected["diagnostics"]["matching"])
        self.assertEqual(result["api"]["jobs"]["count"], expected["api"]["jobs"]["count"])
        self.assertEqual(result["api"]["sessions"]["count"], expected["api"]["sessions"]["count"])
        self.assertEqual(result["api"]["matching"], expected["api"]["matching"])
        self.assertEqual(result["api"]["source"], "python_veeam_client")
        self.assertEqual(result["source"], "python_veeam_client")

    def test_veeam_watcher_runs_jobs_sessions_match_status_then_isolate(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        raw["veeam"] = {
            "enabled": True,
            "username": "administrator",
            "password_env": "LOCKFIX_TEST_VEEAM_PASSWORD",
            "job_id": "job-123",
            "job_name": "Agent_backup",
            "isolate_on_status": ["Success"],
        }
        config_path.write_text(json.dumps(raw), encoding="utf-8")
        config = load_config(config_path)
        controller = LockFixController(config)
        self.approve_operation(controller, "DISK_OFFLINE")

        diagnostics = {
            "success": True,
            "source": "python_veeam_client",
            "matching": {"strategy": "job_id", "matched": True},
            "latest_configured_session": {"repository_path": "F:\\BackupCopyRepo"},
            "isolate_condition": {
                "watcher_enabled": True,
                "matched_session": True,
                "session_id": "session-123",
                "job_name": "Agent_backup",
                "job_id": "job-123",
                "status": "Success",
                "status_allowed": True,
                "already_processed": False,
                "would_call_isolate": True,
            },
            "pre_isolate_checks": {"ready": True},
        }
        with patch.dict("os.environ", {"LOCKFIX_TEST_VEEAM_PASSWORD": "secret"}, clear=False):
            watcher = VeeamWatcher(config, controller, state_path=tmp_path / "veeam_watcher_state.json")
            with patch("lockfix.veeam_watcher.run_veeam_diagnostics", return_value=diagnostics):
                result = watcher.poll_once(slot_id="BAY-01")

        self.assertEqual(result["action"], "isolated")
        self.assertEqual(result["session_id"], "session-123")
        self.assertEqual(result["repository_path"], "F:\\BackupCopyRepo")
        self.assertEqual(controller.status()["BAY-01"], "ISOLATED")

    def test_veeam_webui_test_does_not_launch_process_when_8088_is_closed(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        config = load_config(config_path)
        controller = LockFixController(config)

        with patch(
            "lockfix.veeam_webui_check.run_veeam_diagnostics",
            return_value={"config": {"base_url": "https://127.0.0.1:9419"}, "latest_configured_session": {}},
        ):
            with patch(
                "lockfix.veeam_webui_check.fetch_webui_veeam_backup",
                side_effect=WebUiServerNotRunning("connection refused"),
            ) as fetch:
                result = compare_veeam_test_with_webui(config, controller)

        fetch.assert_called_once()
        self.assertFalse(result["process_launch_attempted"])
        self.assertFalse(result["webui"]["running"])
        self.assertEqual(result["webui"]["message"], "Web UI server is not running")
        self.assertIn("not treated as a Veeam REST integration failure", result["comparison"]["message"])

    def test_veeam_webui_test_keeps_http_error_separate_from_not_running(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        config = load_config(config_path)
        controller = LockFixController(config)

        with patch(
            "lockfix.veeam_webui_check.run_veeam_diagnostics",
            return_value={"config": {"base_url": "https://127.0.0.1:9419"}, "latest_configured_session": {}},
        ):
            with patch(
                "lockfix.veeam_webui_check.fetch_webui_veeam_backup",
                side_effect=HTTPError("http://127.0.0.1:8088/api/veeam-backup", 500, "Internal Server Error", {}, None),
            ):
                result = compare_veeam_test_with_webui(config, controller)

        self.assertFalse(result["process_launch_attempted"])
        self.assertTrue(result["webui"]["running"])
        self.assertEqual(result["webui"]["message"], "Web UI HTTP check failed")
        self.assertIn("separate from Veeam REST 9419 validation", result["comparison"]["message"])

    def test_veeam_webui_test_compares_http_response_with_veeam_test(self) -> None:
        tmp_path = self.make_workspace()
        config_path = write_config(tmp_path)
        config = load_config(config_path)
        controller = LockFixController(config)
        veeam_test_payload = {
            "config": {
                "base_url": "https://127.0.0.1:9419",
                "api_version": "1.2-rev1",
                "verify_ssl": False,
                "job_name": "Agent_backup",
                "job_id": "",
            },
            "authentication": {"ok": True},
            "jobs": {"ok": True, "count": 0},
            "sessions": {"ok": True, "count": 16},
            "matching": {"matched": True, "strategy": "backup_restore_point"},
            "latest_configured_session": {
                "source": "python_veeam_client",
                "name": "Agent_backup",
                "status": "Success",
                "result": "Success",
                "duration": "00:09",
            },
            "vbr_rest_9419": {"port": {"ok": True}},
        }
        webui_payload = {
            "source": "python_veeam_client",
            "api": {
                "source": "python_veeam_client",
                "base_url": "https://127.0.0.1:9419",
                "api_version": "1.2-rev1",
                "verify_ssl": False,
                "token": {"ok": True},
                "jobs": {"ok": True, "count": 0},
                "sessions": {"ok": True, "count": 16},
                "matching": {"matched": True, "strategy": "backup_restore_point"},
                "job_name": "Agent_backup",
                "job_id": "",
            },
            "job": {"name": "Agent_backup", "result": "Success", "duration": "00:09"},
        }

        with patch("lockfix.veeam_webui_check.run_veeam_diagnostics", return_value=veeam_test_payload):
            with patch("lockfix.veeam_webui_check.fetch_webui_veeam_backup", return_value=webui_payload):
                result = compare_veeam_test_with_webui(config, controller)

        self.assertTrue(result["webui"]["running"])
        self.assertTrue(result["webui"]["ok"])
        self.assertTrue(result["comparison"]["ok"])
        self.assertTrue(all(result["comparison"]["matches"].values()))
        self.assertEqual(summarize_webui_backup(webui_payload)["source"], "python_veeam_client")

if __name__ == "__main__":
    unittest.main()
