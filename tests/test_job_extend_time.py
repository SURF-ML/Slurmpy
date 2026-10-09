"""Tests for ClientV0041.job_extend_time edge cases."""

from __future__ import annotations

from unittest.mock import patch

from slurmpy.v0041 import ClientV0041


class TestJobExtendTime:
    def _client(self) -> ClientV0041:
        return ClientV0041('https://slurm.example.com', 'user', 'token')

    def test_returns_none_when_job_resources_missing(self):
        """A job with no job_resources has nothing to extend and must not raise."""
        client = self._client()
        with patch.object(ClientV0041, 'job_status', return_value={'job_resources': None}):
            assert client.job_extend_time('1234') is None

    def test_drain_state_still_returns_none(self):
        """The guard must not break the existing DRAIN short-circuit."""
        client = self._client()
        job = {'job_resources': {'nodes': {'list': 'node1'}}}
        with patch.object(ClientV0041, 'job_status', return_value=job), \
                patch.object(ClientV0041, 'node_status', return_value=['DRAIN']):
            assert client.job_extend_time('1234') is None