"""Tests for password hashing."""

from src.shared.security.password import hash_password, verify_password


def test_password_is_hashed():
    """Password is not stored in plain text."""
    pw = "my-secure-password"
    hashed = hash_password(pw)
    assert hashed != pw
    assert len(hashed) > 20


def test_password_verify_works():
    """Verify returns True for correct password."""
    pw = "test-password-123"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed) is True


def test_wrong_password_rejected():
    """Verify returns False for wrong password."""
    hashed = hash_password("correct-password")
    assert verify_password("wrong-password", hashed) is False


def test_hash_is_different_each_time():
    """Same password produces different hashes (salting)."""
    pw = "same-password"
    h1 = hash_password(pw)
    h2 = hash_password(pw)
    assert h1 != h2
