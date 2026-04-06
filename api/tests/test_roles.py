"""Role / permission integration tests."""
import pytest


def test_customer_cannot_create_product(client, customer_token):
    r = client.post(
        "/products/",
        json={"name": "Test", "price": "9.99"},
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert r.status_code == 403


def test_admin_can_create_product(client, admin_token):
    r = client.post(
        "/products/",
        json={"name": "AdminProd", "price": "19.99"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 201


def test_customer_cannot_create_category(client, customer_token):
    r = client.post(
        "/categories/",
        json={"name": "TestCat"},
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert r.status_code == 403


def test_admin_can_create_category(client, admin_token):
    r = client.post(
        "/categories/",
        json={"name": "AdminCat"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 201
