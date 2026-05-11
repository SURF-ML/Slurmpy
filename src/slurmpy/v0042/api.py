"""Version-specific API implementation for Slurm API v0.0.42.

Combines endpoint handlers and response parsing for v0.0.42.
"""

from __future__ import annotations

import datetime
from typing import Any

import requests
from requests import Response

from slurmpy.logger import slurmpy_logger
from slurmpy.base_api import BaseClient, SlurmResponseError
from slurmpy.v0042 import Job


class ClientV0042(BaseClient):
    version_str = 'v0.0.42'

    def __init__(self, url: str, user: str, token: str):
        super().__init__(url, user, token)
        self.version_str = ClientV0042.version_str

    def diag(self):
        response = requests.get(
            f'{self.url}/diag',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def job_submit(self, job_data: Job):
        """Submit a job for v0.0.42."""
        response = requests.post(
            f'{self.url}/job/submit',
            json=job_data.model_dump(),
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    def job_status(self, job_id: str) -> dict[str, Any]:
        response = requests.get(
            f'{self.url}/job/{job_id}',
            headers=self.headers,
        )
        response.raise_for_status()

        data = response.json()
        jobs = data.get('jobs')
        if not isinstance(jobs, list):
            raise SlurmResponseError(
                'Invalid SLURM response: `jobs` is not a list',
                response_data=data
            )

        if len(jobs) == 0:
            raise SlurmResponseError(
                'No jobs found in response',
                response_data=data
            )

        job = jobs[0]
        return job

    def job_cancel(self, job_id: str) -> None:
        response = requests.delete(
            f'{self.url}/job/{job_id}',
            headers=self.headers,
        )
        response.raise_for_status()