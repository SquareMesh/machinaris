# API Bind Address and Local Worker URL Resolution

**Category:** patterns
**Relevance:** CONFIGURATION.md — Security, ARCHITECTURE.md — Controller-Worker Model
**Date researched:** 2026-03-23

## Summary
When binding a multi-service application's internal API to `127.0.0.1` for security, any component that calls the API using the host's LAN IP (stored in a database or config) will fail with "Connection Refused". A URL resolution layer is needed to rewrite local worker URLs to `localhost` at the HTTP call site.

## Key Findings
- Machinaris stores each worker's URL as `http://<worker_address>:<port>` in the database, using the LAN IP
- Both the WebUI and API scheduler use `worker.url` for HTTP calls (pings, actions, configs)
- Binding the API to `127.0.0.1` breaks all calls that use the LAN IP from within the same container
- The worker registration must keep the LAN IP so multi-worker setups work when the API is opened to `0.0.0.0`
- The fix is a `_resolve_url(worker)` helper at the HTTP call layer that rewrites to localhost for local workers

## Code Example
```python
def _resolve_url(worker):
    api_bind = os.environ.get('api_bind_address', '127.0.0.1')
    if api_bind in ('127.0.0.1', 'localhost') and worker.hostname == get_hostname():
        port = os.environ.get('worker_api_port', '8927')
        return "http://localhost:{0}".format(port)
    return worker.url
```

## Decision / Recommendation
Always add a URL resolution layer when introducing bind address restrictions. The resolution should be transparent to callers (applied inside `send_get`/`send_post` etc.), not at registration time, so the stored data remains correct for both single and multi-instance modes.

## Sources
- Gunicorn `--bind` documentation
- Flask/Gunicorn multi-worker deployment patterns
