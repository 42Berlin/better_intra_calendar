from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Field42cursus(BaseModel):
    level: Optional[float] = None


class CPiscine(BaseModel):
    level: Optional[float] = None


class Cursus(BaseModel):
    field_42cursus: Optional[Field42cursus] = Field(None, alias='42cursus')
    C_Piscine: Optional[CPiscine] = Field(None, alias='C Piscine')


class Versions(BaseModel):
    large: Optional[str] = None
    medium: Optional[str] = None
    small: Optional[str] = None
    micro: Optional[str] = None


class Image(BaseModel):
    link: Optional[str] = None
    versions: Optional[Versions] = None


class User(BaseModel):
    usual_full_name: Optional[str] = None
    location: Optional[str] = None
    cursus: Optional[List[Cursus]] = None
    login: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    image: Optional[Image] = None


class Image1(BaseModel):
    url: Optional[str] = None


class IntraTransactionModel(BaseModel):
    id: Optional[int] = None
    value: Optional[int] = None
    user_id: Optional[int] = None
    transactable_id: Optional[int] = None
    transactable_type: Optional[str] = None
    created_at: Optional[str] = None
    reason: Optional[str] = None
    user: Optional[User] = None
