"""
Food Data Module
Contains nutritional information for various food items.
All values are per 100g serving.
"""

# Food database with nutritional values per 100g
# Format: {food_name: {calories, protein, carbs, fat, fiber, price_per_100g}}

FOOD_DATABASE = {
    # Proteins
    "Chicken Breast": {
        "calories": 165,
        "protein": 31,
        "carbs": 0,
        "fat": 3.6,
        "fiber": 0,
        "price": 0.80,
        "category": "Protein",
        "min_serving": 100,
        "max_serving": 300
    },
    "Eggs": {
        "calories": 155,
        "protein": 13,
        "carbs": 1.1,
        "fat": 11,
        "fiber": 0,
        "price": 0.30,
        "category": "Protein",
        "min_serving": 50,
        "max_serving": 200
    },
    "Salmon": {
        "calories": 208,
        "protein": 20,
        "carbs": 0,
        "fat": 13,
        "fiber": 0,
        "price": 1.50,
        "category": "Protein",
        "min_serving": 100,
        "max_serving": 250
    },
    "Beef (Lean)": {
        "calories": 250,
        "protein": 26,
        "carbs": 0,
        "fat": 15,
        "fiber": 0,
        "price": 1.20,
        "category": "Protein",
        "min_serving": 100,
        "max_serving": 250
    },
    "Tuna": {
        "calories": 132,
        "protein": 28,
        "carbs": 0,
        "fat": 1,
        "fiber": 0,
        "price": 0.90,
        "category": "Protein",
        "min_serving": 80,
        "max_serving": 200
    },
    "Greek Yogurt": {
        "calories": 59,
        "protein": 10,
        "carbs": 3.6,
        "fat": 0.7,
        "fiber": 0,
        "price": 0.50,
        "category": "Protein",
        "min_serving": 100,
        "max_serving": 300
    },
    "Cottage Cheese": {
        "calories": 98,
        "protein": 11,
        "carbs": 3.4,
        "fat": 4.3,
        "fiber": 0,
        "price": 0.45,
        "category": "Protein",
        "min_serving": 100,
        "max_serving": 250
    },
    "Lentils": {
        "calories": 116,
        "protein": 9,
        "carbs": 20,
        "fat": 0.4,
        "fiber": 8,
        "price": 0.20,
        "category": "Protein",
        "min_serving": 100,
        "max_serving": 300
    },
    
    # Carbohydrates
    "Brown Rice": {
        "calories": 112,
        "protein": 2.6,
        "carbs": 24,
        "fat": 0.9,
        "fiber": 1.8,
        "price": 0.15,
        "category": "Carbs",
        "min_serving": 100,
        "max_serving": 300
    },
    "Oatmeal": {
        "calories": 68,
        "protein": 2.5,
        "carbs": 12,
        "fat": 1.4,
        "fiber": 1.7,
        "price": 0.10,
        "category": "Carbs",
        "min_serving": 50,
        "max_serving": 200
    },
    "Whole Wheat Bread": {
        "calories": 247,
        "protein": 13,
        "carbs": 41,
        "fat": 3.4,
        "fiber": 7,
        "price": 0.25,
        "category": "Carbs",
        "min_serving": 50,
        "max_serving": 150
    },
    "Sweet Potato": {
        "calories": 86,
        "protein": 1.6,
        "carbs": 20,
        "fat": 0.1,
        "fiber": 3,
        "price": 0.20,
        "category": "Carbs",
        "min_serving": 100,
        "max_serving": 300
    },
    "Quinoa": {
        "calories": 120,
        "protein": 4.4,
        "carbs": 21,
        "fat": 1.9,
        "fiber": 2.8,
        "price": 0.40,
        "category": "Carbs",
        "min_serving": 80,
        "max_serving": 250
    },
    "Pasta": {
        "calories": 131,
        "protein": 5,
        "carbs": 25,
        "fat": 1.1,
        "fiber": 1.8,
        "price": 0.18,
        "category": "Carbs",
        "min_serving": 80,
        "max_serving": 250
    },
    "White Rice": {
        "calories": 130,
        "protein": 2.7,
        "carbs": 28,
        "fat": 0.3,
        "fiber": 0.4,
        "price": 0.12,
        "category": "Carbs",
        "min_serving": 100,
        "max_serving": 300
    },
    
    # Vegetables
    "Broccoli": {
        "calories": 34,
        "protein": 2.8,
        "carbs": 7,
        "fat": 0.4,
        "fiber": 2.6,
        "price": 0.25,
        "category": "Vegetable",
        "min_serving": 50,
        "max_serving": 200
    },
    "Spinach": {
        "calories": 23,
        "protein": 2.9,
        "carbs": 3.6,
        "fat": 0.4,
        "fiber": 2.2,
        "price": 0.30,
        "category": "Vegetable",
        "min_serving": 30,
        "max_serving": 150
    },
    "Carrots": {
        "calories": 41,
        "protein": 0.9,
        "carbs": 10,
        "fat": 0.2,
        "fiber": 2.8,
        "price": 0.15,
        "category": "Vegetable",
        "min_serving": 50,
        "max_serving": 200
    },
    "Tomatoes": {
        "calories": 18,
        "protein": 0.9,
        "carbs": 3.9,
        "fat": 0.2,
        "fiber": 1.2,
        "price": 0.20,
        "category": "Vegetable",
        "min_serving": 50,
        "max_serving": 200
    },
    "Bell Peppers": {
        "calories": 31,
        "protein": 1,
        "carbs": 6,
        "fat": 0.3,
        "fiber": 2.1,
        "price": 0.35,
        "category": "Vegetable",
        "min_serving": 50,
        "max_serving": 200
    },
    "Cucumber": {
        "calories": 16,
        "protein": 0.7,
        "carbs": 3.6,
        "fat": 0.1,
        "fiber": 0.5,
        "price": 0.18,
        "category": "Vegetable",
        "min_serving": 50,
        "max_serving": 200
    },
    "Green Beans": {
        "calories": 31,
        "protein": 1.8,
        "carbs": 7,
        "fat": 0.1,
        "fiber": 3.4,
        "price": 0.22,
        "category": "Vegetable",
        "min_serving": 50,
        "max_serving": 200
    },
    "Cabbage": {
        "calories": 25,
        "protein": 1.3,
        "carbs": 6,
        "fat": 0.1,
        "fiber": 2.5,
        "price": 0.12,
        "category": "Vegetable",
        "min_serving": 50,
        "max_serving": 200
    },
    
    # Fruits
    "Banana": {
        "calories": 89,
        "protein": 1.1,
        "carbs": 23,
        "fat": 0.3,
        "fiber": 2.6,
        "price": 0.15,
        "category": "Fruit",
        "min_serving": 100,
        "max_serving": 200
    },
    "Apple": {
        "calories": 52,
        "protein": 0.3,
        "carbs": 14,
        "fat": 0.2,
        "fiber": 2.4,
        "price": 0.25,
        "category": "Fruit",
        "min_serving": 100,
        "max_serving": 200
    },
    "Orange": {
        "calories": 47,
        "protein": 0.9,
        "carbs": 12,
        "fat": 0.1,
        "fiber": 2.4,
        "price": 0.20,
        "category": "Fruit",
        "min_serving": 100,
        "max_serving": 250
    },
    "Blueberries": {
        "calories": 57,
        "protein": 0.7,
        "carbs": 14,
        "fat": 0.3,
        "fiber": 2.4,
        "price": 0.80,
        "category": "Fruit",
        "min_serving": 50,
        "max_serving": 150
    },
    "Strawberries": {
        "calories": 32,
        "protein": 0.7,
        "carbs": 8,
        "fat": 0.3,
        "fiber": 2,
        "price": 0.60,
        "category": "Fruit",
        "min_serving": 50,
        "max_serving": 200
    },
    
    # Fats & Nuts
    "Almonds": {
        "calories": 579,
        "protein": 21,
        "carbs": 22,
        "fat": 50,
        "fiber": 12,
        "price": 1.20,
        "category": "Nuts",
        "min_serving": 20,
        "max_serving": 60
    },
    "Olive Oil": {
        "calories": 884,
        "protein": 0,
        "carbs": 0,
        "fat": 100,
        "fiber": 0,
        "price": 1.00,
        "category": "Fat",
        "min_serving": 10,
        "max_serving": 30
    },
    "Peanut Butter": {
        "calories": 588,
        "protein": 25,
        "carbs": 20,
        "fat": 50,
        "fiber": 6,
        "price": 0.50,
        "category": "Nuts",
        "min_serving": 20,
        "max_serving": 60
    },
    "Walnuts": {
        "calories": 654,
        "protein": 15,
        "carbs": 14,
        "fat": 65,
        "fiber": 7,
        "price": 1.50,
        "category": "Nuts",
        "min_serving": 20,
        "max_serving": 50
    },
    "Avocado": {
        "calories": 160,
        "protein": 2,
        "carbs": 9,
        "fat": 15,
        "fiber": 7,
        "price": 0.80,
        "category": "Fat",
        "min_serving": 50,
        "max_serving": 150
    },
    
    # Dairy
    "Milk (Whole)": {
        "calories": 61,
        "protein": 3.2,
        "carbs": 4.8,
        "fat": 3.3,
        "fiber": 0,
        "price": 0.12,
        "category": "Dairy",
        "min_serving": 100,
        "max_serving": 500
    },
    "Cheese (Cheddar)": {
        "calories": 403,
        "protein": 25,
        "carbs": 1.3,
        "fat": 33,
        "fiber": 0,
        "price": 0.90,
        "category": "Dairy",
        "min_serving": 20,
        "max_serving": 80
    },
    "Milk (Skim)": {
        "calories": 34,
        "protein": 3.4,
        "carbs": 5,
        "fat": 0.1,
        "fiber": 0,
        "price": 0.10,
        "category": "Dairy",
        "min_serving": 100,
        "max_serving": 500
    },
}

# Default nutritional targets (daily)
DEFAULT_TARGETS = {
    "calories": {"min": 1800, "max": 2500, "weight": 1.0},
    "protein": {"min": 50, "max": 150, "weight": 1.2},
    "carbs": {"min": 200, "max": 350, "weight": 0.8},
    "fat": {"min": 40, "max": 80, "weight": 0.9},
    "fiber": {"min": 25, "max": 40, "weight": 1.0},
}

# Budget constraint (daily, in dollars)
DEFAULT_BUDGET = 15.0


def get_food_list():
    """Returns list of all food names"""
    return list(FOOD_DATABASE.keys())


def get_food_info(food_name):
    """Returns nutritional info for a food item"""
    return FOOD_DATABASE.get(food_name, None)


def get_foods_by_category(category):
    """Returns foods filtered by category"""
    return {name: info for name, info in FOOD_DATABASE.items() 
            if info["category"] == category}


def get_all_categories():
    """Returns all food categories"""
    return list(set(food["category"] for food in FOOD_DATABASE.values()))
