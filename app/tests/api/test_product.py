import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_db
from app.main import app
from app.models.constant import Constant
from app.models.product import Product

# Thiết lập database test
SQLALCHEMY_DATABASE_URL = "sqlite:///api_test_db.db"


@pytest.fixture
def session():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_products(session):
    # Tạo constant cho testing
    constant = Constant(id=uuid.uuid4(), type=1, name="7")
    session.add(constant)

    # Tạo một số sản phẩm test
    products = []
    for i in range(15):
        product = Product(
            id=uuid.uuid4(),
            name=f"Test Product {i}",
            description=f"Description {i}",
            price=str(100 + i),
            base="USD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        products.append(product)
        session.add(product)
    session.commit()
    return products


def test_read_products_list(client, sample_products):
    response = client.get("/api/v1/product")
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) > 1  # Mặc định size=10
    assert data["pagination"]["total_records"] > 1
    assert data["pagination"]["total_pages"] > 1


def test_read_products_list_with_pagination(client, sample_products):
    response = client.get("/api/v1/product?page=1")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) <= 10 and len(data["data"]) >= 1
    assert data["pagination"]["current"] == 1
    assert data["pagination"]["total_pages"] >= 1
    assert data["pagination"]["total_records"] >= 1


def test_read_product_detail(client, sample_products):
    product_id = sample_products[0].id
    response = client.get(f"/api/v1/product/{product_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(product_id)
    assert data["name"] == "Test Product 0"


def test_read_product_detail_not_found(client):
    fake_id = uuid.uuid4()
    response = client.get(f"/api/v1/product/{fake_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
