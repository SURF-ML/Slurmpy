from __future__ import annotations

from typing import Any


class SlurmResponseError(Exception):
    def __init__(self, message: str, response_data: Any | None = None):
        self.message = message
        self.response_data = response_data
        super().__init__(message)


class BaseClient:

    def __init__(self, url: str, user: str, token: str):
        self.version_str = ''
        self._url = url
        self.user = user
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'X-SLURM-USER-NAME': f'{user}',
            'X-SLURM-USER-TOKEN': f'{token}',
        }

    @property
    def url(self) -> str:
        return f'{self._url}/slurm/{self.version_str}'

    def diag(self):
        raise NotImplementedError()

    def job_submit(self, job_data: Any):
        raise NotImplementedError()

    def job_status(self, job_id: str):
        raise NotImplementedError()

    def job_cancel(self, job_id: str):
        raise NotImplementedError()

    def job_extend_time(self,
                        job_id: str,
                        add_minutes: int = 60,
                        min_job_runtime_to_extend: int = 60
                        ):
        raise NotImplementedError()
