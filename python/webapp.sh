#!/bin/bash

# Start the web service, running within the hypercorn server.
# Entry point is websvc.py, 'app' is the FastAPI object.
# Chris Joakim, Microsoft

Write-Host 'activating the venv ...'
source venv/bin/activate
python --version

Write-Host 'removing tmp files ...'
mkdir -p tmp
rm tmp/*.*

hypercorn webapp:app --bind 127.0.0.1:8000 --workers 1 --reload
#uvicorn webapp:app --port 8000 --reload
