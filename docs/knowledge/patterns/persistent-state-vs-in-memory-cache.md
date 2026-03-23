# Persistent State vs In-Memory Cache for Notification Dedup

**Category:** patterns
**Relevance:** TELEGRAM-NOTIFICATIONS.md — Balance Change Detection
**Date researched:** 2026-03-23

## Summary
In-memory dedup caches (Python dicts) are lost when gunicorn recycles workers via `max_requests`. For deduplication that must survive process restarts, use file-based persistence instead.

## Key Findings
- Gunicorn's `max_requests=1000` causes worker processes to restart after N requests
- Any Python-level global state (dicts, module variables) is wiped on restart
- For balance notification dedup, this caused false notifications when the cache was empty after restart
- Additionally, comparing re-parsed CLI text (old vs new) introduced float variance even when balances were identical
- Solution: persist the last-known balance as a float in a JSON file, compare new parse against that stored value

## Code Example
```python
_STATE_FILE = '/root/.chia/machinaris/config/balance_state.json'

def _load_state():
    if not os.path.exists(_STATE_FILE):
        return {}
    with open(_STATE_FILE) as f:
        return json.load(f)

def _save_state(state):
    with open(_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
```

## Decision / Recommendation
Use file-based state for any dedup or comparison logic that runs in gunicorn workers with `max_requests` enabled. The file I/O overhead is negligible compared to the cost of false notifications or missed dedup. For high-frequency operations, consider SQLite or a shared memory approach instead.

## Sources
- Gunicorn `max_requests` documentation
- Python multiprocessing state management patterns
