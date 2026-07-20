import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from secrets_guard import scan


def test_clean_text_is_not_flagged():
    assert scan("Can you summarize this quarterly report for me?") is False


def test_aws_access_key_is_flagged():
    assert scan("My key is AKIAABCDEFGHIJKLMNOP, don't share it.") is True


def test_github_token_is_flagged():
    assert scan("token: ghp_" + "a" * 36) is True


def test_password_assignment_is_flagged():
    assert scan("password=SuperSecret123!") is True


def test_private_key_block_is_flagged():
    assert scan("-----BEGIN RSA PRIVATE KEY-----\nMIIB...") is True


# --- Phase 6.3: generic high-entropy secret detection ---

def test_bare_jwt_with_no_prefix_is_flagged_by_entropy_alone():
    jwt = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    assert scan(f"Here is my session token: {jwt}") is True


def test_pem_body_with_no_begin_wrapper_is_flagged_by_entropy_alone():
    body = "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKjMzEfYyjiWA4R4"
    assert scan(f"Can you validate this key material: {body}") is True


def test_clean_long_english_text_is_not_flagged_by_entropy():
    assert scan(
        "Could you please help me understand the internationalization and "
        "localization configuration manager we discussed yesterday?"
    ) is False


def test_uuid_is_not_flagged_by_entropy():
    assert scan("The record ID is 550e8400-e29b-41d4-a716-446655440000, please look it up.") is False


def test_sha1_style_hex_hash_is_not_flagged_by_entropy():
    assert scan("The git commit is a94a8fe5ccb19ba61c4c0873d391e987982fbbd3a94a8fe5ccb19ba, FYI.") is False


def test_ordinary_url_is_not_flagged_by_entropy():
    assert scan("See https://example.com/api/v2/users/profile/settings/notifications for details.") is False
