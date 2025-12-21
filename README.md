# Diet Optimizer

Diet optimization application using **Genetic Algorithms (GA)** and **Constraint Satisfaction Problems (CSP)** for finding optimal meal plans based on nutritional targets and budget constraints.

## 🎯 AI Techniques Implemented

### 1. Genetic Algorithm (GA)
- **Chromosome**: Array of food quantities
- **Fitness Function**: Weighted error from nutrition targets + budget penalty
- **Selection**: Tournament selection
- **Crossover**: Single-point crossover
- **Mutation**: Random quantity adjustments with repair
- **Elitism**: Preserves top performers

### 2. Constraint Satisfaction Problem (CSP)
- **Variables**: Quantity of each food item (0 to max_qty)
- **Domains**: {0, 1, 2, ..., max_qty} for each food
- **Constraints**: Budget limit, nutrition targets within tolerance
- **Techniques**: Backtracking with forward checking, MRV heuristic, LCV ordering

## 🚀 Quick Start (Docker)

1. Start services (backend + MongoDB):

```powershell
cd backend
docker compose up --build -d
```

2. Open frontend pages:
- `frontend/home.html` — optimize diet (select GA, CSP, or compare both)
- `frontend/foods.html` — add food items
- `frontend/history.html` — view history and charts

## 📋 Features

- **Technique Selection**: Choose between GA, CSP, or compare both side-by-side
- **Real-time Comparison**: See which technique performs better for your constraints
- **Food Database**: Add/remove foods with nutritional info and price
- **History Tracking**: View past optimizations with charts
- **Budget Constraints**: Stay within your daily food budget

## 🔌 API Endpoints

- `GET /foods` - List all foods
- `POST /foods` - Add a new food
- `DELETE /foods/<name>` - Remove a food
- `POST /optimize` - Run optimization (supports `technique`: "ga", "csp", or "both")
- `GET /results` - List past results
- `GET /health` - Check MongoDB connectivity

## 💻 Running Without Docker

```powershell
# Install dependencies
cd backend
pip install -r requirements.txt

# Start MongoDB locally or set MONGO_URI
set MONGO_URI=mongodb://localhost:27017/
python app.py
```

## 📊 Example API Call

```powershell
$body = @{
  targets = @{ calories = 2000; protein = 100; carbs = 250; fat = 70 }
  budget = 10
  population_size = 50
  generations = 20
  technique = "both"  # "ga", "csp", or "both"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post -Uri 'http://localhost:5000/optimize' -ContentType 'application/json' -Body $body
```

Good luck with your viva — tell me if you want a short demo script or slides prepared.