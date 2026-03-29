# Changelog

## v0.1.0

### Added

- `GET /health` — returns `{"status": "ok"}` with HTTP 200
- `POST /items` — creates an in-memory item with a UUID; validates `name` (required) and `price` (required, must be > 0); returns 422 on invalid input
- `GET /items/{id}` — retrieves an item by UUID; returns 404 if not found
