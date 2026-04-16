"""Slurm API client models for version v0.0.41 (fallback)."""

from __future__ import annotations

from typing import Union

from pydantic import BaseModel


class TimeLimit(BaseModel):
    """Time limit representation for v0.0.41."""
    number: int
    set: bool
    infinite: bool


class MemoryPerNode(BaseModel):
    """Memory per node representation for v0.0.41."""
    set: bool
    infinite: bool
    number: int


class Job(BaseModel):
    """Job representation for v0.0.41."""
    name: str
    nodes: Union[str, int]
    time_limit: TimeLimit
    current_working_directory: str
    cpus_per_task: int
    memory_per_node: MemoryPerNode
    tres_per_node: str
    tasks_per_node: int
    partition: str
    standard_output: str
    environment: list[str]
    script: str


class JobData(BaseModel):
    """Job data wrapper for v0.0.41."""
    job: Job
