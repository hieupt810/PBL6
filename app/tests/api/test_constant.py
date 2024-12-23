import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.main import app

# Sử dụng lại các fixture từ test_product.py
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
def client():
    return TestClient(app)


def test_read_filter_list(client):
    response = client.get("/api/v1/const")
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "number" in data
    assert data["number"] == 2

    # Kiểm tra cấu trúc của response
    filters = data["data"]
    assert len(filters) == 2

    # Kiểm tra category filter
    category_filter = filters[0]
    assert category_filter["param"] == "c"
    assert category_filter["placeholder"] == "Select a category"
    assert len(category_filter["options"]) == 10

    # Kiểm tra time filter
    time_filter = filters[1]
    assert time_filter["param"] == "t"
    assert time_filter["placeholder"] == "Select a time"
    assert len(time_filter["options"]) == 5

    # Kiểm tra format của time filter names
    time_options = time_filter["options"]
    assert any(option["name"] == "Last 1 day" for option in time_options)
    assert any(option["name"] == "Last 7 days" for option in time_options)
