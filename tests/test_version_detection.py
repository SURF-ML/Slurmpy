"""Tests for Slurm API version auto-detection with mocked endpoint."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from requests import HTTPError

from slurmpy import SlurmClient
from slurmpy.logger import slurmpy_logger
from slurmpy.v0041 import ClientV0041
from slurmpy.v0042 import ClientV0042


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

            assert client.version_str == 'v0.0.42'
            assert mock_get.call_count == 1

    def test_falls_back_on_older(
            self, mock_response, mock_failed_response
    ):
        original = ClientV0042.job_submit
        del ClientV0042.job_submit

        try:
            with patch('requests.get') as mock_get, \
                    patch.object(ClientV0041, 'job_submit', return_value={'job_id': 123}) as mock_v41_submit:

                mock_get.return_value = mock_response

                client = SlurmClient('https://slurm.example.com', 'user', 'token')
                result = client.job_submit({'script': 'test.sh'})
                client.job_extend_time('1234')
                mock_v41_submit.assert_called_once()
                assert result == {'job_id': 123}
        finally:
            ClientV0042.job_submit = original
