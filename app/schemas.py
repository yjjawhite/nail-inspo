from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class TagBase(BaseModel):
    name: str
    category: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class InspirationBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    style: Optional[str] = None
    color_palette: Optional[str] = None
    nail_shape: Optional[str] = None
    length: Optional[str] = None
    price_estimate: Optional[float] = None
    duration_estimate_minutes: Optional[int] = None
    tags: List[str] = []


class InspirationCreate(InspirationBase):
    pass


class InspirationRead(InspirationBase):
    id: int
    tags: List[TagRead]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: str
    display_name: str


class UserRead(BaseModel):
    id: int
    email: str
    display_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class FavoriteCreate(BaseModel):
    user_id: int
    inspiration_id: int


class FavoriteRead(BaseModel):
    id: int
    user: UserRead
    inspiration: InspirationRead
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CommunicationCardCreate(BaseModel):
    inspiration_id: int
    notes: Optional[str] = None
    risk_notes: Optional[str] = None
    material_suggestions: Optional[str] = None
    timing_estimate: Optional[str] = None
    difficulty: Optional[int] = None


class CommunicationCardRead(BaseModel):
    id: int
    inspiration: InspirationRead
    notes: Optional[str] = None
    risk_notes: Optional[str] = None
    material_suggestions: Optional[str] = None
    timing_estimate: Optional[str] = None
    difficulty: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
