"""
main.py

The actual running FastAPI application - this is the file uvicorn
points at to start the server.
"""

from fastapi import FastAPI

from app.models import Item

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


# Standing in for a real store for now, just to prove Item (from
# models.py) actually works once something tries to return it from a
# route - this gets replaced with something real in the next step.
fake_items = [
    Item(
        id="1",
        name="Milk",
        category="Dairy",
        status="out_of_stock",
        created_at="2026-06-16T00:00:00",
        updated_at="2026-06-16T00:00:00",
    ),
    Item(
        id="2",
        name="Bread",
        category="Bakery",
        status="low_stock",
        created_at="2026-06-16T00:00:00",
        updated_at="2026-06-16T00:00:00",
    ),
]


# The `-> list[Item]` return type annotation isn't just documentation
# here, the way it would be in plain Python - FastAPI actually reads
# it and uses it to validate and shape the JSON response, enforced at
# runtime, not just checked by an editor. The closest TS equivalent
# would be a function return type that the framework itself enforces,
# not just the compiler.
@app.get("/items")
def list_items() -> list[Item]:
    return fake_items
