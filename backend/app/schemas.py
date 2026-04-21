from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Role = Literal["Intern", "Employee", "Executive", "Admin"]


class RouteRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    role: Role
    prompt: str = Field(..., min_length=1)


class RouteResponse(BaseModel):
    provider: str
    model: str
    complexity_score: float
    pii_types: list[str]
    redaction_count: int
    redacted_prompt: str
    estimated_cost: float
    estimated_carbon: float
    status: str
    latency_ms: int
    response: Any | None = None


class PolicyView(BaseModel):
    role_tiers: list[str]
    pii_policy: str
    fallback_policy: str


class EventRecord(BaseModel):
    timestamp: str
    user_id: str
    role: str
    provider: str
    model: str
    complexity_score: float
    pii_types: list[str]
    redaction_count: int
    estimated_cost: float
    estimated_carbon: float
    latency_ms: int
    status: str
