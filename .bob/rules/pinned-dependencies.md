# Pinned Dependencies

## Rule

Every entry in `requirements.txt` MUST use exact version pinning with `==`. Unpinned or loosely-pinned dependencies are not allowed.

### Allowed

```
fastapi==0.141.1
uvicorn[standard]==0.52.4
sqlalchemy==2.0.52
```

### Not allowed

```
fastapi>=0.100.0
uvicorn
sqlalchemy~=2.0
fastapi!=0.140.0
```

### Enforcement

- When **adding a new dependency**, always pin to the exact version you installed (e.g. run `pip show <package>` to confirm the version, then write `package==x.y.z`).
- When **reviewing a `requirements.txt` change**, reject any entry that does not use `==`.
- Do **not** use `>=`, `~=`, `!=`, `>`, `<`, or bare unpinned names.
- If a dependency needs upgrading, update the pinned version explicitly — do not widen the constraint.

### Rationale

Unpinned dependencies mean the installed environment can change silently on the next `pip install`, breaking builds or introducing vulnerabilities. Exact pins guarantee reproducible installs across all environments.
