import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Restaurant, Menuitem, Order, OrderItem

app = FastAPI(title="Food Delivery API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Food Delivery API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# -------------------- Helper --------------------

def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")

# -------------------- Restaurants --------------------

@app.get("/restaurants", response_model=List[Restaurant])
def list_restaurants(limit: int = 20):
    docs = get_documents("restaurant", {}, limit)
    # Normalize fields for Pydantic
    for d in docs:
        d.pop("_id", None)
    return docs

@app.post("/restaurants")
def create_restaurant(restaurant: Restaurant):
    inserted_id = create_document("restaurant", restaurant)
    return {"id": inserted_id}

# -------------------- Menu Items --------------------

@app.get("/menu", response_model=List[Menuitem])
def list_menu(restaurant_id: Optional[str] = None, limit: int = 50):
    filt = {}
    if restaurant_id:
        filt["restaurant_id"] = restaurant_id
    docs = get_documents("menuitem", filt, limit)
    for d in docs:
        d.pop("_id", None)
    return docs

@app.post("/menu")
def create_menu_item(item: Menuitem):
    inserted_id = create_document("menuitem", item)
    return {"id": inserted_id}

# -------------------- Orders --------------------

class OrderResponse(BaseModel):
    id: str

@app.post("/orders", response_model=OrderResponse)
def create_order(order: Order):
    # compute total if not provided
    if order.total is None:
        # Fetch prices for items
        items = order.items
        menu_items = get_documents("menuitem", {"_id": {"$in": [to_object_id(i.menu_item_id) for i in items]}})
        price_map = {str(m.get("_id")): m.get("price", 0) for m in menu_items}
        total = 0.0
        for it in items:
            price = price_map.get(it.menu_item_id)
            if price is None:
                raise HTTPException(status_code=400, detail=f"Menu item not found: {it.menu_item_id}")
            total += price * it.quantity
        order.total = round(total, 2)
    inserted_id = create_document("order", order)
    return {"id": inserted_id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
