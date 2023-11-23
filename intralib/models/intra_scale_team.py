from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class Team(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    locked_at: Optional[str] = None
    closed_at: Optional[str] = None
    final_mark: Optional[Any] = None
    repo_url: Optional[str] = None
    repo_uuid: Optional[str] = None
    deadline_at: Optional[Any] = None
    terminating_at: Optional[str] = None
    project_session_id: Optional[int] = None
    status: Optional[str] = None


class Flag(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    positive: Optional[bool] = None
    icon: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Scale(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    comment: Optional[str] = None
    introduction_md: Optional[str] = None
    disclaimer_md: Optional[str] = None
    guidelines_md: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    evaluation_id: Optional[int] = None
    is_primary: Optional[bool] = None
    correction_number: Optional[int] = None
    duration: Optional[int] = None
    manual_subscription: Optional[bool] = None
    is_external: Optional[bool] = None
    free: Optional[bool] = None


class Project(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None


class Versions(BaseModel):
    large: Optional[str] = None
    medium: Optional[str] = None
    small: Optional[str] = None
    micro: Optional[str] = None


class Image(BaseModel):
    link: Optional[str] = None
    versions: Optional[Versions] = None


class User(BaseModel):
    id: Optional[int] = None
    email: Optional[str] = None
    login: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    usual_first_name: Optional[Any] = None
    url: Optional[str] = None
    phone: Optional[str] = None
    displayname: Optional[str] = None
    image: Optional[Image] = None
    staff_: Optional[bool] = Field(..., alias='staff?')
    correction_point: Optional[int] = None
    pool_month: Optional[str] = None
    pool_year: Optional[str] = None
    location: Optional[Any] = None
    wallet: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class IntraScaleTeamModel(BaseModel):
    id: Optional[int] = None
    team: Optional[Team] = None
    truant: Optional[Any] = None
    flag: Optional[Flag] = None
    scale: Optional[Scale] = None
    begin_at: Optional[str] = None
    comment: Optional[Any] = None
    feedback: Optional[Any] = None
    feedback_rating: Optional[Any] = None
    final_mark: Optional[Any] = None
    token: Optional[Any] = None
    ip: Optional[Any] = None
    filled_at: Optional[Any] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    project: Optional[Project] = None
    user: Optional[User] = None


class RandomEvaluation(BaseModel):
    evaluator_id: Optional[int] = None
    evaluator_login: Optional[str] = None
    evaluee_login: Optional[str] = None
    project_id: Optional[int] = None
    slot_start: Optional[str] = None
    slot_end: Optional[str] = None