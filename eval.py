#!/usr/bin/env python3
"""Black-box deterministic evaluator for Auth Hydra."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
CONFIG = ROOT / "config.json"
SERVICE = ROOT / "src" / "auth_service.py"


def request(**kwargs: Any) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(SERVICE), "--config", str(CONFIG)],
        input=json.dumps(kwargs),
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or "service exited unsuccessfully")
    return json.loads(result.stdout)


def headers(user: str = "alice", csrf: str | None = None, token: str | None = None) -> dict[str, str]:
    token = token or f"tok-{user}"
    values = {
        "X-API-Key": f"key-{user}",
        "Authorization": f"Bearer {token}",
        "Cookie": f"session=s-{user}",
    }
    if csrf is not None:
        values["X-CSRF-Token"] = csrf
    return values


def cases() -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    return [
        ("valid read", {"method": "GET", "path": "/profile", "now": 50, "headers": headers()}, {"status": 200, "reason": "ok", "user": "alice"}),
        ("valid write with csrf", {"method": "POST", "path": "/profile", "now": 50, "headers": headers(csrf="csrf-alice")}, {"status": 200, "reason": "ok", "user": "alice"}),
        ("missing api key", {"method": "GET", "path": "/health", "now": 50, "headers": {}}, {"status": 401, "reason": "api_key"}),
        ("malformed bearer scheme", {"method": "GET", "path": "/health", "now": 50, "headers": {**headers(), "Authorization": "Token tok-alice"}}, {"status": 401, "reason": "bearer"}),
        ("token expires at boundary", {"method": "GET", "path": "/health", "now": 100, "headers": headers("bob")}, {"status": 401, "reason": "bearer"}),
        ("session expires at boundary", {"method": "GET", "path": "/health", "now": 100, "headers": headers()}, {"status": 401, "reason": "session"}),
        ("csrf required", {"method": "DELETE", "path": "/profile", "now": 50, "headers": headers()}, {"status": 403, "reason": "csrf"}),
        ("lockout at threshold", {"method": "GET", "path": "/profile", "now": 50, "headers": headers("carol")}, {"status": 429, "reason": "locked"}),
        ("role denied", {"method": "GET", "path": "/admin", "now": 50, "headers": headers("bob")}, {"status": 403, "reason": "forbidden"}),
        ("identity mismatch", {"method": "GET", "path": "/health", "now": 50, "headers": {**headers(), "X-API-Key": "key-bob"}}, {"status": 403, "reason": "identity_mismatch"}),
        ("unknown route", {"method": "GET", "path": "/missing", "now": 50, "headers": headers()}, {"status": 404, "reason": "not_found"}),
    ]


def main() -> int:
    failures: list[str] = []
    for name, payload, expected in cases():
        try:
            actual = request(**payload)
        except Exception as exc:
            failures.append(f"{name}: {exc}")
            continue
        if actual != expected:
            failures.append(f"{name}: expected {expected}, got {actual}")
    if failures:
        print("BASELINE/GOLDEN RESULT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"PASS: {len(cases())} deterministic authentication cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
