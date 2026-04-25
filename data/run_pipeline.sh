#!/bin/bash

CD_PATH="/Users/abdulrahmanfahmi/Documents/egna projekt/HealthApp/HealthApp/data"
UV="/opt/homebrew/bin/uv"
LOG="$CD_PATH/pipeline.log"

echo "$(date) - Startar pipeline..." >> "$LOG"

cd "$CD_PATH" || { echo "$(date) -  Kunde inte hitta mappen!" >> "$LOG"; exit 1; }

$UV run pipelines/recommendation_pipeline.py
$UV run pipelines/analysis.py

echo "$(date) - Pipeline klar!" >> "$LOG"