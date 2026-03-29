import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI()

_items: dict[str, dict] = {}


class ItemCreate(BaseModel):
    name: str
    price: float

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("price must be greater than 0")
        return v


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    item_id = str(uuid.uuid4())
    _items[item_id] = {"id": item_id, "name": item.name, "price": item.price}
    return _items[item_id]


@app.get("/items/{item_id}")
def get_item(item_id: str):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    return _items[item_id]
