from __future__ import annotations

from ctypes import addressof, byref, c_char_p, c_uint, c_void_p, cdll, create_string_buffer, memmove
from ctypes import Structure
import hmac
import hashlib
import os
from pathlib import Path
import secrets
import sqlite3
import sys
from typing import Any


class DATA_BLOB(Structure):
    _fields_ = [("cbData", c_uint), ("pbData", c_void_p)]


class LockFixSecureStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.key_path = self.db_path.with_suffix(".key.dpapi")
        self._secret = self.load_or_create_secret()
        self.initialize()

    @classmethod
    def from_runtime(cls, runtime_dir: Path) -> "LockFixSecureStore":
        configured = os.getenv("LOCKFIX_DB_PATH", "").strip()
        db_path = Path(configured) if configured else runtime_dir / "lockfix.db"
        return cls(db_path)

    def initialize(self) -> None:
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA busy_timeout=5000")
            db.execute("PRAGMA foreign_keys=ON")
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS disk_identity (
                    slot_id TEXT PRIMARY KEY,
                    disk_unique_id TEXT,
                    serial TEXT,
                    model TEXT,
                    wwn TEXT,
                    expected_hash_hmac TEXT NOT NULL,
                    access_path TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS emergency_access_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slot_id TEXT NOT NULL,
                    event TEXT NOT NULL,
                    result TEXT NOT NULL,
                    hash_hmac TEXT,
                    access_path TEXT,
                    disk_number TEXT,
                    partition_number TEXT,
                    message TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path, timeout=5)
        db.row_factory = sqlite3.Row
        return db

    def hash_hmac(self, value: str) -> str:
        return hmac.new(self._secret, str(value or "").encode("utf-8"), hashlib.sha256).hexdigest()

    def remember_disk_hash(
        self,
        *,
        slot_id: str,
        expected_hash: str,
        identity: dict[str, str],
        access_path: str,
        storage_state: dict[str, Any],
    ) -> str:
        digest = self.hash_hmac(expected_hash)
        with self.connect() as db:
            db.execute(
                """
                INSERT INTO disk_identity (
                    slot_id, disk_unique_id, serial, model, wwn, expected_hash_hmac, access_path
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slot_id) DO UPDATE SET
                    disk_unique_id=excluded.disk_unique_id,
                    serial=excluded.serial,
                    model=excluded.model,
                    wwn=excluded.wwn,
                    expected_hash_hmac=excluded.expected_hash_hmac,
                    access_path=excluded.access_path,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    slot_id,
                    str(storage_state.get("diskUniqueId") or identity.get("unique_id") or ""),
                    str(identity.get("serial") or ""),
                    str(identity.get("model") or ""),
                    str(identity.get("wwn") or ""),
                    digest,
                    access_path,
                ),
            )
        return digest

    def stored_hash_hmac(self, slot_id: str) -> str:
        with self.connect() as db:
            row = db.execute(
                "SELECT expected_hash_hmac FROM disk_identity WHERE slot_id = ?",
                (slot_id,),
            ).fetchone()
        return str(row["expected_hash_hmac"]) if row else ""

    def record_emergency_event(
        self,
        *,
        slot_id: str,
        event: str,
        result: str,
        hash_hmac: str = "",
        access_path: str = "",
        storage_state: dict[str, Any] | None = None,
        message: str = "",
    ) -> None:
        state = storage_state or {}
        with self.connect() as db:
            db.execute(
                """
                INSERT INTO emergency_access_history (
                    slot_id, event, result, hash_hmac, access_path, disk_number, partition_number, message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    slot_id,
                    event,
                    result,
                    hash_hmac,
                    access_path,
                    str(state.get("diskNumber") or ""),
                    str(state.get("partitionNumber") or ""),
                    message,
                ),
            )

    def load_or_create_secret(self) -> bytes:
        if self.key_path.exists():
            protected = self.key_path.read_bytes()
            return unprotect_local_secret(protected)
        secret = secrets.token_bytes(32)
        self.key_path.write_bytes(protect_local_secret(secret))
        return secret


def protect_local_secret(secret: bytes) -> bytes:
    if sys.platform != "win32":
        return secret
    return _crypt_protect(secret)


def unprotect_local_secret(secret: bytes) -> bytes:
    if sys.platform != "win32":
        return secret
    return _crypt_unprotect(secret)


def _blob_from_bytes(data: bytes) -> tuple[DATA_BLOB, Any]:
    buffer = create_string_buffer(data)
    blob = DATA_BLOB(len(data), c_void_p(addressof(buffer)))
    return blob, buffer


def _crypt_protect(data: bytes) -> bytes:
    crypt32 = cdll.crypt32
    kernel32 = cdll.kernel32
    kernel32.LocalFree.argtypes = [c_void_p]
    kernel32.LocalFree.restype = c_void_p
    in_blob, _buffer = _blob_from_bytes(data)
    out_blob = DATA_BLOB()
    if not crypt32.CryptProtectData(byref(in_blob), c_char_p(b"LOCK-FIX local key"), None, None, None, 0, byref(out_blob)):
        raise OSError("Windows DPAPI failed to protect LOCK-FIX key")
    try:
        output = create_string_buffer(out_blob.cbData)
        memmove(output, out_blob.pbData, out_blob.cbData)
        return output.raw
    finally:
        kernel32.LocalFree(c_void_p(out_blob.pbData))


def _crypt_unprotect(data: bytes) -> bytes:
    crypt32 = cdll.crypt32
    kernel32 = cdll.kernel32
    kernel32.LocalFree.argtypes = [c_void_p]
    kernel32.LocalFree.restype = c_void_p
    in_blob, _buffer = _blob_from_bytes(data)
    out_blob = DATA_BLOB()
    if not crypt32.CryptUnprotectData(byref(in_blob), None, None, None, None, 0, byref(out_blob)):
        raise OSError("Windows DPAPI failed to open LOCK-FIX key")
    try:
        output = create_string_buffer(out_blob.cbData)
        memmove(output, out_blob.pbData, out_blob.cbData)
        return output.raw
    finally:
        kernel32.LocalFree(c_void_p(out_blob.pbData))
