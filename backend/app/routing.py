from __future__ import annotations

from dataclasses import dataclass

from .schemas import Role

ROLE_WEIGHT = {
    "Intern": 1.0,
    "Employee": 1.2,
    "Executive": 1.5,
    "Admin": 1.8,
}

PROVIDER_RATE = {
    "lmstudio": {"cost": 0.0002, "carbon": 0.00015},
    "groq": {"cost": 0.0004, "carbon": 0.00009},
    "gemini": {"cost": 0.0008, "carbon": 0.00011},
}


@dataclass(frozen=True)
class RouteDecision:
    provider: str
    model: str
    complexity_score: float
    estimated_cost: float
    estimated_carbon: float
    reason: str


def estimate_complexity(prompt: str, role: Role) -> float:
    words = len(prompt.split())
    chars = len(prompt)
    code_block_hits = prompt.count("```") // 2
    keyword_hits = sum(1 for k in ("optimize", "architecture", "benchmark", "security", "refactor") if k in prompt.lower())
    base = (words / 20.0) + (chars / 500.0) + (code_block_hits * 1.5) + (keyword_hits * 0.8)
    return round(base * ROLE_WEIGHT[role], 2)


def estimate_usage(prompt: str) -> int:
    return max(1, len(prompt) // 4)


def estimate_cost_and_carbon(provider: str, prompt: str) -> tuple[float, float]:
    tokens = estimate_usage(prompt)
    rates = PROVIDER_RATE[provider]
    return round(tokens * rates["cost"], 6), round(tokens * rates["carbon"], 6)


def choose_provider(
    *,
    role: Role,
    complexity_score: float,
    pii_detected: bool,
    gemini_available: bool,
    groq_available: bool,
    lmstudio_model: str,
    gemini_model: str,
    groq_model: str,
) -> RouteDecision:
    if pii_detected and role != "Admin":
        return RouteDecision(
            provider="lmstudio",
            model=lmstudio_model,
            complexity_score=complexity_score,
            estimated_cost=0.0,
            estimated_carbon=0.0,
            reason="PII detected for non-admin; forcing local provider",
        )

    if role in {"Executive", "Admin"} or complexity_score >= 4.5:
        if gemini_available:
            return RouteDecision("gemini", gemini_model, complexity_score, 0.0, 0.0, "High-complexity or privileged role")
        if groq_available:
            return RouteDecision("groq", groq_model, complexity_score, 0.0, 0.0, "Gemini unavailable fallback")
        return RouteDecision("lmstudio", lmstudio_model, complexity_score, 0.0, 0.0, "Cloud keys unavailable fallback")

    if complexity_score < 4.5 and groq_available:
        return RouteDecision("groq", groq_model, complexity_score, 0.0, 0.0, "Cost-first routing for lower complexity")

    if gemini_available:
        return RouteDecision("gemini", gemini_model, complexity_score, 0.0, 0.0, "Groq unavailable fallback")

    return RouteDecision("lmstudio", lmstudio_model, complexity_score, 0.0, 0.0, "Cloud keys unavailable fallback")
