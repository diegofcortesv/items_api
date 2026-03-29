# items_api

A minimal FastAPI service with a health check and an in-memory items store.

## Installation

```bash
pip install -r requirements.txt
```

## Running the server

```bash
uvicorn main:app --port 8000
```

## Endpoints

### GET /health

Returns service health status.

```bash
curl -s http://localhost:8000/health
# {"status":"ok"}
```

### POST /items

Create a new item. `price` must be greater than 0.

```bash
curl -s -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "price": 9.99}'
# {"id":"<uuid>","name":"Widget","price":9.99}
```

Returns `422` if `name` or `price` is missing, or if `price <= 0`.

### GET /items/{id}

Retrieve an item by its UUID.

```bash
curl -s http://localhost:8000/items/<uuid>
# {"id":"<uuid>","name":"Widget","price":9.99}
```

Returns `404` if the item does not exist.

## Running tests

```bash
pytest test_items.py -v
```
