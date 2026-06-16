"""
main.py

The actual running FastAPI application - this is the file uvicorn
points at to start the server.
"""

from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from app.models import CreateItemDto, Item

# Creating the FastAPI app is the rough equivalent of `const app =
# express()` in Express - one object that everything else (routes,
# middleware) attaches to.
app = FastAPI()


# @app.get("/") is a decorator - it wraps the function below it with
# extra behaviour. This is how a plain function becomes a route: "when
# a GET request hits /, call this function and send back whatever it
# returns as JSON." Roughly `app.get('/', (req, res) => res.json({...}))`
# in Express, just inside-out syntactically - the handler is written
# first, the route registration wraps around it via @.
@app.get("/")
def read_root():
    return {"message": "Cupboard API is running"}


# A real, mutable list standing in for a database for now - playing
# the same role `items` plays inside cupboard.py, just living in
# server memory instead of a JSON file. Restarting the server resets
# this list back to these two seed entries, the same way cupboard.py
# would lose everything without save_items() to persist it.
items: list[Item] = [
    Item(
        id=str(uuid4()),
        name="Milk",
        category="Dairy",
        status="out_of_stock",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
    ),
    Item(
        id=str(uuid4()),
        name="Bread",
        category="Bakery",
        status="low_stock",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
    ),
]


# The `-> list[Item]` return type annotation isn't just documentation
# here, the way it would be in plain Python - FastAPI actually reads
# it and uses it to validate and shape the JSON response, enforced at
# runtime, not just checked by an editor.
@app.get("/items")
def list_items() -> list[Item]:
    return items


# `item: CreateItemDto` as a parameter is the key piece here - FastAPI
# sees that type hint, reads the incoming request body as JSON, and
# validates it against CreateItemDto BEFORE this function body even
# runs. This is the exact same validation you tested by hand ages ago
# (CreateItemDto(name="Milk", category="Dairy")) - it's just firing on
# real HTTP requests now instead of inside a Python shell.
@app.post("/items")
def create_item(item: CreateItemDto) -> Item:
    now = datetime.now().isoformat()
    new_item = Item(
        id=str(uuid4()),
        name=item.name,
        category=item.category,
        status=item.status,
        created_at=now,
        updated_at=now,
    )
    items.append(new_item)
    return new_item


# {item_id} in the route path is a path parameter - FastAPI matches it
# to the `item_id` function parameter automatically. The same idea as
# Express's `router.delete('/items/:id', ...)` then reading `req.params.id`,
# just declared through the function signature instead of a separate
# params object.
#
# Unlike create_item()'s validation, "does this id actually exist?"
# isn't something Pydantic can check for you - there's no type that
# means "a real item in the list." That's what HTTPException is for:
# raising it stops the function immediately and sends back whatever
# status_code and detail you give it, the rough equivalent of
# `res.status(404).json({ detail: '...' })` in Express.
@app.delete("/items/{item_id}")
def delete_item(item_id: str) -> dict:
    for item in items:
        if item.id == item_id:
            items.remove(item)
            return {"message": f"Removed {item.name} ({item.category})"}

    raise HTTPException(status_code=404, detail=f"No item with id {item_id} found")
