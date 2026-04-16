"""Logger module for slurmpy."""

import logging

# Create a simple logger instance
slurmpy_logger = logging.getLogger("slurmpy")
slurmpy_logger.setLevel(logging.INFO)

# Add a handler if none exists
if not slurmpy_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    slurmpy_logger.addHandler(handler)
