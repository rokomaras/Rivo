"""
Shared pytest fixtures for integration tests.

Uses an in-memory SQLite database so no real Postgres is needed.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.base import Base
from app.core.database import get_db
from app.main import create_app

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
SQLITE_URL = "sqlite://"  # in-memory


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def db(engine):
    """Create a fresh session for each test, rolled back after the test."""
    connection = engine.connect()
    transaction = connection.begin()
    TestingSession = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = TestingSession()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """FastAPI TestClient with overridden DB dependency."""
    app = create_app()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

def _register_and_login(client, email: str, password: str, role: str = "customer"):
    """Register a user and return (user_data, access_token)."""
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    user = r.json()

    # If admin role needed, set via DB (simulating admin promotion)
    if role == "admin":
        # Promote via a raw DB update through the client's overridden session
        from app.core.database import get_db as _get_db
        db_gen = client.app.dependency_overrides[_get_db]()
        session = next(db_gen)
        from app.models.user import User
        u = session.query(User).filter(User.email == email).first()
        u.role = "admin"
        u.is_admin = True
        session.commit()

    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return user, token


@pytest.fixture()
def admin_token(client):
    _, token = _register_and_login(client, "admin@test.com", "adminpass", role="admin")
    return token


@pytest.fixture()
def customer_token(client):
    _, token = _register_and_login(client, "customer@test.com", "customerpass", role="customer")
    return token


@pytest.fixture()
def customer_b_token(client):
    _, token = _register_and_login(client, "customerb@test.com", "bpass", role="customer")
    return token
