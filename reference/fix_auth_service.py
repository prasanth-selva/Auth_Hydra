from pathlib import Path

path = Path(__file__).parents[1] / "src" / "auth_service.py"
text = path.read_text()
text = text.replace('token = authorization.removeprefix("Bearer ")\n    token_record', 'scheme, separator, token = authorization.partition(" ")\n    if scheme != "Bearer" or not separator or not token:\n        return {"status": 401, "reason": "bearer"}\n    token_record')
text = text.replace('now > int(token_record.get("exp", -1))', 'now >= int(token_record.get("exp", -1))')
text = text.replace('now > int(session.get("expires", -1))', 'now >= int(session.get("expires", -1))')
text = text.replace('if not route:\n        return {"status": 404, "reason": "not_found"}', 'if route is None:\n        return {"status": 404, "reason": "not_found"}')
text = text.replace('> int(config.get("max_failed_attempts", 3))', '>= int(config.get("max_failed_attempts", 3))')
path.write_text(text)
