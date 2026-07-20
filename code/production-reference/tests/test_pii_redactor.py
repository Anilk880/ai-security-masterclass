import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pii_redactor import redact


def test_email_is_redacted():
    text, found = redact("Contact me at anil.kumar@example.com please")
    assert "[REDACTED_EMAIL]" in text
    assert "EMAIL" in found
    assert "anil.kumar@example.com" not in text


def test_pan_is_redacted():
    text, found = redact("My PAN is ABCDE1234F for verification")
    assert "[REDACTED_PAN_ID]" in text
    assert "PAN_ID" in found


def test_aadhaar_is_redacted():
    text, found = redact("Aadhaar number: 1234 5678 9012")
    assert "[REDACTED_AADHAAR_ID]" in text
    assert "AADHAAR_ID" in found


def test_credit_card_is_redacted():
    text, found = redact("Card number 4111 1111 1111 1111 expires soon")
    assert "[REDACTED_CREDIT_CARD]" in text
    assert "CREDIT_CARD" in found


def test_phone_number_is_redacted():
    text, found = redact("Call me on 9876543210 tomorrow")
    assert "[REDACTED_PHONE_NUMBER]" in text
    assert "PHONE_NUMBER" in found


def test_clean_text_is_untouched():
    text, found = redact("Hello, how can I help you today?")
    assert text == "Hello, how can I help you today?"
    assert found == []


def test_multiple_pii_types_in_one_message():
    text, found = redact(
        "Email anil@example.com or call 9876543210, Aadhaar 1234 5678 9012"
    )
    assert set(found) == {"EMAIL", "PHONE_NUMBER", "AADHAAR_ID"}
