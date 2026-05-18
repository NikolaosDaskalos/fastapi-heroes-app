from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.depedencies import CurrentUser, SessionDep, Page, CurrentAdmin
from app.schemas.hero import HeroResponse, HeroCreateRequest, HeroUpdateRequest
from app.models.models import Hero, Mission

router = APIRouter(prefix="/heroes", tags=["heroes"])


@router.post("", response_model=HeroResponse, status_code=status.HTTP_201_CREATED)
def create_hero(data: HeroCreateRequest, session: SessionDep, _user: CurrentUser):
    """Create a new hero."""
    hero = Hero(**data.model_dump())
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.get("", response_model=list[HeroResponse])
def get_all_heroes(session: SessionDep, page: Page):
    return session.exec(select(Hero).offset(page['skip']).limit(page['limit'])).all()


@router.get("/{hero_id}", response_model=HeroResponse)
def get_hero(session: SessionDep, hero_id: int):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hero not found")
    return hero


@router.patch("/{hero_id}", response_model=HeroResponse)
def update_hero(patch: HeroUpdateRequest, hero_id: int, session: SessionDep, _user: CurrentUser):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hero not found")

    for field, value in patch.model_dump(exclude_unset=True).items():
        setattr(hero, field, value)

    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hero(session: SessionDep, hero_id: int, _admin: CurrentAdmin):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hero not found")

    active_mission = session.exec(
        select(Mission.id)
        .where(Mission.hero_id == hero_id, Mission.completed == False)
        .limit(1)).first()

    if active_mission:
        raise HTTPException(status.HTTP_409_CONFLICT, "Hero has active mission(s)")

    session.delete(hero)
    session.commit()
