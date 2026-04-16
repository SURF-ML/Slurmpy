"""Slurm API v0.0.41 version-specific implementations (fallback)."""

from __future__ import annotations

from slurmpy.v0041.models import Job, JobData, TimeLimit, MemoryPerNode
from slurmpy.v0041.api import ClientV0041, SlurmResponseError

__all__ = [
    "Job",
    "JobData",
    "TimeLimit",
    "MemoryPerNode",
    "ClientV0041",
    "SlurmResponseError",
]
