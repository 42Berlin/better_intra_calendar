from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Versions(BaseModel):
    large: Optional[str]
    medium: Optional[str]
    small: Optional[str]
    micro: Optional[str]


class Image(BaseModel):
    link: Optional[str]
    versions: Optional[Versions]


class User(BaseModel):
    id: Optional[int]
    email: Optional[str]
    login: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    usual_first_name: Optional[str]
    url: Optional[str]
    phone: Optional[str]
    displayname: Optional[str]
    image: Optional[Image]
    staff_: Optional[bool] = Field(..., alias='staff?')
    correction_point: Optional[int]
    pool_month: Optional[str]
    pool_year: Optional[str]
    location: Optional[str]
    wallet: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]


class CommunityService(BaseModel):
    id: Optional[int]
    duration: Optional[int]
    schedule_at: Optional[str]
    occupation: Optional[str]
    state: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class Closer(BaseModel):
    id: Optional[int]
    login: Optional[str]
    url: Optional[str]


class IntraCloseModel(BaseModel):
    id: Optional[int] = None
    reason: Optional[str] = None
    state: Optional[str] = None
    user: Optional[User] = None
    kind: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    community_services: Optional[List[CommunityService]] = None
    closer: Optional[Closer] = None
