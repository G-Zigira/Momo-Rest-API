import sys
sys.path.insert(0, "./")
import base64
from unittest.mock import MagicMock
from server import _check_auth, _parse_id

def test_check_auth_valid():
    # Create a mock handler with valid credentials
    handler = MagicMock()
    credentials = base64.b64encode(b"admin:momo2024").decode("utf-8")
    handler.headers.get.return_value = f"Basic {credentials}"
    result = _check_auth(handler)
    assert result == True, f"Expected True for valid credentials, got {result}"

def test_check_auth_invalid():
    # Create a mock handler with invalid credentials
    handler = MagicMock()
    credentials = base64.b64encode(b"admin:wrongpassword").decode("utf-8")
    handler.headers.get.return_value = f"Basic {credentials}"
    result = _check_auth(handler)
    assert result == False, f"Expected False for invalid credentials, got {result}"

def test_parse_id_with_string():
    result = _parse_id("123")
    assert result == 123, f"Expected 123, got {result}"

def test_parse_id_with_non_string():
    result = _parse_id(4345)
    assert result == 4345, f"Expected 4345, got {result}"

def test_parse_id_with_invalid_string():
    result = _parse_id("xyz")
    assert result is None, f"Expected None for invalid string, got {result}"

def test_parse_id_with_none():
    result = _parse_id(None)
    assert result is None, f"Expected None for None input, got {result}"

def test_parse_id_with_empty_string():
    result = _parse_id("")
    assert result is None, f"Expected None for empty string, got {result}" 

def test_parse_id_with_float_string():
    result = _parse_id("89.4648825")
    assert result is None, f"Expected None for float string, got {result}"

def  test_parse_id_with_valid_string():
    result = _parse_id("456")
    assert result == 456, f"Expected 456, got {result}"

