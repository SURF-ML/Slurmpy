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

    def diag(self):
        response = requests.get(
            f'{self.url}/slurm/v0.0.42/diag',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def job_submit(self, job_data: Job):
        """Submit a job for v0.0.42."""
        response = requests.post(
            f'{self.url}/slurm/v0.0.42/job/submit',
            data=job_data.json(),
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    def job_status(self, job_id: str) -> dict[str, Any]:
        response = requests.get(
            f'{self.url}/slurm/v0.0.42/job/{job_id}',
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
            f'{self.url}/slurm/v0.0.42/job/{job_id}',
            headers=self.headers,
        )
        response.raise_for_status()

    def job_extend_time(
            self,
            job_id: str,
            add_minutes: int = 60,
            min_job_runtime_to_extend: int = 60
    ) -> Response | None:
        """
        Extend job runtime for v0.0.42.

        Args:
            job_id: The job ID to extend
            add_minutes: Minutes to add to runtime
            min_job_runtime_to_extend: Minimum remaining runtime to trigger extension

        Returns:
            Response from the API or None if extension not triggered
        """
        response = requests.get(
            f'{self.url}/slurm/v0.0.42/job/{job_id}',
            headers=self.headers
        )
        if response.status_code != 200:
            return None

        job = response.json()['jobs'][0]
        now = datetime.datetime.now().timestamp()
        end_time = job.get('end_time').get('number')

        if (end_time - now) / 60 > min_job_runtime_to_extend:
            return None

        current_time_limit = job.get('time_limit').get('number')
        response = requests.post(
            f'{self.url}/slurm/v0.0.42/job/{job_id}',
            json={'time_limit': {'set': True, 'number': current_time_limit + add_minutes}},
            headers=self.headers
        )
        if not response.status_code == 200:
            slurmpy_logger.info(
                f"Failed updating time: {response.text}, your account may not have rights to extend jobs.")
            return None

        return response.json()
