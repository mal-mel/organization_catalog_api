from fastapi import status

from app.core.config import settings


class TestSecurityAndErrors:
    """Тесты безопасности и обработки ошибок"""

    def test_missing_api_key(self, client):
        """Тест запроса без API ключа"""
        client_without_key = client
        client_without_key.headers.pop(settings.API_KEY_NAME, None)

        response = client_without_key.get("/api/v1/organizations/")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_api_key(self, client):
        """Тест запроса с невалидным API ключом"""
        client_with_invalid_key = client
        client_with_invalid_key.headers[settings.API_KEY_NAME] = "invalid-key"

        response = client_with_invalid_key.get("/api/v1/organizations/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_pagination(self, client, db_session):
        """Тест пагинации"""
        from app.models.organization import Organization
        from app.models.building import Building

        building = Building(
            address="г. Москва, ул. МногоОрганизаций 1",
            latitude=55.0,
            longitude=37.0
        )
        db_session.add(building)
        db_session.flush()

        for i in range(5):
            organization = Organization(
                name=f"Организация {i}",
                building_id=building.id
            )
            db_session.add(organization)

        db_session.commit()

        response = client.get("/api/v1/organizations/?skip=2&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 2

    def test_health_check(self, client):
        """Тест health check эндпоинта"""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Тест корневого эндпоинта"""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "message" in data
        assert "version" in data

        assert data["message"] == settings.PROJECT_NAME
        assert data["version"] == settings.VERSION
