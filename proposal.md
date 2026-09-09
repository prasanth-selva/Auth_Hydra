# Proposal: Auth Hydra — Broken Multi-Layer Authentication System

## Task Summary

Auth Hydra is a small request-authorisation service with several checks that have to agree before a request is allowed through. The service is deliberately close to the sort of code that sits in front of an internal API: API keys identify the caller, bearer tokens prove the session identity, cookies carry the session, and write requests need CSRF protection.

The starter has a few subtle boundary bugs rather than one obvious missing function. It accepts credentials at their expiry time, treats the lockout limit as exclusive, and is too forgiving about the bearer scheme. The job is to repair the implementation without changing the JSON command-line interface or the response format.

The benchmark is intentionally offline. The service reads a request from stdin, reads a local JSON configuration file, and writes one JSON response to stdout. That keeps the result repeatable while still exercising the authentication decisions that matter.

## Key Components

### 1. Service contract (`instruction.md`)

The task asks the agent to repair `src/auth_service.py` and keep this command working:

```bash
python3 src/auth_service.py --config config.json < request.json
```

The implementation must handle:

- API-key lookup
- Exact `Bearer <token>` parsing
- Token and session expiry
- API-key/token identity matching
- CSRF checks on `POST`, `PUT`, `PATCH`, and `DELETE`
- User lockout at the configured failed-attempt threshold
- Route lookup and role checks

The status codes and reason values are part of the public contract. The evaluator does not require a particular internal design.

### 2. Local fixture (`config.json`)

The configuration contains separate users for the normal, locked, and role-denied cases. Timestamps and failed-attempt counts are fixed in the file, so expiry and lockout behavior can be tested at the exact boundary without depending on the system clock.

### 3. Broken starting point (`src/auth_service.py`)

The initial implementation is syntactically valid and handles ordinary requests, but it has three meaningful defects:

- Token and session expiry use `>` instead of expiring at `>=`.
- Lockout happens only after the configured limit instead of at the limit.
- Bearer authentication strips a prefix without rejecting other schemes.

This gives the agent something to diagnose and repair rather than asking it to create a placeholder project.

### 4. Deterministic evaluator (`eval.py`)

The evaluator treats the service as a subprocess and sends requests through its documented interface. It covers 11 cases:

- Valid read request
- Valid CSRF-protected write
- Missing API key
- Invalid bearer scheme
- Token expiry boundary
- Session expiry boundary
- Missing CSRF token
- Lockout threshold
- Missing role
- API-key/token identity mismatch
- Unknown route

Each response is compared as structured JSON. Private helper names and implementation details are not part of the test contract.

## Verification Plan

The required lifecycle is:

```bash
# Fresh starter: expected to fail
python3 eval.py

# Apply the development reference repair
python3 reference/fix_auth_service.py

# Re-run the same evaluator: expected to pass
python3 eval.py
```

The Docker check uses the same evaluator and confirms that the task works in a clean environment:

```bash
docker build -t auth-hydra .
docker run --rm auth-hydra
```

