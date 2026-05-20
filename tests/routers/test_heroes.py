from fastapi import status

from app.schemas.hero import HeroResponse


class TestHeroes:
    """Test Heroes routes."""

    def _create_hero(
        self,
        client,
        name: str = "hero_name",
        level: int = 1,
        power: str = "hero_power",
        active: bool = False,
    ) -> HeroResponse:
        response = client.post(
            "/heroes",
            json={"name": name, "level": level, "power": power, "active": active},
        )
        assert response.status_code == status.HTTP_201_CREATED
        return HeroResponse.model_validate(response.json())

    def _create_active_mission(self, client, hero_id: int):
        response = client.post(
            "/missions",
            json={
                "title": "Protect city",
                "difficulty": 5,
                "completed": False,
                "hero_id": hero_id,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        return response.json()

    def _create_completed_mission(self, client, hero_id: int):
        response = client.post(
            "/missions",
            json={
                "title": "Rescued city",
                "difficulty": 5,
                "completed": True,
                "hero_id": hero_id,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        return response.json()

    def test_hero_creation(self, client, logged_in_user):
        """Test Hero post request."""
        hero_response = self._create_hero(client)

        assert hero_response.id >= 1
        assert hero_response.name == "hero_name"
        assert hero_response.level == 1
        assert hero_response.power == "hero_power"
        assert hero_response.active == False

    def test_hero_creation_requires_authenticated_user(self, client):
        """Test Hero post request without bearer token."""
        response = client.post(
            "/heroes",
            json={"name": "hero_name", "level": 1, "power": "hero_power", "active": False},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_hero_creation_rejects_invalid_payload(self, client, logged_in_user):
        """Test Hero post request with invalid body."""
        response = client.post(
            "/heroes",
            json={"name": "he", "level": 101, "power": "hp", "active": False},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_get_all_heroes(self, client, logged_in_user):
        """Test Heroes list request."""
        first_hero = self._create_hero(client, name="first_hero", power="first_power")
        second_hero = self._create_hero(client, name="second_hero", power="second_power")

        response = client.get("/heroes")

        assert response.status_code == status.HTTP_200_OK
        heroes = [HeroResponse.model_validate(hero) for hero in response.json()]
        assert [hero.id for hero in heroes] == [first_hero.id, second_hero.id]

    def test_get_all_heroes_supports_pagination(self, client, logged_in_user):
        """Test Heroes list pagination."""
        self._create_hero(client, name="first_hero", power="first_power")
        second_hero = self._create_hero(client, name="second_hero", power="second_power")

        response = client.get("/heroes", params={"skip": 1, "limit": 1})

        assert response.status_code == status.HTTP_200_OK
        heroes = [HeroResponse.model_validate(hero) for hero in response.json()]
        assert len(heroes) == 1
        assert heroes[0].id == second_hero.id

    def test_get_hero(self, client, logged_in_user):
        """Test Hero get request."""
        created_hero = self._create_hero(client)

        response = client.get(f"/heroes/{created_hero.id}")

        assert response.status_code == status.HTTP_200_OK
        hero_response = HeroResponse.model_validate(response.json())
        assert hero_response == created_hero

    def test_get_hero_returns_not_found_for_unknown_hero(self, client):
        """Test Hero get request for missing hero."""
        response = client.get("/heroes/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Hero not found"

    def test_hero_update(self, client, logged_in_user):
        """Test Hero update request."""
        created_hero = self._create_hero(client)

        response = client.patch(
            f"/heroes/{created_hero.id}",
            json={"name": "updated_hero", "level": 2, "power": "updated_power", "active": True},
        )

        assert response.status_code == status.HTTP_200_OK
        hero_response = HeroResponse.model_validate(response.json())
        assert hero_response.id == created_hero.id
        assert hero_response.name == "updated_hero"
        assert hero_response.level == 2
        assert hero_response.power == "updated_power"
        assert hero_response.active == True

    def test_hero_update_requires_authenticated_user(self, client):
        """Test Hero update request without bearer token."""
        response = client.patch(
            "/heroes/1",
            json={"name": "updated_hero", "level": 2, "power": "updated_power", "active": True},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_hero_update_returns_not_found_for_unknown_hero(self, client, logged_in_user):
        """Test Hero update request for missing hero."""
        response = client.patch(
            "/heroes/999",
            json={"name": "updated_hero", "level": 2, "power": "updated_power", "active": True},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Hero not found"

    def test_hero_update_rejects_invalid_payload(self, client, logged_in_user):
        """Test Hero update request with invalid body."""
        created_hero = self._create_hero(client)

        response = client.patch(
            f"/heroes/{created_hero.id}",
            json={"name": "no", "level": 0, "power": "up", "active": True},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_hero_deletion(self, client, logged_in_admin):
        """Test Hero delete request."""
        created_hero = self._create_hero(client)

        response = client.delete(f"/heroes/{created_hero.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        get_response = client.get(f"/heroes/{created_hero.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_hero_deletion_requires_authenticated_user(self, client):
        """Test Hero delete request without bearer token."""
        response = client.delete("/heroes/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_hero_deletion_requires_admin_user(self, client, logged_in_user):
        """Test Hero delete request without admin privileges."""
        created_hero = self._create_hero(client)

        response = client.delete(f"/heroes/{created_hero.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Admin privileges required"

    def test_hero_deletion_returns_not_found_for_unknown_hero(self, client, logged_in_admin):
        """Test Hero delete request for missing hero."""
        response = client.delete("/heroes/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Hero not found"

    def test_hero_deletion_rejects_hero_with_active_mission(self, client, logged_in_admin):
        """Test Hero delete request when hero has an active mission."""
        created_hero = self._create_hero(client)
        self._create_active_mission(client, created_hero.id)

        response = client.delete(f"/heroes/{created_hero.id}")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "Hero has active mission(s)"

    def test_hero_deletion_allows_hero_with_only_completed_missions(self, client, logged_in_admin):
        """Test Hero delete request when hero has only completed missions."""
        created_hero = self._create_hero(client)
        self._create_completed_mission(client, created_hero.id)

        response = client.delete(f"/heroes/{created_hero.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        get_response = client.get(f"/heroes/{created_hero.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
