# Diet Optimizer - AI Final Term Project Report

## 1. Problem Definition

### 1.1 Problem Statement
Finding an optimal diet that meets all nutritional requirements while staying within budget constraints is a complex optimization problem. Traditional methods struggle with:
- Large solution space (many possible food combinations)
- Multiple conflicting objectives (nutrition vs. cost vs. variety)
- Hard and soft constraints (minimum/maximum nutritional requirements)

### 1.2 Why Genetic Algorithm?
Genetic Algorithms (GA) are ideal for this problem because:
1. **Large Search Space**: With 35+ foods and varying quantities, the search space is enormous
2. **Multi-objective Optimization**: GA can balance multiple goals simultaneously
3. **Constraint Handling**: Easy to incorporate nutritional constraints
4. **Global Search**: Avoids local optima through population-based search
5. **Flexibility**: Can easily add new foods or constraints

## 2. Methodology

### 2.1 System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│                  (CLI / Tkinter GUI)                        │
├─────────────────────────────────────────────────────────────┤
│                   Main Controller                            │
├─────────────┬─────────────────────────┬────────────────────┤
│   Genetic   │    Fitness              │    Database        │
│  Algorithm  │   Calculator            │   (SQLite)         │
│             │                         │                    │
│ - Selection │ - Nutrition Scoring     │ - Food Data        │
│ - Crossover │ - Cost Calculation      │ - User Profiles    │
│ - Mutation  │ - Constraint Checking   │ - Saved Plans      │
└─────────────┴─────────────────────────┴────────────────────┘
```

### 2.2 Chromosome Representation
Each chromosome represents a diet plan:
- **Gene**: Tuple of (food_name, quantity_in_grams)
- **Chromosome**: List of 5-12 genes (food items)

Example:
```python
diet = [
    ("Chicken Breast", 200),
    ("Brown Rice", 150),
    ("Broccoli", 100),
    ("Banana", 100),
    ("Almonds", 30)
]
```

### 2.3 Fitness Function
The fitness function evaluates diet quality based on:

$$Fitness = W_n \times NutritionScore + W_c \times CostScore + W_v \times VarietyBonus$$

Where:
- **NutritionScore**: How well nutritional targets are met (within min-max range)
- **CostScore**: Reward for staying under budget
- **VarietyBonus**: Bonus for food category diversity
- **W_n, W_c, W_v**: Weights (100, 20, 100 respectively)

#### Nutrition Scoring:
- +1.0 for being within target range
- Penalty proportional to deviation outside range
- Weighted by nutrient importance (protein weighted higher)

### 2.4 Genetic Operators

#### Selection: Tournament Selection
- Tournament size: 5
- Best individual from tournament is selected
- Maintains selection pressure while preserving diversity

#### Crossover: Two-point Crossover
- Rate: 80%
- Combines food pools from both parents
- Random split of combined foods to offspring

#### Mutation (Rate: 15%)
Four mutation types:
1. **Add**: Add a new random food
2. **Remove**: Remove a random food
3. **Quantity**: Adjust quantity by ±30%
4. **Swap**: Replace one food with another

### 2.5 Algorithm Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| Population Size | 100 | Number of individuals |
| Generations | 200 | Maximum iterations |
| Crossover Rate | 0.80 | Probability of crossover |
| Mutation Rate | 0.15 | Probability of mutation |
| Tournament Size | 5 | Selection tournament size |
| Elitism | 2 | Best individuals preserved |

## 3. Implementation Details

### 3.1 Project Structure
```
Diet Optimizer/
├── src/
│   ├── genetic_algorithm.py    # GA implementation
│   ├── fitness.py              # Fitness function
│   ├── database.py             # SQLite operations
│   ├── food_data.py            # Food database
│   └── utils.py                # Utilities
├── gui/
│   └── app.py                  # Tkinter GUI
├── tests/
│   └── test_optimizer.py       # Unit tests (24 tests)
├── data/
│   └── diet_optimizer.db       # SQLite database
├── main.py                     # Entry point
└── requirements.txt            # Dependencies
```

### 3.2 Food Database
- 35 food items across 8 categories
- Nutritional values per 100g (calories, protein, carbs, fat, fiber)
- Price per 100g
- Minimum and maximum serving sizes

### 3.3 Database Schema
```sql
-- Foods table
CREATE TABLE foods (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    calories REAL,
    protein REAL,
    carbs REAL,
    fat REAL,
    fiber REAL,
    price REAL,
    category TEXT
);

-- Diet plans table
CREATE TABLE diet_plans (
    id INTEGER PRIMARY KEY,
    fitness_score REAL,
    total_cost REAL,
    total_calories REAL,
    ...
);
```

### 3.4 Key Classes

#### GeneticAlgorithm Class
```python
class GeneticAlgorithm:
    def __init__(self, population_size, num_generations, ...):
        # Initialize parameters
    
    def create_random_individual(self) -> Individual:
        # Generate random diet
    
    def tournament_selection(self) -> Individual:
        # Select parent
    
    def crossover(self, parent1, parent2) -> Tuple[Individual, Individual]:
        # Produce offspring
    
    def mutate(self, individual) -> Individual:
        # Apply mutation
    
    def run(self) -> Individual:
        # Main evolution loop
```

#### FitnessCalculator Class
```python
class FitnessCalculator:
    def calculate_nutrition(self, diet) -> Dict:
        # Sum nutritional values
    
    def calculate_cost(self, diet) -> float:
        # Calculate total cost
    
    def calculate_fitness(self, diet) -> Dict:
        # Compute overall fitness
```

## 4. Testing and Evaluation

### 4.1 Unit Tests
24 comprehensive unit tests covering:
- Fitness calculation
- GA operations (selection, crossover, mutation)
- Utility functions (BMI, BMR, TDEE)
- Food data integrity
- Integration tests

**Test Results**: All 24 tests pass ✓

### 4.2 Sample Optimization Results

#### Test Case 1: Default Settings
**Input**: Default nutritional targets, $15 budget
**Result**:
- Fitness Score: 486.72
- Total Cost: $6.50 (under budget)
- All nutritional targets met ✓

| Nutrient | Value | Target Range | Status |
|----------|-------|--------------|--------|
| Calories | 2119.9 | 1800-2500 | ✅ OK |
| Protein | 121.4g | 50-150g | ✅ OK |
| Carbs | 246.0g | 200-350g | ✅ OK |
| Fat | 76.1g | 40-80g | ✅ OK |
| Fiber | 32.5g | 25-40g | ✅ OK |

### 4.3 Convergence Analysis
The GA typically converges within 50-100 generations:
- Fast initial improvement (generations 0-20)
- Gradual refinement (generations 20-50)
- Convergence (generations 50+)

## 5. User Interface

### 5.1 Command Line Interface
- Interactive user profile setup
- Custom GA parameters
- Export to CSV
- Visualization support

### 5.2 Graphical Interface (Tkinter)
Features:
- User profile input
- Adjustable nutritional targets
- Real-time optimization progress
- Diet plan display
- Food database browser
- CSV export

## 6. Conclusions

### 6.1 Achievements
1. ✅ Successfully implemented Genetic Algorithm for diet optimization
2. ✅ Integrated SQLite database for data persistence
3. ✅ Created both CLI and GUI interfaces
4. ✅ Comprehensive testing suite (24 tests, 100% pass rate)
5. ✅ Achieved excellent fitness scores meeting all nutritional constraints

### 6.2 Strengths
- Fast convergence (often finds good solutions within 50 generations)
- Flexible constraint handling
- Personalized recommendations based on user profile
- Cost-effective diet plans

### 6.3 Future Improvements
- Add meal timing/scheduling
- Include micronutrients (vitamins, minerals)
- Add food preference constraints
- Implement meal prep suggestions
- Add recipe recommendations

## 7. How to Run

### Installation
```bash
pip install -r requirements.txt
```

### Usage
```bash
# Command Line
python main.py

# GUI Mode
python main.py --gui

# Run Tests
python main.py --test

# Quick Demo
python main.py --demo
```

## 8. References

1. Holland, J. H. (1992). Genetic algorithms. Scientific American
2. Mitchell, M. (1998). An Introduction to Genetic Algorithms
3. Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning
4. USDA Food Composition Database

---
**Author**: AI Final Term Project  
**Date**: December 2024  
**Course**: Artificial Intelligence - CSP, Genetic Algorithms, Expert Systems
