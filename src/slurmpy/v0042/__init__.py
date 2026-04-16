"""Slurm API v0.0.42 version-specific implementations."""

from __future__ import annotations

from slurmpy.v0042.models import Job, JobData, TimeLimit, MemoryPerNode
from slurmpy.v0042.api import ClientV0042, SlurmResponseError

__all__ = [
    "Job",
    "JobData",
    "TimeLimit",
    "MemoryPerNode",
    "ClientV0042",
    "SlurmResponseError",
]
