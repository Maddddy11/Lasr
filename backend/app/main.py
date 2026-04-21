from __future__ import annotations

from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import init_db, insert_event, list_events
from .pii import redact_pii
from .providers import GeminiProvider, GroqProvider, LMStudioProvider
from .routing import choose_provider, estimate_complexity, estimate_cost_and_carbon
from .schemas import PolicyView, RouteRequest, RouteResponse

load_dotenv()
settings = get_settings()
init_db(settings.db_path)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/policies", response_model=PolicyView)
def policies() -> PolicyView:
    return PolicyView(
        role_tiers=["Intern", "Employee", "Executive", "Admin"],
        pii_policy="If PII is detected and role is not Admin, route to LM Studio and redact before provider call.",
        fallback_policy="If Gemini/Groq keys are missing, route falls back to LM Studio.",
    )


@app.get("/v1/events")
def events(limit: int = 100) -> list[dict]:
    return list_events(settings.db_path, limit=limit)


@app.post("/v1/route", response_model=RouteResponse)
def route(request: RouteRequest) -> RouteResponse:
    redacted_prompt, pii_counts, pii_types = redact_pii(request.prompt)
    redaction_count = sum(pii_counts.values())

    complexity_score = estimate_complexity(request.prompt, request.role)

    decision = choose_provider(
        role=request.role,
        complexity_score=complexity_score,
        pii_detected=bool(pii_types),
        gemini_available=bool(settings.gemini_api_key),
        groq_available=bool(settings.groq_api_key),
        lmstudio_model=settings.lmstudio_model,
        gemini_model=settings.gemini_model,
        groq_model=settings.groq_model,
    )

    estimated_cost, estimated_carbon = estimate_cost_and_carbon(decision.provider, redacted_prompt)

    providers = {
        "lmstudio": LMStudioProvider(settings.lmstudio_base_url),
        "gemini": GeminiProvider(settings.gemini_api_key),
        "groq": GroqProvider(settings.groq_api_key),
    }

    provider_result = providers[decision.provider].invoke(decision.model, redacted_prompt)

    event_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": request.user_id,
        "role": request.role,
        "provider": decision.provider,
        "model": decision.model,
        "complexity_score": complexity_score,
        "pii_types": pii_types,
        "redaction_count": redaction_count,
        "estimated_cost": estimated_cost,
        "estimated_carbon": estimated_carbon,
        "latency_ms": provider_result.latency_ms,
        "status": provider_result.status,
    }
    insert_event(settings.db_path, event_payload)

    return RouteResponse(
        provider=decision.provider,
        model=decision.model,
        complexity_score=complexity_score,
        pii_types=pii_types,
        redaction_count=redaction_count,
        redacted_prompt=redacted_prompt,
        estimated_cost=estimated_cost,
        estimated_carbon=estimated_carbon,
        latency_ms=provider_result.latency_ms,
        status=provider_result.status,
        response=provider_result.response,
    )
