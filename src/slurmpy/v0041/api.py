"""Version-specific API implementation for Slurm API v0.0.41 (fallback).

Combines endpoint handlers and response parsing for v0.0.41.
"""

from __future__ import annotations

import datetime
from typing import Any, Literal, List

import requests
from requests import Response

from slurmpy.logger import slurmpy_logger
from slurmpy.base_api import BaseClient, SlurmResponseError
from slurmpy.v0041 import Job


class ClientV0041(BaseClient):
    version_str = 'v0.0.41'

    def __init__(self, url: str, user: str, token: str):
        super().__init__(url, user, token)
        self.version_str = ClientV0041.version_str

    def diag(self):
        response = requests.get(
            f'{self.url}/diag',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def job_submit(self, job_data: Job):
        """Submit a job for v0.0.41."""
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

    def job_extend_time(
            self,
            job_id: str,
            add_minutes: int = 60,
            min_job_runtime_to_extend: int = 60
    ) -> Response | None:
        """
        Extend job runtime for v0.0.41.
        Will honor the Slurm DRAIN state and not extend the jobs when this node state is encountered.

        Args:
            job_id: The job ID to extend
            add_minutes: Minutes to add to runtime
            min_job_runtime_to_extend: Minimum remaining runtime to trigger extension

        Returns:
            Response from the API or None if extension not triggered
        """
        job = self.job_status(job_id)

        node_name = job.get('job_resources').get('nodes').get('list')
        statuses = self.node_status(node_name)
        if 'DRAIN' in statuses:
            slurmpy_logger.info(f"Not extending job due to `DRAIN` state on node {node_name}.")
            return None

        now = datetime.datetime.now().timestamp()
        end_time = job.get('end_time').get('number')

        if (end_time - now) / 60 > min_job_runtime_to_extend:
            return None

        current_time_limit = job.get('time_limit').get('number')
        response = requests.post(
            f'{self.url}/job/{job_id}',
            json={'time_limit': {'set': True, 'number': current_time_limit + add_minutes}},
            headers=self.headers
        )
        if not response.status_code == 200:
            slurmpy_logger.info(
                f"Failed updating time: {response.text}, your account may not have rights to extend jobs.")
            return None

        return response.json()

    def node_status(self, node_name: str) -> List[Literal['DOWN', 'DRAIN', 'IDLE', 'MIXED', 'NOT_RESPONDING', 'ALLOCATED']]:
        response = requests.get(
            f'{self.url}/node/{node_name}',
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        nodes = data.get('nodes')
        if len(nodes) > 0:
            slurmpy_logger.info("More than one node matched node name, selecting first one.")
        return nodes[0].get('state')