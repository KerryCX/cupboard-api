"""
test_main.py

Tests for the actual HTTP endpoints in main.py, using FastAPI's
TestClient. Unlike a real request, TestClient talks to the app
directly in-process (no real network call, no need to have uvicorn
running) - the same idea as supertest wrapping an Express app directly
rather than hitting a live server.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app, items
from app.models import Item

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_items():
    """
    `items` in main.py is ONE shared list, mutated directly by every
    endpoint (append, remove, setattr). Left alone, that's exactly the
    kind of global state that lets tests interfere with each other -
    a test that deletes Milk would silently break a later test that
    still expects Milk to be there.

    `autouse=True` means this fixture runs before EVERY test
    automatically, with no need to request it by name - the rough
    equivalent of a Jest `beforeEach` that applies to the whole file.

    Important detail: `items.clear()` and `items.extend(...)` mutate
    the SAME list object that main.py's route handlers are using -
    they don't create a new list and leave the old one behind. That
    only works because `items` here is the literal object imported
    from app.main, not a copy of it - the same "same object, not a
    copy" idea you've already seen with mutating dicts inside
    cupboard.py's `items` list.

    A real production app would usually sidestep this problem
    entirely by giving each request its own database session rather
    than sharing one in-memory list for the whole process - this
    fixture is a workaround for a genuine limitation of the current
    design, not a long-term fix.
    """
    items.clear()
    items.extend(
        [
            Item(
                id="milk-id",
                name="Milk",
                category="Dairy",
                status="out_of_stock",
                created_at="2026-01-01T00:00:00",
                updated_at="2026-01-01T00:00:00",
            ),
            Item(
                id="bread-id",
                name="Bread",
                category="Bakery",
                status="low_stock",
                created_at="2026-01-01T00:00:00",
                updated_at="2026-01-01T00:00:00",
            ),
        ]
    )


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Cupboard API is running"}


def test_list_items_returns_seeded_items():
    response = client.get("/items")
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["Milk", "Bread"]


def test_get_item_returns_the_matching_item():
    response = client.get("/items/milk-id")
    assert response.status_code == 200

    item = response.json()
    assert item["id"] == "milk-id"
    assert item["name"] == "Milk"


def test_get_item_returns_404_for_unknown_id():
    response = client.get("/items/does-not-exist")
    assert response.status_code == 404
    assert response.json() == {"detail": "No item with id does-not-exist found"}


def test_create_item_adds_to_the_list():
    response = client.post(
        "/items",
        json={"name": "Eggs", "category": "Dairy", "status": "in_stock"},
    )
    assert response.status_code == 200

    created = response.json()
    assert created["name"] == "Eggs"
    assert created["category"] == "Dairy"
    assert created["status"] == "in_stock"
    assert created["id"]  # a real id got generated, not left blank

    # Confirm it actually persisted into the shared list, not just
    # echoed back in the response.
    list_response = client.get("/items")
    names = [item["name"] for item in list_response.json()]
    assert "Eggs" in names


def test_create_item_rejects_invalid_status():
    response = client.post(
        "/items",
        json={"name": "Cheese", "category": "Dairy", "status": "moldy"},
    )
    assert response.status_code == 422


def test_create_item_rejects_empty_name():
    response = client.post("/items", json={"name": "", "category": "Dairy"})
    assert response.status_code == 422


def test_delete_item_removes_it():
    response = client.delete("/items/milk-id")
    assert response.status_code == 200
    assert response.json() == {"message": "Removed Milk (Dairy)"}

    list_response = client.get("/items")
    names = [item["name"] for item in list_response.json()]
    assert "Milk" not in names


def test_delete_item_returns_404_for_unknown_id():
    response = client.delete("/items/does-not-exist")
    assert response.status_code == 404
    assert response.json() == {"detail": "No item with id does-not-exist found"}


def test_update_item_changes_only_the_sent_field():
    response = client.patch("/items/milk-id", json={"status": "in_stock"})
    assert response.status_code == 200

    updated = response.json()
    assert updated["status"] == "in_stock"
    assert updated["name"] == "Milk"  # untouched
    assert updated["category"] == "Dairy"  # untouched


def test_update_item_rejects_invalid_status():
    response = client.patch("/items/milk-id", json={"status": "rotten"})
    assert response.status_code == 422


def test_update_item_returns_404_for_unknown_id():
    response = client.patch("/items/does-not-exist", json={"status": "in_stock"})
    assert response.status_code == 404