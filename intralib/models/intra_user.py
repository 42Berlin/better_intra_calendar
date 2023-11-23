from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class Versions(BaseModel):
    large: str
    medium: str
    small: str
    micro: str


class Image(BaseModel):
    link: str
    versions: Versions


class IntraUserModel(BaseModel):
    id: Optional[int] = None
    email: Optional[str] = None
    login: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    usual_first_name: Optional[str] = None
    url: Optional[str] = None
    phone: Optional[str] = None
    displayname: Optional[str] = None
    image: Optional[Image] = None
    staff_: Optional[bool] = Field(..., alias='staff?')
    correction_point: Optional[int] = None
    pool_month: Optional[str] = None
    pool_year: Optional[str] = None
    location: Optional[str] = None
    wallet: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
