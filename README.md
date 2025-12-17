# Diet Optimizer

Simple diet optimization demo (Flask backend + static frontend) for semester viva.

Quick run (requires Docker Desktop):

1. Start services (backend + Mongo):

```powershell
cd backend
docker compose up --build -d
```

2. Open frontend pages:
- `frontend/home.html` — optimize diet
- `frontend/foods.html` — add food items
- `frontend/history.html` — view history and charts

Notes:
- Health check: `GET http://localhost:5000/health` returns Mongo connectivity.
- API endpoints:
  - `GET /foods`, `POST /foods`, `DELETE /foods/<name>`
  - `POST /optimize` — runs GA and stores result in Mongo
  - `GET /results` — lists past results

If you prefer running without Docker:
- Install Python 3.12+, create a venv, and `pip install -r backend/requirements.txt`.
- Start MongoDB locally or change `MONGO_URI` env var to a reachable Mongo.
- Run backend:

```powershell
cd backend
set MONGO_URI=mongodb://localhost:27017/
python app.py
```

For the viva, you can run a quick optimize call using PowerShell:

```powershell
$body = @{
  targets = @{ calories = 2000; protein = 100; carbs = 250; fat = 70 }
  budget = 10
  population_size = 50
  generations = 20
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post -Uri 'http://localhost:5000/optimize' -ContentType 'application/json' -Body $body
```

Good luck with your viva — tell me if you want a short demo script or slides prepared.