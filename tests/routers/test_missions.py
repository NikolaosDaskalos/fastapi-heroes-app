from fastapi import status

from app.schemas.hero import HeroResponse
from app.schemas.mission import MissionResponse

HEROES_URL = "/heroes"
MISSIONS_URL = "/missions"

DEFAULT_HERO_PAYLOAD = {
    "name": "hero_name",
    "level": 1,
    "power": "hero_power",
    "active": True,
}

DEFAULT_MISSION_PAYLOAD = {
    "title": "Protect city",
    "difficulty": 5,
    "completed": False,
}

UPDATED_MISSION_PAYLOAD = {
    "title": "Updated mission",
    "difficulty": 8,
    "completed": True,
}

INVALID_MISSION_PAYLOAD = {
    "title": "bad",
    "difficulty": 11,
    "completed": False,
    "hero_id": 0,
}


def hero_payload(**overrides):
    return DEFAULT_HERO_PAYLOAD | overrides


def mission_payload(hero_id: int, **overrides):
    return DEFAULT_MISSION_PAYLOAD | {"hero_id": hero_id} | overrides


def create_hero(client, **overrides) -> HeroResponse:
    response = client.post(HEROES_URL, json=hero_payload(**overrides))
    assert response.status_code == status.HTTP_201_CREATED
    return HeroResponse.model_validate(response.json())


def create_mission(client, hero_id: int, **overrides) -> MissionResponse:
    response = client.post(MISSIONS_URL, json=mission_payload(hero_id, **overrides))
    assert response.status_code == status.HTTP_201_CREATED
    return MissionResponse.model_validate(response.json())


def mission_responses(response):
    return [MissionResponse.model_validate(mission) for mission in response.json()]


class TestMissions:
    """Test Missions routes."""

    def test_mission_creation(self, client, logged_in_user):
        """Test Mission post request."""
        hero = create_hero(client)

        response = client.post(
            MISSIONS_URL,
            json=mission_payload(hero.id, title="  Protect city  "),
        )

        assert response.status_code == status.HTTP_201_CREATED
        mission_response = MissionResponse.model_validate(response.json())
        assert mission_response.id >= 1
        assert mission_response.title == "Protect city"
        assert mission_response.difficulty == 5
        assert mission_response.completed is False
        assert mission_response.hero_id == hero.id

    def test_mission_creation_defaults_completed_to_false(self, client, logged_in_user):
        """Test Mission post request default completed value."""
        hero = create_hero(client)
        payload = {"title": "Protect city", "difficulty": 5, "hero_id": hero.id}

        response = client.post(MISSIONS_URL, json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        mission_response = MissionResponse.model_validate(response.json())
        assert mission_response.completed is False

    def test_mission_creation_requires_authenticated_user(self, client):
        """Test Mission post request without bearer token."""
        response = client.post(MISSIONS_URL, json=mission_payload(hero_id=1))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_mission_creation_returns_not_found_for_unknown_hero(
        self,
        client,
        logged_in_user,
    ):
        """Test Mission post request for missing hero."""
        response = client.post(MISSIONS_URL, json=mission_payload(hero_id=999))

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Hero not found"

    def test_mission_creation_rejects_invalid_payload(self, client, logged_in_user):
        """Test Mission post request with invalid body."""
        response = client.post(MISSIONS_URL, json=INVALID_MISSION_PAYLOAD)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_get_all_missions(self, client, logged_in_user):
        """Test Missions list request."""
        first_hero = create_hero(client, name="first_hero", power="first_power")
        second_hero = create_hero(client, name="second_hero", power="second_power")
        first_mission = create_mission(client, first_hero.id, title="First mission")
        second_mission = create_mission(client, second_hero.id, title="Second mission")

        response = client.get(MISSIONS_URL)

        assert response.status_code == status.HTTP_200_OK
        missions = mission_responses(response)
        assert [mission.id for mission in missions] == [
            first_mission.id,
            second_mission.id,
        ]

    def test_get_all_missions_supports_pagination(self, client, logged_in_user):
        """Test Missions list pagination."""
        first_hero = create_hero(client, name="first_hero", power="first_power")
        second_hero = create_hero(client, name="second_hero", power="second_power")
        create_mission(client, first_hero.id, title="First mission")
        second_mission = create_mission(client, second_hero.id, title="Second mission")

        response = client.get(MISSIONS_URL, params={"skip": 1, "limit": 1})

        assert response.status_code == status.HTTP_200_OK
        missions = mission_responses(response)
        assert len(missions) == 1
        assert missions[0].id == second_mission.id

    def test_get_mission(self, client, logged_in_user):
        """Test Mission get request."""
        hero = create_hero(client)
        created_mission = create_mission(client, hero.id)

        response = client.get(f"{MISSIONS_URL}/{created_mission.id}")

        assert response.status_code == status.HTTP_200_OK
        mission_response = MissionResponse.model_validate(response.json())
        assert mission_response == created_mission

    def test_get_mission_returns_not_found_for_unknown_mission(self, client):
        """Test Mission get request for missing mission."""
        response = client.get(f"{MISSIONS_URL}/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Mission not found"

    def test_mission_update(self, client, logged_in_user):
        """Test Mission update request."""
        hero = create_hero(client)
        created_mission = create_mission(client, hero.id)

        response = client.patch(
            f"{MISSIONS_URL}/{created_mission.id}",
            json=UPDATED_MISSION_PAYLOAD,
        )

        assert response.status_code == status.HTTP_200_OK
        mission_response = MissionResponse.model_validate(response.json())
        assert mission_response.id == created_mission.id
        assert mission_response.title == "Updated mission"
        assert mission_response.difficulty == 8
        assert mission_response.completed is True
        assert mission_response.hero_id == hero.id

    def test_mission_update_requires_authenticated_user(self, client):
        """Test Mission update request without bearer token."""
        response = client.patch(f"{MISSIONS_URL}/1", json=UPDATED_MISSION_PAYLOAD)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_mission_update_returns_not_found_for_unknown_mission(
        self,
        client,
        logged_in_user,
    ):
        """Test Mission update request for missing mission."""
        response = client.patch(f"{MISSIONS_URL}/999", json=UPDATED_MISSION_PAYLOAD)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Mission not found"

    def test_mission_update_rejects_invalid_payload(self, client, logged_in_user):
        """Test Mission update request with invalid body."""
        hero = create_hero(client)
        created_mission = create_mission(client, hero.id)
        invalid_update_payload = {
            "title": "bad",
            "difficulty": 0,
            "completed": True,
        }

        response = client.patch(
            f"{MISSIONS_URL}/{created_mission.id}",
            json=invalid_update_payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_mission_deletion(self, client, logged_in_admin):
        """Test Mission delete request."""
        hero = create_hero(client)
        created_mission = create_mission(client, hero.id)

        response = client.delete(f"{MISSIONS_URL}/{created_mission.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        get_response = client.get(f"{MISSIONS_URL}/{created_mission.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_mission_deletion_requires_authenticated_user(self, client):
        """Test Mission delete request without bearer token."""
        response = client.delete(f"{MISSIONS_URL}/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_mission_deletion_requires_admin_user(self, client, logged_in_user):
        """Test Mission delete request without admin privileges."""
        hero = create_hero(client)
        created_mission = create_mission(client, hero.id)

        response = client.delete(f"{MISSIONS_URL}/{created_mission.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Admin privileges required"

    def test_mission_deletion_returns_not_found_for_unknown_mission(
        self,
        client,
        logged_in_admin,
    ):
        """Test Mission delete request for missing mission."""
        response = client.delete(f"{MISSIONS_URL}/999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Mission not found"
