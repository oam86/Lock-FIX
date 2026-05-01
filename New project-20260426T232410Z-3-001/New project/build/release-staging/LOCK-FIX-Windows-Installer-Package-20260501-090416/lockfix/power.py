from __future__ import annotations

from .audit import AuditLogger
from .command import CommandRunner
from .config import PowerConfig


class PowerController:
    def off(self, slot_id: str) -> None:
        raise NotImplementedError

    def on(self, slot_id: str) -> None:
        raise NotImplementedError


class MockPowerController(PowerController):
    def __init__(self, audit: AuditLogger) -> None:
        self.audit = audit

    def off(self, slot_id: str) -> None:
        self.audit.write("power.mock.off", slot_id=slot_id)

    def on(self, slot_id: str) -> None:
        self.audit.write("power.mock.on", slot_id=slot_id)


class CommandPowerController(PowerController):
    def __init__(self, runner: CommandRunner, config: PowerConfig, audit: AuditLogger) -> None:
        self.runner = runner
        self.config = config
        self.audit = audit

    def off(self, slot_id: str) -> None:
        output = self.runner.run(self.config.off_command)
        self.audit.write("power.command.off", slot_id=slot_id, output=output)

    def on(self, slot_id: str) -> None:
        output = self.runner.run(self.config.on_command)
        self.audit.write("power.command.on", slot_id=slot_id, output=output)


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
