from fastapi import APIRouter, status, HTTPException
from sqlmodel import select
from app.models.models import Hero, Mission
from app.depedencies import CurrentUser, CurrentAdmin, SessionDep, Page
from app.schemas.mission import MissionUpdateRequest, MissionCreateRequest, MissionResponse

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
def create_mission(mission: MissionCreateRequest, session: SessionDep, _user: CurrentUser):
    hero = session.get(Hero, mission.hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")

    mission = Mission(
        title=mission.title.strip(),
        difficulty=mission.difficulty,
        completed=mission.completed,
        hero_id=mission.hero_id,
    )
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@router.get("", response_model=list[MissionResponse])
def get_all_missions(session: SessionDep, page: Page):
    return session.exec(select(Mission).offset(page["skip"]).limit(page["limit"])).all()


@router.get("/{mission_id}", response_model=MissionResponse)
def get_mission(mission_id: int, session: SessionDep):
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    return mission


@router.patch("/{mission_id}", response_model=MissionResponse)
def update_mission(mission_id: int, patch: MissionUpdateRequest, session: SessionDep, _user: CurrentUser):
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")

    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(mission, field, value)

    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(mission_id: int, session: SessionDep, _admin: CurrentAdmin):
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")

    session.delete(mission)
    session.commit()