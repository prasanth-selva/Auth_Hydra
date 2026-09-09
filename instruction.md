# Auth Hydra: repair the request authorizer

`src/auth_service.py` is the request authorizer used by a small internal API. It receives one JSON request on stdin and returns one JSON response on stdout:

```bash
python3 src/auth_service.py --config config.json < request.json
```

Repair the implementation without changing the command-line interface or response shape.

## Request contract

A request may contain `method`, `path`, `now`, and `headers`. Header names use their exact spelling from the examples. The configuration file contains API keys, bearer tokens, sessions, lockout counters, route roles, and `max_failed_attempts`.

Authentication has four layers:

1. `X-API-Key` must identify an existing API-key record.
2. `Authorization` must be exactly a bearer credential in the form `Bearer <token>`; the token must exist and remain valid at the supplied timestamp.
3. The `session` cookie must exist and remain valid at the supplied timestamp.
4. The API-key user and bearer-token user must be the same.

For `POST`, `PUT`, `PATCH`, and `DELETE`, `X-CSRF-Token` must match the session's CSRF token. A token is locked when its user's `failed_attempts` is greater than or equal to `max_failed_attempts`. Locked users receive `429`.

After authentication, the requested path must exist. Routes with a `role` require that role in the bearer token's roles. Missing routes return `404`; insufficient roles return `403`.

Use the status and reason values already represented in the starter and preserve the successful response's user field. Do not add network access, external dependencies, or state that depends on wall-clock time.

## Acceptance criteria

- Valid read and write requests succeed.
- Missing, malformed, expired, mismatched, or unauthorized credentials are rejected with the correct status and reason.
- Expiry and lockout boundaries are deterministic.
- Unknown routes and role-protected routes follow the contract above.
- `python3 eval.py` exits zero in the repaired environment.
