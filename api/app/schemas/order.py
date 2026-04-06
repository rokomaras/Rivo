from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Must be greater than 0")
    unit_price: Decimal = Field(gt=0, description="Must be greater than 0")


class OrderItemUpdate(BaseModel):
    quantity: int = Field(gt=0, description="Must be greater than 0")


class OrderItemRead(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    pass  # order is created for current user; no extra fields needed at creation


class OrderRead(BaseModel):
    id: int
    user_id: int
    status: str
    created_at: datetime
    submitted_at: datetime | None = None
    items: list[OrderItemRead] = []

    model_config = {"from_attributes": True}
