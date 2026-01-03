#!/bin/bash
export PYTHONPATH=/app:$PYTHONPATH
cd /app/turkish
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
