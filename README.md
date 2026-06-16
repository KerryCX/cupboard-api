# Cupboard API

A small REST API for tracking pantry/cupboard stock - built as a hands-on project for learning FastAPI and Pydantic, with full CRUD support and a properly tested validation layer.

## What it does

Tracks items (name, category, and stock status: `in_stock`, `low_stock`, or `out_of_stock`) through a simple REST API.

| Method | Endpoint           | Description                          |
|--------|--------------------|---------------------------------------|
| GET    | `/`                 | Health check                          |
| GET    | `/items`            | List all items                        |
| GET    | `/items/{item_id}`  | Get a single item by id               |
| POST   | `/items`            | Create a new item                     |
| PATCH  | `/items/{item_id}`  | Update one or more fields of an item  |
| DELETE | `/items/{item_id}`  | Remove an item                        |

Interactive documentation (Swagger UI) is available at `/docs` once the server is running.

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn
uvicorn app.main:app --reload
```

Then visit `http://127.0.0.1:8000/docs`.

## Running tests

```bash
pip install pytest httpx
pytest test_main.py -v
```

Twelve tests cover the full CRUD flow, including validation failures (`422`) and not-found cases (`404`).

## Design notes

- **Validation is declarative, not hand-rolled.** Request and response shapes are defined once as Pydantic models (`app/models.py`), and FastAPI validates every request against them automatically - including the `in_stock` / `low_stock` / `out_of_stock` status enum.
- **Items are identified by a generated id, not by name.** This avoids any ambiguity when two items share a name (two different kinds of milk, say) - callers always act on a specific id rather than searching by name.
- **Updates are partial by design.** `PATCH` only changes fields actually included in the request body (via Pydantic's `exclude_unset`), so updating just an item's status never accidentally wipes out its name or category.

## Known limitations

- **Storage is in-memory only.** Restarting the server resets everything back to two seed items - there's no database or file persistence yet. This was a deliberate scope decision, to get the API layer right first.
- **No authentication.** Anyone who can reach the API can read or modify any item.

## Background

This API mirrors the logic of an earlier, plain-Python menu-driven CLI version of the same idea. Comparing the two is a useful illustration of how the same domain logic looks different depending on whether it's built for an interactive human (input validation loops, disambiguating duplicate names) or a stateless HTTP client (declarative validation, identification by id).
