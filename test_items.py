import pytest
from fastapi.testclient import TestClient
from main import app, _items

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_items():
    _items.clear()
    yield
    _items.clear()


def test_create_item_success():
    response = client.post("/items", json={"name": "Widget", "price": 9.99})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Widget"
    assert data["price"] == 9.99
    assert "id" in data


def test_get_item_after_create():
    create_resp = client.post("/items", json={"name": "Gadget", "price": 4.50})
    item_id = create_resp.json()["id"]
    get_resp = client.get(f"/items/{item_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == item_id
    assert get_resp.json()["name"] == "Gadget"


def test_create_item_missing_name():
    response = client.post("/items", json={"price": 5.00})
    assert response.status_code == 422


def test_create_item_missing_price():
    response = client.post("/items", json={"name": "Thing"})
    assert response.status_code == 422


def test_create_item_negative_price():
    response = client.post("/items", json={"name": "Cheap", "price": -1.00})
    assert response.status_code == 422


def test_get_item_not_found():
    response = client.get("/items/nonexistent-id")
    assert response.status_code == 404
