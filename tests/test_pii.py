from backend.app.pii import redact_pii


def test_redact_multiple_pii_types() -> None:
    text = (
        "Contact me at user@example.com or +1 (555) 111-2222. "
        "SSN 123-45-6789 and card 4111 1111 1111 1111. "
        "Token sk-abcdefghijklmnop1234567890."
    )

    redacted, counts, pii_types = redact_pii(text)

    assert "user@example.com" not in redacted
    assert counts["email"] == 1
    assert counts["phone"] == 1
    assert counts["ssn"] == 1
    assert counts["credit_card"] == 1
    assert counts["api_key"] == 1
    assert "email" in pii_types
