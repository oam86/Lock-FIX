from __future__ import annotations

from .audit import AuditLogger
from .command import CommandRunner
from .config import PowerConfig


class PowerController:
    def off(self, slot_id: str) -> None:
        raise NotImplementedError

    def on(self, slot_id: str) -> None:
        raise NotImplementedError

    def status(self, slot_id: str) -> dict[str, object]:
        raise NotImplementedError


class MockPowerController(PowerController):
    def __init__(self, audit: AuditLogger) -> None:
        self.audit = audit

    def off(self, slot_id: str) -> None:
        self.audit.write("power.mock.off.start", slot_id=slot_id)
        self.audit.write("power.mock.off.tick", slot_id=slot_id, elapsed_seconds=1)
        self.audit.write("power.mock.off", slot_id=slot_id)

    def on(self, slot_id: str) -> None:
        self.audit.write("power.mock.on.start", slot_id=slot_id)
        self.audit.write("power.mock.on.tick", slot_id=slot_id, elapsed_seconds=1)
        self.audit.write("power.mock.on", slot_id=slot_id)

    def status(self, slot_id: str) -> dict[str, object]:
        result = {
            "mode": "mock",
            "provable": False,
            "ok": None,
            "state": "UNKNOWN",
            "reason": "mock power controller cannot prove physical power state",
            "requirement": "Use a PDU, relay, or storage controller status response to prove physical OFF.",
        }
        self.audit.write("power.mock.status", slot_id=slot_id, **result)
        return result


class CommandPowerController(PowerController):
    def __init__(self, runner: CommandRunner, config: PowerConfig, audit: AuditLogger) -> None:
        self.runner = runner
        self.config = config
        self.audit = audit

    def off(self, slot_id: str) -> None:
        self.audit.write("power.command.off.start", slot_id=slot_id, command=self.config.off_command)
        try:
            output = self.runner.run(self.config.off_command)
        except Exception as exc:
            self.audit.write("power.command.off.error", slot_id=slot_id, command=self.config.off_command, error=str(exc))
            raise
        self.audit.write("power.command.off.tick", slot_id=slot_id, elapsed_seconds=1)
        self.audit.write("power.command.off", slot_id=slot_id, output=output)

    def on(self, slot_id: str) -> None:
        self.audit.write("power.command.on.start", slot_id=slot_id, command=self.config.on_command)
        try:
            output = self.runner.run(self.config.on_command)
        except Exception as exc:
            self.audit.write("power.command.on.error", slot_id=slot_id, command=self.config.on_command, error=str(exc))
            raise
        self.audit.write("power.command.on.tick", slot_id=slot_id, elapsed_seconds=1)
        self.audit.write("power.command.on", slot_id=slot_id, output=output)

    def status(self, slot_id: str) -> dict[str, object]:
        if not self.config.status_command:
            result = {
                "mode": "command",
                "provable": False,
                "ok": None,
                "state": "UNKNOWN",
                "reason": "power.status_command is not configured",
                "requirement": "Configure power.status_command or LOCKFIX_POWER_<SLOT>_STATUS_URL/LOCKFIX_POWER_<SLOT>_STATUS_EXE.",
            }
            self.audit.write("power.command.status.missing", slot_id=slot_id, **result)
            return result
        self.audit.write("power.command.status.start", slot_id=slot_id, command=self.config.status_command)
        try:
            output = self.runner.run(self.config.status_command, timeout=30)
        except Exception as exc:
            result = {
                "mode": "command",
                "provable": True,
                "ok": False,
                "state": "ERROR",
                "error": str(exc),
            }
            self.audit.write("power.command.status.error", slot_id=slot_id, command=self.config.status_command, error=str(exc))
            return result

        normalized_output = str(output or "").strip().lower()
        expected = [value for value in self.config.off_status_values if value]
        off_confirmed = any(value in normalized_output for value in expected)
        result = {
            "mode": "command",
            "provable": True,
            "ok": off_confirmed,
            "state": "OFF" if off_confirmed else "NOT_OFF",
            "expected": expected,
            "output": output,
        }
        self.audit.write("power.command.status", slot_id=slot_id, **result)
        return result


def build_power_controller(
    runner: CommandRunner,
    config: PowerConfig,
    audit: AuditLogger,
) -> PowerController:
    if config.type == "mock":
        return MockPowerController(audit)
    if config.type == "command":
        return CommandPowerController(runner, config, audit)
    raise ValueError(f"unsupported power controller: {config.type}")
