# 🥗 Diet Optimizer using Genetic Algorithm

## Project Overview
This project implements a **Diet Optimizer** using **Genetic Algorithms** to find optimal meal plans that satisfy nutritional requirements while minimizing cost.

## Problem Statement
Finding an optimal diet that meets all nutritional requirements while staying within budget constraints is a complex optimization problem. Traditional methods struggle with the large solution space and multiple conflicting objectives. This project uses Genetic Algorithms to evolve optimal diet plans.

## Why Genetic Algorithm?
- **Large Search Space**: Many possible food combinations exist
- **Multi-objective Optimization**: Balance nutrition, cost, and preferences
- **Constraint Handling**: Meet minimum/maximum nutritional requirements
- **Flexibility**: Easy to add new constraints and objectives

## Features
- ✅ Genetic Algorithm for diet optimization
- ✅ SQLite database for food and nutrition data
- ✅ Customizable nutritional targets
- ✅ Cost optimization
- ✅ Interactive GUI interface
- ✅ Comprehensive testing suite
- ✅ Visualization of optimization progress

## Project Structure
```
Diet Optimizer/
├── src/
│   ├── __init__.py
│   ├── genetic_algorithm.py    # GA implementation
│   ├── fitness.py              # Fitness function
│   ├── database.py             # Database operations
│   ├── food_data.py            # Food and nutrition data
│   └── utils.py                # Utility functions
├── gui/
│   ├── __init__.py
│   └── app.py                  # Tkinter GUI
├── tests/
│   ├── __init__.py
│   └── test_optimizer.py       # Unit tests
├── data/
│   └── diet_optimizer.db       # SQLite database
├── main.py                     # Main entry point
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line
```bash
python main.py
```

### GUI Mode
```bash
python main.py --gui
```

## Algorithm Details

### Chromosome Representation
Each chromosome represents a diet plan with food items and their quantities.

### Fitness Function
```
Fitness = w1 * NutritionScore - w2 * CostPenalty - w3 * ConstraintViolation
```

### Genetic Operators
- **Selection**: Tournament Selection
- **Crossover**: Two-point crossover
- **Mutation**: Random food swap and quantity adjustment

## Nutritional Targets (Daily)
- Calories: 2000-2500 kcal
- Protein: 50-100g
- Carbohydrates: 250-350g
- Fat: 50-80g
- Fiber: 25-35g
- Vitamins and Minerals

## Author
AI Final Term Project - Diet Optimizer

## License
MIT License
