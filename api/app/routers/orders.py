from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import DomainError, ForbiddenError, NotFoundError
from app.core.security import get_current_user
from app.repositories import order as order_repo
from app.schemas.order import OrderItemCreate, OrderItemRead, OrderItemUpdate, OrderRead

router = APIRouter(prefix="/orders", tags=["orders"])


def _get_order_or_404(db: Session, order_id: int):
    order = order_repo.get_order(db, order_id)
    if not order:
        raise NotFoundError("Order not found")
    return order


def _check_ownership(order, current_user):
    if current_user.role != "admin" and not current_user.is_admin:
        if order.user_id != current_user.id:
            raise ForbiddenError("Access to this order is not allowed")


@router.post("/", response_model=OrderRead, status_code=201)
def create_order(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return order_repo.create_order(db, user_id=current_user.id)


@router.get("/", response_model=list[OrderRead])
def list_orders(
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = None if (current_user.role == "admin" or current_user.is_admin) else current_user.id
    return order_repo.get_orders(db, user_id=user_id, status=status, limit=limit, offset=offset)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = _get_order_or_404(db, order_id)
    _check_ownership(order, current_user)
    return order


@router.post("/{order_id}/items", response_model=OrderItemRead, status_code=201)
def add_item(
    order_id: int,
    data: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = _get_order_or_404(db, order_id)
    _check_ownership(order, current_user)
    return order_repo.add_item(db, order, data)


@router.patch("/{order_id}/items/{item_id}", response_model=OrderItemRead)
def update_item(
    order_id: int,
    item_id: int,
    data: OrderItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = _get_order_or_404(db, order_id)
    _check_ownership(order, current_user)
    item = order_repo.get_item(db, item_id)
    if not item or item.order_id != order_id:
        raise NotFoundError("Order item not found")
    return order_repo.update_item(db, order, item, data)


@router.delete("/{order_id}/items/{item_id}", status_code=204)
def delete_item(
    order_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = _get_order_or_404(db, order_id)
    _check_ownership(order, current_user)
    item = order_repo.get_item(db, item_id)
    if not item or item.order_id != order_id:
        raise NotFoundError("Order item not found")
    order_repo.delete_item(db, order, item)


@router.post("/{order_id}/checkout", response_model=OrderRead)
def checkout(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = _get_order_or_404(db, order_id)
    _check_ownership(order, current_user)
    return order_repo.submit_order(db, order)
