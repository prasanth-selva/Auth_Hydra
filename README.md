# Auth Hydra

A deterministic terminal benchmark for repairing a broken multi-layer authentication authorizer.

The service is intentionally defective at the start. The public task is described in `instruction.md`; the evaluator drives the JSON CLI and does not depend on private helper names.

Local checks:

```bash
python3 eval.py
```

The container workflow is deterministic and uses only the Python standard library.
