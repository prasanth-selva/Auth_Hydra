# Auth Hydra benchmark report

## Status

**BENCHMARK STATUS: PASS**

## Real-world problem

Repair a request authorizer for an internal API with API-key, bearer-token,
session, CSRF, role, and lockout checks.

## Objective success criteria

- Valid authenticated reads and CSRF-protected writes return 200.
- Malformed, expired, mismatched, unauthorized, and locked credentials return
the documented status and reason.
- Expiry and lockout boundaries are inclusive and deterministic.
- Unknown routes return 404 after authentication.
- The CLI and Docker workflow are stable without network services.

## Broken initial state

The starter accepted credentials at expiry boundaries, used an exclusive
lockout threshold, and did not strictly validate the bearer scheme.

## Lifecycle results

| Gate | Result |
|---|---|
| Fresh baseline | FAIL, as required |
| Golden solution | PASS |
| Functional evaluator | PASS, 11 cases |
| Edge cases | PASS |
| Determinism | PASS |
| Docker build and run | PASS |
| Network dependency | None |
| Public CLI evaluation | PASS |

## Files

- `instruction.md`: agent-facing task contract
- `src/auth_service.py`: intentionally broken starter, repaired in final state
- `eval.py`: black-box deterministic evaluator
- `config.json`: local fixture data
- `reference/fix_auth_service.py`: golden repair kept separate from the task contract
- `Dockerfile` and `solve.sh`: reproducible execution

## Remaining packaging note

For an external benchmark runner, ship `reference/` outside the agent-visible
archive. It is kept separately in this development workspace only to support
the baseline/golden lifecycle proof.

## Final decision

**SUBMIT**
