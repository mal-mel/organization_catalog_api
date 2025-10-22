from fastapi import status


class TestBuildings:
    """Тесты для эндпоинтов Buildings"""

    def test_get_buildings(self, client, test_building):
        """Тест получения списка зданий"""
        response = client.get("/api/v1/buildings/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["address"] == test_building.address
        assert data[0]["latitude"] == test_building.latitude
        assert data[0]["longitude"] == test_building.longitude

    def test_get_building_detail(self, client, test_building, test_organization):
        """Тест получения деталей здания с организациями"""
        response = client.get(f"/api/v1/buildings/{test_building.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == test_building.id
        assert data["address"] == test_building.address
        assert len(data["organizations"]) == 1
        assert data["organizations"][0]["name"] == test_organization.name

    def test_get_nonexistent_building(self, client):
        """Тест получения несуществующего здания"""
        response = client.get("/api/v1/buildings/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_building_organizations(self, client, test_building, test_organization):
        """Тест получения организаций в здании"""
        response = client.get(f"/api/v1/buildings/{test_building.id}/organizations")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == test_organization.id
        assert data[0]["name"] == test_organization.name
        assert data[0]["building_id"] == test_building.id

    def test_get_building_organizations_empty(self, client, db_session):
        """Тест получения организаций пустого здания"""
        from app.models.building import Building

        building = Building(
            address="г. Москва, ул. Пустая 1",
            latitude=55.0,
            longitude=37.0
        )
        db_session.add(building)
        db_session.commit()

        response = client.get(f"/api/v1/buildings/{building.id}/organizations")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 0

    def test_get_nearby_buildings_circle(self, client, test_building):
        """Тест поиска зданий в радиусе"""
        response = client.get(
            "/api/v1/buildings/nearby",
            params={
                "lat": 55.7558,
                "lon": 37.6173,
                "radius": 1000  # 1 км
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == test_building.id
        assert data[0]["distance"] is not None
        assert data[0]["distance"] <= 1000

    def test_get_nearby_buildings_rectangle(self, client, test_building):
        """Тест поиска зданий в прямоугольнике"""
        response = client.get(
            "/api/v1/buildings/nearby",
            params={
                "min_lat": 55.0,
                "max_lat": 56.0,
                "min_lon": 37.0,
                "max_lon": 38.0
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == test_building.id
        assert data[0]["distance"] is None  # Для прямоугольника distance не рассчитывается

    def test_get_nearby_buildings_invalid_params(self, client):
        """Тест поиска зданий с невалидными параметрами"""
        # Неполные параметры для круга
        response = client.get(
            "/api/v1/buildings/nearby",
            params={"lat": 55.7558, "radius": 1000}  # Нет lon
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_nearby_buildings_no_results(self, client):
        """Тест поиска зданий без результатов"""
        response = client.get(
            "/api/v1/buildings/nearby",
            params={
                "lat": 60.0,  # Далеко от тестового здания
                "lon": 30.0,
                "radius": 1000
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 0