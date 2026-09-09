#!/usr/bin/env python3
"""Auth Hydra request authorizer.

The benchmark starter intentionally contains defects. The public interface is a
single JSON request on stdin and a single JSON response on stdout.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def read_cookie(header: str, name: str) -> str | None:
    for item in header.split(";"):
        key, separator, value = item.strip().partition("=")
        if separator and key == name:
            return value
    return None


def authorize(request: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    headers = request.get("headers", {})
    now = int(request.get("now", 0))
    api_key = headers.get("X-API-Key")
    api_record = config.get("api_keys", {}).get(api_key)
    if not api_record:
        return {"status": 401, "reason": "api_key"}

    authorization = headers.get("Authorization", "")
    scheme, separator, token = authorization.partition(" ")
    if scheme != "Bearer" or not separator or not token:
        return {"status": 401, "reason": "bearer"}
    token_record = config.get("tokens", {}).get(token)
    if not token_record or now >= int(token_record.get("exp", -1)):
        return {"status": 401, "reason": "bearer"}

    session_id = read_cookie(headers.get("Cookie", ""), "session")
    session = config.get("sessions", {}).get(session_id)
    if not session or now >= int(session.get("expires", -1)):
        return {"status": 401, "reason": "session"}

    if api_record.get("user") != token_record.get("user"):
        return {"status": 403, "reason": "identity_mismatch"}

    if request.get("method", "GET").upper() in MUTATING_METHODS:
        if headers.get("X-CSRF-Token") != session.get("csrf"):
            return {"status": 403, "reason": "csrf"}

    lockout = config.get("lockouts", {}).get(token_record.get("user"), {})
    if int(lockout.get("failed_attempts", 0)) >= int(config.get("max_failed_attempts", 3)):
        return {"status": 429, "reason": "locked"}

    route = config.get("routes", {}).get(request.get("path"))
    if route is None:
        return {"status": 404, "reason": "not_found"}
    required_role = route.get("role")
    if required_role and required_role not in token_record.get("roles", []):
        return {"status": 403, "reason": "forbidden"}

    return {"status": 200, "reason": "ok", "user": token_record.get("user")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    request = json.load(sys.stdin)
    print(json.dumps(authorize(request, config), sort_keys=True))


if __name__ == "__main__":
    main()
