from backend.app.routing import choose_provider, estimate_complexity


def test_non_admin_with_pii_forces_lmstudio() -> None:
    complexity = estimate_complexity("Please summarize this", "Employee")
    decision = choose_provider(
        role="Employee",
        complexity_score=complexity,
        pii_detected=True,
        gemini_available=True,
        groq_available=True,
        lmstudio_model="local-model",
        gemini_model="gemini-model",
        groq_model="groq-model",
    )

    assert decision.provider == "lmstudio"


def test_admin_with_pii_can_use_cloud() -> None:
    complexity = estimate_complexity("```python\nprint('hello')\n```", "Admin")
    decision = choose_provider(
        role="Admin",
        complexity_score=complexity,
        pii_detected=True,
        gemini_available=True,
        groq_available=True,
        lmstudio_model="local-model",
        gemini_model="gemini-model",
        groq_model="groq-model",
    )

    assert decision.provider == "gemini"


def test_missing_cloud_keys_fallback_to_lmstudio() -> None:
    complexity = estimate_complexity("Simple question", "Intern")
    decision = choose_provider(
        role="Intern",
        complexity_score=complexity,
        pii_detected=False,
        gemini_available=False,
        groq_available=False,
        lmstudio_model="local-model",
        gemini_model="gemini-model",
        groq_model="groq-model",
    )

    assert decision.provider == "lmstudio"
