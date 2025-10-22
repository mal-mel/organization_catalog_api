from fastapi import status


class TestActivities:
    """Тесты для эндпоинтов Activities"""

    def test_get_activities_tree(self, client, test_activity_tree):
        """Тест получения дерева активностей"""
        response = client.get("/api/v1/activities/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data) == 1
        assert data[0]["name"] == "Тестовая корневая"
        assert len(data[0]["children"]) == 1
        assert data[0]["children"][0]["name"] == "Тестовая дочерняя"
        assert len(data[0]["children"][0]["children"]) == 1
        assert data[0]["children"][0]["children"][0]["name"] == "Тестовая внучка"

    def test_get_activities_tree_with_max_depth(self, client, test_activity_tree):
        """Тест ограничения глубины дерева"""
        response = client.get("/api/v1/activities/?max_depth=1")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Проверяем, что дети есть, но внуков нет
        assert len(data[0]["children"]) == 1
        assert len(data[0]["children"][0]["children"]) == 0

    def test_get_activity_detail(self, client, test_activity_tree, test_organization):
        """Тест получения деталей активности"""
        activity = test_activity_tree["root"]

        response = client.get(f"/api/v1/activities/{activity.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == activity.id
        assert data["name"] == activity.name
        assert data["parent_id"] is None
        assert len(data["children"]) == 1
        assert data["organizations_count"] == 1

    def test_get_nonexistent_activity(self, client):
        """Тест получения несуществующей активности"""
        response = client.get("/api/v1/activities/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
