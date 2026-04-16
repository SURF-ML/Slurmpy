"""Tests for Slurm API version auto-detection with mocked endpoint."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from requests import HTTPError

from slurmpy import SlurmClient


class TestVersionAutoDetection:
    """Tests for automatic version detection via diag endpoint."""

    @pytest.fixture
    def mock_response(self):
        """Create a mock response object."""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {'server': {'version': 'v0.0.42'}}
        return response

    @pytest.fixture
    def mock_failed_response(self):
        """Create a mock failed response (404)."""
        response = Mock()
        response.status_code = 404
        response.raise_for_status.side_effect = HTTPError(response=response)
        return response

    def test_auto_detect_version_newest_available(
        self, mock_response, mock_failed_response
    ):
        with patch('requests.get') as mock_get:
            mock_get.return_value = mock_response

            client = SlurmClient('https://slurm.example.com', 'user', 'token')

            assert client.version_str == 'v0.0.41'
            # Should have called diag endpoint once
            assert mock_get.call_count == 1
