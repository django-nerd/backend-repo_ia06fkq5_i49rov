"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# ---------------- Food Delivery App Schemas ----------------

class Restaurant(BaseModel):
    name: str = Field(..., description="Restaurant name")
    description: Optional[str] = Field(None, description="Short description")
    image: Optional[str] = Field(None, description="Cover image URL")
    cuisine: Optional[str] = Field(None, description="Cuisine type, e.g., Italian")
    rating: Optional[float] = Field(4.5, ge=0, le=5, description="Average rating")
    delivery_time: Optional[str] = Field("25-35 min", description="Estimated delivery time")

class Menuitem(BaseModel):
    restaurant_id: str = Field(..., description="Related restaurant ObjectId as string")
    name: str = Field(..., description="Dish name")
    description: Optional[str] = Field(None, description="Dish description")
    price: float = Field(..., ge=0, description="Price in dollars")
    image: Optional[str] = Field(None, description="Image URL")
    vegetarian: Optional[bool] = Field(False, description="Is vegetarian")
    spicy: Optional[bool] = Field(False, description="Is spicy")

class OrderItem(BaseModel):
    menu_item_id: str = Field(..., description="Menu item ObjectId as string")
    quantity: int = Field(1, ge=1, description="Quantity")

class Order(BaseModel):
    customer_name: str
    address: str
    phone: str
    restaurant_id: str
    items: List[OrderItem]
    notes: Optional[str] = None
    total: Optional[float] = Field(None, ge=0)

# ---------------- Example Schemas (kept for reference) ----------------

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
