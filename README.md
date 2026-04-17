# slurmpy

A Python library for interacting with the Slurm workload manager REST API.

## Installation

```bash
pip install git+https://github.com/SURF-ML/Slurmpy.git
```

## Usage

```python
from slurmpy import SlurmClient, Job, JobData, TimeLimit, MemoryPerNode

# Create a client
client = SlurmClient(
    url="https://slurm.example.com",
    user="your_username",
    token="your_token"
)

# Check diagnostics
response = client.diag()
print(response.json())

# Submit a job
job_data = JobData(
    job=Job(
        name="my_job",
        nodes=1,
        time_limit=TimeLimit(number=60, set=True, infinite=False),
        current_working_directory="/path/to/workdir",
        cpus_per_task=4,
        memory_per_node=MemoryPerNode(set=True, infinite=False, number=8000),
        tres_per_node="cpu=4",
        tasks_per_node=1,
        partition="compute",
        standard_output="/path/to/output.log",
        environment=["VAR=value"],
        script="#!/bin/bash\necho 'Hello World'"
    )
)

response = client.job_submit(job_data)
print(response.json())

# Get job status
job_id = "12345"
status_response = client.job_status(job_id)
print(status_response.json())

# Cancel a job
client.job_cancel(job_id)
```

## API Reference

See the source code for full documentation. The main entry points are:

- `SlurmClient` - Main client class (see `src/slurmpy/client.py`)
- `Job`, `JobData`, `TimeLimit`, `MemoryPerNode` - Models (see `src/slurmpy/v0041/models.py` and `src/slurmpy/v0042/models.py`)

## Version Handling and Fallback Lookup

This library supports multiple Slurm API versions (currently v0.0.41 and v0.0.42) with automatic version detection and fallback mechanisms.

### Automatic Version Detection

When you create a `SlurmClient` without specifying a version, the library automatically detects the highest compatible API version:

```python
# Auto-detect the highest supported version
client = SlurmClient(
    url="https://slurm.example.com",
    user="your_username",
    token="your_token"
)
```

The client attempts to connect to each available version (starting from the newest) using the `/diag` endpoint. Once a successful connection is made, that version becomes the active client.

### Manual Version Selection

You can also specify a version explicitly if needed:

```python
# Force a specific version
client = SlurmClient(
    url="https://slurm.example.com",
    user="your_username",
    token="your_token",
    version="v0.0.41"
)
```

### Function Resolution with Fallback Lookup

The library uses a function resolution mechanism to handle API methods that may differ between versions:

1. **Primary Client**: When a method is called (e.g., `client.job_status()`), it first delegates to the primary client instance that was selected during initialization.

2. **Fallback Chain**: If a method is not available on the primary client, the library searches older implementations in descending version order. This allows you to use methods from older API versions even when connected to a newer version. As in most cases between SLURM API versions the input/output is the same.

3. **Attribute Resolution Order**:
   - Methods are first looked up on the primary client
   - If not found, the library searches older implementations sorted by version
   - An `AttributeError` is raised if the method is not found in any supported version

