from decimal import Decimal

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    category_id: int | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    category_id: int | None = None


class ProductRead(ProductBase):
    id: int

    model_config = {"from_attributes": True}
