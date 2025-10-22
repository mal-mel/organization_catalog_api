from fastapi import status


class TestOrganizations:
    """Тесты для эндпоинтов Organizations"""

    def test_get_organizations(self, client, test_organization):
        """Тест получения списка организаций"""
        response = client.get("/api/v1/organizations/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["name"] == test_organization.name
        assert len(data[0]["phone_numbers"]) == 1
        assert len(data[0]["activities"]) == 1

    def test_get_organization_detail(self, client, test_organization):
        """Тест получения деталей организации"""
        response = client.get(f"/api/v1/organizations/{test_organization.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == test_organization.id
        assert data["name"] == test_organization.name
        assert data["building_id"] == test_organization.building_id
        assert len(data["phone_numbers"]) == 1
        assert data["phone_numbers"][0]["number"] == "123-456-789"
        assert len(data["activities"]) == 1

    def test_get_nonexistent_organization(self, client):
        """Тест получения несуществующей организации"""
        response = client.get("/api/v1/organizations/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_search_organizations_by_activity(self, client, test_organization, test_activity_tree):
        """Тест поиска организаций по виду деятельности"""
        activity = test_activity_tree["root"]

        response = client.get(
            "/api/v1/organizations/",
            params={"activity_id": activity.id}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == test_organization.id

    def test_search_organizations_by_activity_tree(self, client, test_organization, test_activity_tree):
        """Тест поиска организаций по дереву деятельностей"""
        # Ищем по корневой активности, должна найтись организация с дочерней активностью
        root_activity = test_activity_tree["root"]

        response = client.get(
            "/api/v1/organizations/",
            params={"activity_id": root_activity.id}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == test_organization.id

    def test_search_organizations_by_name(self, client, test_organization):
        """Тест поиска организаций по названию"""
        response = client.get(
            "/api/v1/organizations/",
            params={"name": "Тестовая"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == test_organization.id

    def test_search_organizations_by_name_no_results(self, client):
        """Тест поиска организаций по несуществующему названию"""
        response = client.get(
            "/api/v1/organizations/",
            params={"name": "Несуществующая"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 0

    def test_search_organizations_in_circle_area(self, client, test_organization, test_building):
        """Тест поиска организаций в круговой области"""
        response = client.get(
            "/api/v1/organizations/",
            params={"in_area": f"circle:{test_building.latitude},{test_building.longitude},1000"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == test_organization.id

    def test_search_organizations_in_rectangle_area(self, client, test_organization, test_building):
        """Тест поиска организаций в прямоугольной области"""
        response = client.get(
            "/api/v1/organizations/",
            params={
                "in_area": f"rect:{test_building.latitude - 0.1},{test_building.longitude - 0.1},{test_building.latitude + 0.1},{test_building.longitude + 0.1}"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == test_organization.id

    def test_search_organizations_invalid_area_format(self, client):
        """Тест поиска организаций с невалидным форматом области"""
        response = client.get(
            "/api/v1/organizations/",
            params={"in_area": "invalid:format"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_organization(self, client, test_building, test_activity_tree):
        """Тест создания организации"""
        organization_data = {
            "name": "Новая тестовая организация",
            "building_id": test_building.id,
            "phone_numbers": [
                {"number": "111-222-333"},
                {"number": "444-555-666"}
            ],
            "activity_ids": [test_activity_tree["root"].id]
        }

        response = client.post("/api/v1/organizations/", json=organization_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["name"] == organization_data["name"]
        assert data["building_id"] == test_building.id
        assert len(data["phone_numbers"]) == 2
        assert len(data["activities"]) == 1

    def test_create_organization_invalid_building(self, client):
        """Тест создания организации с невалидным зданием"""
        organization_data = {
            "name": "Организация с несуществующим зданием",
            "building_id": 999,
            "phone_numbers": [],
            "activity_ids": []
        }

        response = client.post("/api/v1/organizations/", json=organization_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_organization(self, client, test_organization):
        """Тест обновления организации"""
        update_data = {
            "name": "Обновленное название организации"
        }

        response = client.put(
            f"/api/v1/organizations/{test_organization.id}",
            json=update_data
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["name"] == "Обновленное название организации"
        assert data["id"] == test_organization.id

    def test_delete_organization(self, client, db_session):
        """Тест удаления организации"""
        from app.models.organization import Organization
        from app.models.building import Building

        # Создаем временную организацию для удаления
        building = Building(
            address="г. Москва, ул. Временная 1",
            latitude=55.0,
            longitude=37.0
        )
        db_session.add(building)
        db_session.flush()

        organization = Organization(
            name="Организация для удаления",
            building_id=building.id
        )
        db_session.add(organization)
        db_session.commit()

        response = client.delete(f"/api/v1/organizations/{organization.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем, что организация удалена
        response = client.get(f"/api/v1/organizations/{organization.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND