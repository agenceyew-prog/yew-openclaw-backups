## [ERR-20260312-002] maton_api_key_not_found

**Logged**: 2026-03-12T15:01:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
`MATON_API_KEY` environment variable not accessible within `python3` script executed via `exec` command.

### Error
```
KeyError: 'MATON_API_KEY'
```

### Context
- Command/operation attempted: `python3 ...` to query Maton API, expecting `os.environ["MATON_API_KEY"]` to work.
- Input or parameters used: N/A
- Environment details if relevant: Variable set in `.env` but not propagated to `exec` environment.

### Suggested Fix
Explicitly export `MATON_API_KEY` before running the `python3` script or use a method that ensures environment variables from `.env` are loaded.

### Metadata
- Reproducible: yes
- Related Files: N/A
- See Also: N/A

---
