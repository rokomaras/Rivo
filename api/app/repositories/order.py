from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import DuplicateItemError, NotFoundError, OrderLockedError
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order import OrderItemCreate, OrderItemUpdate


def create_order(db: Session, user_id: int) -> Order:
    order = Order(user_id=user_id, status="draft", created_at=datetime.now(timezone.utc))
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders(
    db: Session,
    user_id: int | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Order]:
    q = db.query(Order)
    if user_id is not None:
        q = q.filter(Order.user_id == user_id)
    if status is not None:
        q = q.filter(Order.status == status)
    return q.order_by(Order.id).limit(limit).offset(offset).all()


def submit_order(db: Session, order: Order) -> Order:
    if order.status != "draft":
        raise OrderLockedError("Order is already submitted")
    order.status = "submitted"
    order.submitted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(order)
    return order


def add_item(db: Session, order: Order, data: OrderItemCreate) -> OrderItem:
    if order.status != "draft":
        raise OrderLockedError()
    item = OrderItem(
        order_id=order.id,
        product_id=data.product_id,
        quantity=data.quantity,
        unit_price=data.unit_price,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateItemError("Product already in this order")
    db.refresh(item)
    return item


def get_item(db: Session, item_id: int) -> OrderItem | None:
    return db.query(OrderItem).filter(OrderItem.id == item_id).first()


def update_item(db: Session, order: Order, item: OrderItem, data: OrderItemUpdate) -> OrderItem:
    if order.status != "draft":
        raise OrderLockedError()
    item.quantity = data.quantity
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, order: Order, item: OrderItem) -> None:
    if order.status != "draft":
        raise OrderLockedError()
    db.delete(item)
    db.commit()
