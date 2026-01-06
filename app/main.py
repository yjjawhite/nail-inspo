from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .config import get_settings
from .database import Base, SessionLocal, engine
from .models import CommunicationCard, Inspiration, Tag, User, inspiration_tag_table, Favorite
from .schemas import (
    CommunicationCardCreate,
    CommunicationCardRead,
    FavoriteCreate,
    FavoriteRead,
    InspirationCreate,
    InspirationRead,
    TagCreate,
    TagRead,
    UserCreate,
    UserRead,
)

settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)


# Create tables for a simple bootstrap experience.
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "environment": settings.app_env}


@app.get("/tags", response_model=List[TagRead], tags=["tags"])
def list_tags(db: Session = Depends(get_db)):
    tags = db.execute(select(Tag)).scalars().all()
    return tags


@app.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED, tags=["tags"])
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(Tag).where(Tag.name == tag.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists")
    db_tag = Tag(name=tag.name, category=tag.category)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.get("/inspirations", response_model=List[InspirationRead], tags=["inspirations"])
def list_inspirations(
    tag: Optional[List[str]] = Query(default=None, description="Filter by tag names"),
    style: Optional[str] = Query(default=None, description="Filter by style"),
    db: Session = Depends(get_db),
):
    query = select(Inspiration).options(joinedload(Inspiration.tags))
    if style:
        query = query.where(Inspiration.style == style)
    if tag:
        query = query.join(inspiration_tag_table).join(Tag).where(Tag.name.in_(tag))
    inspirations = db.execute(query).unique().scalars().all()
    return inspirations


@app.post("/inspirations", response_model=InspirationRead, status_code=status.HTTP_201_CREATED, tags=["inspirations"])
def create_inspiration(payload: InspirationCreate, db: Session = Depends(get_db)):
    db_tags = []
    for tag_name in payload.tags:
        tag = db.execute(select(Tag).where(Tag.name == tag_name)).scalar_one_or_none()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.flush()
        db_tags.append(tag)

    inspiration = Inspiration(
        title=payload.title,
        description=payload.description,
        image_url=str(payload.image_url) if payload.image_url else None,
        style=payload.style,
        color_palette=payload.color_palette,
        nail_shape=payload.nail_shape,
        length=payload.length,
        price_estimate=payload.price_estimate,
        duration_estimate_minutes=payload.duration_estimate_minutes,
        tags=db_tags,
    )
    db.add(inspiration)
    db.commit()
    db.refresh(inspiration)
    return inspiration


@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(User).where(User.email == user.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    db_user = User(email=user.email, display_name=user.display_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/favorites", response_model=FavoriteRead, status_code=status.HTTP_201_CREATED, tags=["favorites"])
def create_favorite(favorite: FavoriteCreate, db: Session = Depends(get_db)):
    user = db.get(User, favorite.user_id)
    inspiration = db.get(Inspiration, favorite.inspiration_id)
    if not user or not inspiration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or inspiration not found")

    existing = (
        db.execute(
            select(Favorite).where(
                Favorite.user_id == favorite.user_id,
                Favorite.inspiration_id == favorite.inspiration_id,
            )
        )
        .scalar_one_or_none()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already favorited")

    db_favorite = Favorite(user_id=favorite.user_id, inspiration_id=favorite.inspiration_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


@app.get("/users/{user_id}/favorites", response_model=List[InspirationRead], tags=["favorites"])
def list_favorites(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    favorites_query = (
        select(Inspiration)
        .join(Favorite, Favorite.inspiration_id == Inspiration.id)
        .options(joinedload(Inspiration.tags))
        .where(Favorite.user_id == user_id)
    )
    favorites = db.execute(favorites_query).unique().scalars().all()
    return favorites


@app.post(
    "/communication-cards",
    response_model=CommunicationCardRead,
    status_code=status.HTTP_201_CREATED,
    tags=["communication_cards"],
)
def create_communication_card(payload: CommunicationCardCreate, db: Session = Depends(get_db)):
    inspiration = db.get(Inspiration, payload.inspiration_id)
    if not inspiration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspiration not found")

    card = CommunicationCard(
        inspiration_id=payload.inspiration_id,
        notes=payload.notes or _default_notes(inspiration),
        risk_notes=payload.risk_notes or "提前沟通时间预算，复杂元素可能需要额外耗时。",
        material_suggestions=payload.material_suggestions
        or "如缺少同款钻/色号，可选相近色或同色系简化版。",
        timing_estimate=payload.timing_estimate
        or _format_timing(inspiration.duration_estimate_minutes),
        difficulty=payload.difficulty or _derive_difficulty(inspiration),
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def _format_timing(duration_estimate_minutes: Optional[int]) -> Optional[str]:
    if not duration_estimate_minutes:
        return None
    hours = duration_estimate_minutes / 60
    if hours < 1:
        return f"约 {duration_estimate_minutes} 分钟"
    return f"约 {hours:.1f} 小时"


def _derive_difficulty(inspiration: Inspiration) -> int:
    base = 2
    if inspiration.tags:
        complex_tags = {"猫眼", "贴钻", "渐变", "闪粉"}
        if any(tag.name in complex_tags for tag in inspiration.tags):
            base += 1
    return min(base, 5)


def _default_notes(inspiration: Inspiration) -> str:
    parts = ["底色: 优先选择与图片接近的色号"]
    if inspiration.nail_shape:
        parts.append(f"甲型: {inspiration.nail_shape}")
    if inspiration.length:
        parts.append(f"长度: {inspiration.length}")
    if inspiration.style:
        parts.append(f"风格: {inspiration.style}")
    return "；".join(parts)
