"""
main.py

The actual running FastAPI application - this is the file uvicorn
points at to start the server.
"""

from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from app.models import CreateItemDto, Item, UpdateItemDto

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


# Same {item_id} path parameter pattern as delete_item() and
# update_item() below - and the same "loop through items, return on
# match, raise HTTPException if nothing matched" shape too. That's now
# three endpoints repeating this exact lookup. Worth keeping an eye on,
# the same way pick_from_matches() in cupboard.py only got extracted
# once the duplication between add_item() and remove_item() became
# obvious - not necessarily something to fix the moment it appears.
@app.get("/items/{item_id}")
def get_item(item_id: str) -> Item:
    for item in items:
        if item.id == item_id:
            return item

    raise HTTPException(status_code=404, detail=f"No item with id {item_id} found")


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


# UpdateItemDto has every field optional, so a client only needs to
# send what's actually changing - e.g. {"status": "low_stock"} on its
# own, leaving name and category untouched.
#
# .model_dump(exclude_unset=True) is the key piece: it converts
# UpdateItemDto back into a plain dict, but ONLY including fields the
# caller actually sent. Without exclude_unset, every omitted field
# would come through as None and overwrite real data with nothing -
# the exact bug a naive "just copy every field across" update would
# introduce. Roughly the same problem `{ ...item, ...req.body }` in JS
# avoids by spreading, just solved on the Pydantic side instead.
@app.patch("/items/{item_id}")
def update_item(item_id: str, updates: UpdateItemDto) -> Item:
    for item in items:
        if item.id == item_id:
            update_data = updates.model_dump(exclude_unset=True)

            # setattr(item, field, value) sets an attribute by name
            # given as a string - the Python equivalent of `item[field]
            # = value` in JS, useful here because the field name isn't
            # known in advance; it's whatever the caller happened to
            # include.
            for field, value in update_data.items():
                setattr(item, field, value)

            item.updated_at = datetime.now().isoformat()
            return item

    raise HTTPException(status_code=404, detail=f"No item with id {item_id} found")
