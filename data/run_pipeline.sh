#!/bin/bash
# HealthApp Training Intelligence Platform
# Entry point — all logic hanteras av run_all_pipelines.py

echo "Starting HealthApp Intelligence Engine..."
echo "$(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================="

export PYTHONPATH=.
uv run run_all_pipelines.py

echo "=================================="
echo "Done!"
