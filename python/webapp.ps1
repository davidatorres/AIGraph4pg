# Start the web app, running within the hypercorn server.
# Entry point is webapp.py, 'app' is the FastAPI object.
# hypercorn enables restarting the app as the Python code changes.
# Chris Joakim, Microsoft

New-Item -ItemType Directory -Force -Path .\tmp | out-null

Write-Host 'activating the venv ...'
.\venv\Scripts\Activate.ps1

Write-Host 'removing tmp files ...'
del tmp\*.*

Write-Host '.env file contents ...'
cat .env 

hypercorn webapp:app --bind 127.0.0.1:8000 --workers 1 --reload
#uvicorn webapp:app --port 8000 --reload
