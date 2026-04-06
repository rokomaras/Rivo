"""Ownership, workflow and constraint integration tests for orders."""
import pytest


def _create_order(client, token: str) -> dict:
    r = client.post("/orders/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 201, r.text
    return r.json()


def _add_item(client, token: str, order_id: int, product_id: int = 1) -> dict:
    r = client.post(
        f"/orders/{order_id}/items",
        json={"product_id": product_id, "quantity": 2, "unit_price": "5.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return r


# ---------------------------------------------------------------------------
# Ownership
# ---------------------------------------------------------------------------

def test_customer_cannot_access_other_customers_order(client, customer_token, customer_b_token):
    order = _create_order(client, customer_token)
    r = client.get(
        f"/orders/{order['id']}",
        headers={"Authorization": f"Bearer {customer_b_token}"},
    )
    assert r.status_code == 403


def test_customer_can_access_own_order(client, customer_token):
    order = _create_order(client, customer_token)
    r = client.get(
        f"/orders/{order['id']}",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert r.status_code == 200


def test_admin_can_access_any_order(client, admin_token, customer_token):
    order = _create_order(client, customer_token)
    r = client.get(
        f"/orders/{order['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Workflow: checkout locks the order
# ---------------------------------------------------------------------------

def test_checkout_transitions_to_submitted(client, customer_token):
    order = _create_order(client, customer_token)
    r = client.post(
        f"/orders/{order['id']}/checkout",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "submitted"


def test_add_item_after_checkout_returns_400_order_locked(client, customer_token):
    order = _create_order(client, customer_token)
    # checkout first
    client.post(
        f"/orders/{order['id']}/checkout",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    r = _add_item(client, customer_token, order["id"])
    assert r.status_code == 400
    assert r.json()["code"] == "order_locked"


def test_update_item_after_checkout_returns_400_order_locked(client, customer_token):
    order = _create_order(client, customer_token)
    r = _add_item(client, customer_token, order["id"])
    assert r.status_code == 201, r.text
    item_id = r.json()["id"]
    # checkout
    client.post(
        f"/orders/{order['id']}/checkout",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    r2 = client.patch(
        f"/orders/{order['id']}/items/{item_id}",
        json={"quantity": 5},
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert r2.status_code == 400
    assert r2.json()["code"] == "order_locked"


def test_delete_item_after_checkout_returns_400_order_locked(client, customer_token):
    order = _create_order(client, customer_token)
    r = _add_item(client, customer_token, order["id"])
    assert r.status_code == 201, r.text
    item_id = r.json()["id"]
    # checkout
    client.post(
        f"/orders/{order['id']}/checkout",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    r2 = client.delete(
        f"/orders/{order['id']}/items/{item_id}",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert r2.status_code == 400
    assert r2.json()["code"] == "order_locked"


# ---------------------------------------------------------------------------
# Constraint: duplicate product in same order → 409
# ---------------------------------------------------------------------------

def test_duplicate_item_returns_409(client, customer_token):
    order = _create_order(client, customer_token)
    r1 = _add_item(client, customer_token, order["id"], product_id=1)
    assert r1.status_code == 201, r1.text
    r2 = _add_item(client, customer_token, order["id"], product_id=1)
    assert r2.status_code == 409
    assert r2.json()["code"] == "duplicate_item"
