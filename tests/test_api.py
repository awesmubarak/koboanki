"""Tests for API functionality in koboanki.core module."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch

import pytest

from koboanki.core import fetch_definition


def create_mock_response(data: str, status: int = 200) -> MagicMock:
    """Create a mock HTTP response object."""
    mock_response = MagicMock()
    mock_response.status = status
    mock_response.read.return_value = data.encode('utf-8')
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None
    return mock_response


class TestFetchDefinition:
    """Test the fetch_definition function comprehensively."""

    def test_unsupported_language_returns_empty_string(self) -> None:
        """Test that unsupported language codes return empty string."""
        result = fetch_definition("word", "unsupported")
        assert result == ""
        
        result = fetch_definition("word", "xx")
        assert result == ""

    @patch('urllib.request.urlopen')
    def test_successful_definition_fetch(self, mock_urlopen: MagicMock) -> None:
        """Test successful API response with valid definition."""
        mock_data = {
            "senses": [
                {"glosses": ["a round fruit"]},
                {"glosses": ["technology company"]}
            ]
        }
        
        mock_response = create_mock_response(json.dumps(mock_data))
        mock_urlopen.return_value = mock_response
        
        result = fetch_definition("apple", "en")
        assert result == "a round fruit; technology company"
        
        # Verify the correct URL was called
        expected_url = "https://kaikki.org/dictionary/English/meaning/a/ap/apple.jsonl"
        mock_urlopen.assert_called_once_with(expected_url, timeout=5)

    @patch('urllib.request.urlopen')
    def test_404_error_returns_empty_string(self, mock_urlopen: MagicMock) -> None:
        """Test that 404 errors (word not found) return empty string."""
        from email.message import EmailMessage
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="test", code=404, msg="Not Found", hdrs=EmailMessage(), fp=None
        )
        
        result = fetch_definition("nonexistentword", "en")
        assert result == ""

    @patch('urllib.request.urlopen')
    def test_other_http_errors_are_raised(self, mock_urlopen: MagicMock) -> None:
        """Test that non-404 HTTP errors are propagated."""
        # Clear cache to ensure fresh test
        fetch_definition.cache_clear()
        
        from email.message import EmailMessage
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="test",
            code=500,
            msg="Internal Server Error",
            hdrs=EmailMessage(),
            fp=None
        )
        
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            fetch_definition("test_http_error", "en")  # Use unique word
        assert exc_info.value.code == 500

    @patch('urllib.request.urlopen')
    def test_network_errors_are_raised(self, mock_urlopen: MagicMock) -> None:
        """Test that URLError (network errors) are propagated."""
        # Clear cache to ensure fresh test
        fetch_definition.cache_clear()
        
        mock_urlopen.side_effect = urllib.error.URLError("Network unreachable")
        
        with pytest.raises(urllib.error.URLError):
            fetch_definition("test_url_error", "en")  # Use unique word

    @patch('urllib.request.urlopen')
    def test_missing_senses_returns_empty_string(self, mock_urlopen: MagicMock) -> None:
        """Test that responses without senses field return empty string."""
        # JSON Lines with objects that don't have senses
        mock_jsonl = (
            json.dumps({"word": "test", "pos": "noun"})
            + "\n"
            + json.dumps({"etymology": "from latin"})
        )
        
        mock_response = create_mock_response(mock_jsonl)
        mock_urlopen.return_value = mock_response
        
        result = fetch_definition("test", "en")
        assert result == ""

    @patch('urllib.request.urlopen')
    def test_empty_api_response_returns_empty_string(
        self, mock_urlopen: MagicMock
    ) -> None:
        """Test that empty API responses return empty string."""
        mock_response = create_mock_response(json.dumps({}))
        mock_urlopen.return_value = mock_response
        
        result = fetch_definition("test", "en")
        assert result == ""

    @patch('urllib.request.urlopen')
    def test_caching_behavior(self, mock_urlopen: MagicMock) -> None:
        """Test that the LRU cache works correctly."""
        # Clear the cache first to avoid interference from other tests
        fetch_definition.cache_clear()
        
        mock_response = create_mock_response(json.dumps({
            "senses": [{"glosses": ["cached definition"]}]
        }))
        mock_urlopen.return_value = mock_response
        
        # First call should hit the API
        result1 = fetch_definition("test_cache_word", "en")
        assert result1 == "cached definition"
        assert mock_urlopen.call_count == 1
        
        # Second call should use cache
        result2 = fetch_definition("test_cache_word", "en")
        assert result2 == "cached definition"
        assert mock_urlopen.call_count == 1  # No additional call
        
        # Different word should hit API again
        fetch_definition("another_test_word", "en")
        assert mock_urlopen.call_count == 2