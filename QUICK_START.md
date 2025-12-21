# Diet Optimizer - Quick Start Guide

## Prerequisites
- Docker Desktop installed at `D:\Docker\Docker Desktop.exe`
- Python 3.13+ (included in Docker)
- Modern web browser

## Quick Start (3 Steps)

### Step 1: Start Docker
```powershell
# Open PowerShell and run:
& "D:\Docker\Docker Desktop.exe"
Start-Sleep -Seconds 8
```

### Step 2: Start Containers
```powershell
cd "e:\Projects\Diet Opmitizer\backend"
docker compose up --build -d
Start-Sleep -Seconds 5
```

### Step 3: Open Frontend
```
File > Open File:
e:\Projects\Diet Opmitizer\frontend\home.html
```

---

## Using the Application

### 1. Home Page (Optimization)

**Fill the form:**
- Calories target (e.g., 2000 kcal)
- Protein target (e.g., 100g)
- Carbs target (e.g., 250g)
- Fat target (e.g., 70g)
- Budget (e.g., $15)

**Select Algorithm:**
- Click "GA" for Genetic Algorithm
- Click "CSP" for Constraint Satisfaction Problem
- Click "Both" for side-by-side comparison

**Optional Parameters:**
- Tolerance (for CSP): How much deviation allowed from targets (5-50%)
- Population Size (for GA): Number of solutions in each generation (default: 30)
- Generations (for GA): Number of iterations (default: 50)

**Get Results:**
Click "Optimize Diet" and wait 2-7 seconds

### 2. Food Database Page

**View Foods:**
Table of 32 pre-loaded foods with nutrition data

**Add Food:**
Fill form with:
- Food name
- Calories
- Protein (g)
- Carbs (g)
- Fat (g)
- Price ($)

Click "Add Food"

**Remove Food:**
Click delete button next to any food

### 3. History Page

**View Results:**
- All optimization attempts
- Scores and costs
- Time stamps
- Nutrition breakdown charts

---

## API Endpoints

### Foods
```
GET  /foods              - List all foods
POST /foods              - Add new food
DELETE /foods/<name>     - Remove food
```

### Optimization
```
POST /optimize
Parameters:
  - technique: "ga" | "csp" | "both"
  - targets: {calories, protein, carbs, fat}
  - budget: number
  - population_size: number (GA only)
  - generations: number (GA only)
  - tolerance: 0-1 (CSP only)
```

### Results
```
GET /results - Retrieve all saved results
```

---

## Example Requests

### Genetic Algorithm
```bash
curl -X POST http://localhost:5000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "technique": "ga",
    "targets": {"calories": 2000, "protein": 100, "carbs": 250, "fat": 70},
    "budget": 15,
    "population_size": 30,
    "generations": 50
  }'
```

### Constraint Satisfaction
```bash
curl -X POST http://localhost:5000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "technique": "csp",
    "targets": {"calories": 2000, "protein": 100, "carbs": 250, "fat": 70},
    "budget": 15,
    "tolerance": 0.15
  }'
```

### Comparison
```bash
curl -X POST http://localhost:5000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "technique": "both",
    "targets": {"calories": 2000, "protein": 100, "carbs": 250, "fat": 70},
    "budget": 15,
    "population_size": 30,
    "generations": 50,
    "tolerance": 0.15
  }'
```

---

## File Locations

```
Project Root: e:\Projects\Diet Opmitizer\

Backend Files:
  backend/app.py                   - Flask API server
  backend/genetic_algorithm.py     - GA implementation
  backend/csp_solver.py            - CSP implementation
  backend/requirements.txt          - Python dependencies
  backend/compose.yml              - Docker configuration
  backend/Dockerfile               - Container image definition

Frontend Files:
  frontend/home.html               - Main optimization page
  frontend/foods.html              - Food database manager
  frontend/history.html            - Results viewer
  frontend/app.js                  - Client-side JavaScript
  frontend/style.css               - Responsive styling

Documentation:
  README.md                        - Project overview
  TEST_RESULTS.md                  - Full test report
  QUICK_START.md                   - This file
```

---

## Troubleshooting

### Containers won't start
```powershell
# Stop all containers
docker compose down

# Rebuild from scratch
docker compose up --build -d
```

### "Cannot connect to Docker daemon"
```powershell
# Start Docker Desktop
& "D:\Docker\Docker Desktop.exe"
Start-Sleep -Seconds 15
```

### Frontend won't load
- Check browser console (F12) for errors
- Ensure backend is running: `docker ps`
- Verify API responds: http://localhost:5000/foods

### API returns 500 error
```powershell
# Check backend logs
docker logs backend-app-1 --tail 20
```

### No foods in database
- Go to Foods page
- Add at least one food before optimizing
- Or populate via API: `POST /foods`

---

## Algorithm Explanation

### Genetic Algorithm (GA)
- **Approach**: Evolutionary population-based search
- **Strengths**: Good for large search spaces with continuous optimization
- **Weaknesses**: May violate hard constraints (e.g., budget limits)
- **Best for**: Flexible requirements with soft constraints

### Constraint Satisfaction Problem (CSP)
- **Approach**: Backtracking search with constraint propagation
- **Strengths**: Guarantees constraint satisfaction; excellent at finding feasible solutions
- **Weaknesses**: May take longer to optimize; sensitive to problem structure
- **Best for**: Problems with hard constraints (budgets, requirements)

### Performance
- **CSP**: Consistently 82/100 score (highly constrained problems)
- **GA**: Varies 1-87/100 (depends on budget availability)
- **Comparison**: CSP wins on constrained problems by 36-55 points

---

## Viva Demonstration Talking Points

1. **Two Different Algorithms**
   - Genetic Algorithm: Evolutionary approach
   - Constraint Satisfaction: Logical constraint satisfaction
   - Why two: Show different problem-solving paradigms

2. **When CSP Wins**
   - Budget constraints are hard (must stay within)
   - Nutrition targets must be met (or close)
   - Show CSP scores 82/100 vs GA 27/100

3. **When GA Wins**
   - High budgets with flexible requirements
   - GA can achieve 87/100 with ample budget
   - Evolutionary approach explores more solutions

4. **Real-World Applications**
   - Meal planning for specific diets
   - Cost optimization in food services
   - Nutritional requirement satisfaction
   - Student/institutional cafeteria planning

5. **Technical Achievements**
   - Modular Python code (clean separation)
   - Docker containerization (portable deployment)
   - MongoDB persistence (scalable storage)
   - Responsive web interface (usable frontend)
   - Dual-algorithm support (algorithm comparison)

---

## Testing Checklist

Before viva, verify:

- [ ] Docker containers running (`docker ps`)
- [ ] Frontend loads (home.html opens in browser)
- [ ] Food database has items (Foods page)
- [ ] GA optimization works (returns score, diet, cost)
- [ ] CSP optimization works (returns score, diet, cost)
- [ ] Comparison mode works (shows both results)
- [ ] History saves results (History page shows attempts)
- [ ] API endpoints respond (all 6 endpoints working)
- [ ] No JavaScript errors (Browser F12 console is clear)
- [ ] Responsive design works (resize browser window)

---

## Performance Benchmarks

| Operation | Time | Status |
|-----------|------|--------|
| GA Optimization | 2-3s | Fast |
| CSP Optimization | 3-4s | Fast |
| Comparison (both) | 5-7s | Acceptable |
| Food CRUD | <1s | Fast |
| Results retrieval | <1s | Fast |

---

**Status**: ✓ Ready for Viva Demonstration

All algorithms working, all tests passing, ready to showcase!
