import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.config import settings
from app.main import app
from app.models.base import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    client.headers["X-API-Key"] = settings.API_KEY
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_building(db_session):
    """Создает тестовое здание"""
    from app.models.building import Building
    building = Building(
        address="г. Москва, ул. Тестовая 1",
        latitude=55.7558,
        longitude=37.6173
    )
    db_session.add(building)
    db_session.commit()
    db_session.refresh(building)
    return building


@pytest.fixture
def test_activity_tree(db_session):
    """Создает тестовое дерево активностей"""
    from app.models.activity import Activity

    root_activity = Activity(name="Тестовая корневая")
    db_session.add(root_activity)
    db_session.flush()

    child_activity = Activity(name="Тестовая дочерняя", parent_id=root_activity.id)
    db_session.add(child_activity)
    db_session.flush()

    grandchild_activity = Activity(name="Тестовая внучка", parent_id=child_activity.id)
    db_session.add(grandchild_activity)

    db_session.commit()

    return {
        "root": root_activity,
        "child": child_activity,
        "grandchild": grandchild_activity
    }


@pytest.fixture
def test_organization(db_session, test_building, test_activity_tree):
    """Создает тестовую организацию"""
    from app.models.organization import Organization
    from app.models.phone_number import PhoneNumber

    organization = Organization(
        name="Тестовая организация",
        building_id=test_building.id
    )
    db_session.add(organization)
    db_session.flush()

    phone = PhoneNumber(number="123-456-789", organization_id=organization.id)
    db_session.add(phone)

    organization.activities.append(test_activity_tree["root"])

    db_session.commit()
    db_session.refresh(organization)
    return organization