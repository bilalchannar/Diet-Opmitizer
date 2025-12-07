"""
Utility Functions Module
Contains helper functions for the Diet Optimizer.
"""

from typing import List, Tuple, Dict
from src.food_data import FOOD_DATABASE


def format_diet_plan(diet: List[Tuple[str, float]], analysis: Dict = None) -> str:
    """
    Format a diet plan for display.
    
    Args:
        diet: List of (food_name, quantity) tuples
        analysis: Optional detailed analysis
    
    Returns:
        Formatted string representation
    """
    lines = []
    lines.append("\n" + "="*60)
    lines.append("🥗 OPTIMIZED DIET PLAN")
    lines.append("="*60)
    
    if not diet:
        lines.append("No diet plan available.")
        return "\n".join(lines)
    
    # Group by category
    categorized = {}
    for food_name, quantity in diet:
        if food_name in FOOD_DATABASE:
            category = FOOD_DATABASE[food_name]["category"]
            if category not in categorized:
                categorized[category] = []
            categorized[category].append((food_name, quantity))
    
    # Display foods by category
    total_cost = 0
    for category in sorted(categorized.keys()):
        lines.append(f"\n📦 {category}")
        lines.append("-" * 40)
        for food_name, quantity in categorized[category]:
            food = FOOD_DATABASE[food_name]
            cost = food["price"] * (quantity / 100)
            total_cost += cost
            lines.append(f"  • {food_name}: {quantity}g (${cost:.2f})")
    
    # Summary
    lines.append("\n" + "="*60)
    lines.append("📊 NUTRITIONAL SUMMARY")
    lines.append("="*60)
    
    if analysis:
        nutrients = analysis.get("nutrients", {})
        for nutrient, info in nutrients.items():
            status_icon = "✅" if info["status"] == "OK" else "⚠️"
            lines.append(f"  {status_icon} {nutrient.capitalize()}: {info['value']:.1f} "
                        f"(Target: {info['min']}-{info['max']}) [{info['status']}]")
        
        lines.append(f"\n💰 Total Cost: ${analysis.get('total_cost', 0):.2f}")
        lines.append(f"📈 Fitness Score: {analysis.get('fitness', 0):.2f}")
        
        if analysis.get("within_budget", True):
            lines.append(f"✅ Within budget (${analysis.get('budget', 15):.2f})")
        else:
            lines.append(f"⚠️ Over budget (${analysis.get('budget', 15):.2f})")
    
    lines.append("="*60)
    
    return "\n".join(lines)


def calculate_bmi(weight_kg: float, height_cm: float) -> Tuple[float, str]:
    """
    Calculate BMI and category.
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
    
    Returns:
        Tuple of (BMI value, category string)
    """
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return round(bmi, 1), category


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor equation.
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: "male" or "female"
    
    Returns:
        BMR in calories
    """
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    return round(bmr)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure.
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: One of "sedentary", "light", "moderate", "active", "very_active"
    
    Returns:
        TDEE in calories
    """
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    multiplier = multipliers.get(activity_level.lower(), 1.55)
    return round(bmr * multiplier)


def get_recommended_targets(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str = "maintain"
) -> Dict:
    """
    Get personalized nutritional targets.
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: "male" or "female"
        activity_level: Activity level string
        goal: "lose", "maintain", or "gain"
    
    Returns:
        Dictionary of nutritional targets
    """
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    
    # Adjust calories based on goal
    if goal == "lose":
        target_calories = tdee - 500  # 500 calorie deficit
    elif goal == "gain":
        target_calories = tdee + 300  # 300 calorie surplus
    else:
        target_calories = tdee
    
    # Ensure minimum calories
    target_calories = max(1200, target_calories)
    
    # Calculate macros
    # Protein: 1.6-2.2g per kg for active individuals
    protein_min = round(weight_kg * 1.6)
    protein_max = round(weight_kg * 2.2)
    
    # Fat: 20-35% of calories
    fat_min = round((target_calories * 0.20) / 9)  # 9 cal per gram of fat
    fat_max = round((target_calories * 0.35) / 9)
    
    # Carbs: remaining calories
    carb_min = round((target_calories * 0.40) / 4)  # 4 cal per gram of carbs
    carb_max = round((target_calories * 0.55) / 4)
    
    # Fiber: 25-38g
    fiber_min = 25
    fiber_max = 38
    
    return {
        "calories": {"min": target_calories - 200, "max": target_calories + 200, "weight": 1.0},
        "protein": {"min": protein_min, "max": protein_max, "weight": 1.2},
        "carbs": {"min": carb_min, "max": carb_max, "weight": 0.8},
        "fat": {"min": fat_min, "max": fat_max, "weight": 0.9},
        "fiber": {"min": fiber_min, "max": fiber_max, "weight": 1.0},
    }


def export_diet_to_csv(diet: List[Tuple[str, float]], filename: str):
    """
    Export diet plan to CSV file.
    
    Args:
        diet: List of (food_name, quantity) tuples
        filename: Output filename
    """
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Food', 'Quantity (g)', 'Calories', 'Protein (g)', 
                        'Carbs (g)', 'Fat (g)', 'Fiber (g)', 'Cost ($)'])
        
        for food_name, quantity in diet:
            if food_name in FOOD_DATABASE:
                food = FOOD_DATABASE[food_name]
                factor = quantity / 100
                writer.writerow([
                    food_name,
                    quantity,
                    round(food["calories"] * factor, 1),
                    round(food["protein"] * factor, 1),
                    round(food["carbs"] * factor, 1),
                    round(food["fat"] * factor, 1),
                    round(food["fiber"] * factor, 1),
                    round(food["price"] * factor, 2)
                ])
    
    print(f"✓ Diet plan exported to {filename}")


def visualize_optimization(best_history: List[float], avg_history: List[float]):
    """
    Visualize optimization progress using matplotlib.
    
    Args:
        best_history: List of best fitness values per generation
        avg_history: List of average fitness values per generation
    """
    try:
        import matplotlib.pyplot as plt
        
        generations = range(len(best_history))
        
        plt.figure(figsize=(10, 6))
        plt.plot(generations, best_history, 'b-', label='Best Fitness', linewidth=2)
        plt.plot(generations, avg_history, 'r--', label='Average Fitness', linewidth=1)
        
        plt.xlabel('Generation')
        plt.ylabel('Fitness Score')
        plt.title('Genetic Algorithm Optimization Progress')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('optimization_progress.png', dpi=150)
        plt.show()
        
        print("✓ Visualization saved to optimization_progress.png")
        
    except ImportError:
        print("⚠️ matplotlib not installed. Skipping visualization.")


def visualize_nutrition(analysis: Dict):
    """
    Visualize nutritional breakdown using matplotlib.
    
    Args:
        analysis: Detailed analysis dictionary
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        nutrients = analysis.get("nutrients", {})
        if not nutrients:
            return
        
        # Prepare data
        names = list(nutrients.keys())
        values = [nutrients[n]["value"] for n in names]
        mins = [nutrients[n]["min"] for n in names]
        maxs = [nutrients[n]["max"] for n in names]
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Bar chart showing actual vs target
        x = np.arange(len(names))
        width = 0.25
        
        bars1 = ax1.bar(x - width, mins, width, label='Minimum', color='lightgreen', alpha=0.7)
        bars2 = ax1.bar(x, values, width, label='Actual', color='steelblue')
        bars3 = ax1.bar(x + width, maxs, width, label='Maximum', color='salmon', alpha=0.7)
        
        ax1.set_xlabel('Nutrient')
        ax1.set_ylabel('Amount')
        ax1.set_title('Nutritional Values vs Targets')
        ax1.set_xticks(x)
        ax1.set_xticklabels([n.capitalize() for n in names], rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Percentage of target met
        percentages = [(nutrients[n]["value"] / nutrients[n]["min"]) * 100 
                      for n in names]
        colors = ['green' if 80 <= p <= 150 else 'orange' if 50 <= p else 'red' 
                 for p in percentages]
        
        ax2.barh(names, percentages, color=colors)
        ax2.axvline(x=100, color='black', linestyle='--', label='100% Target')
        ax2.set_xlabel('% of Minimum Target')
        ax2.set_title('Percentage of Nutritional Targets Met')
        ax2.set_xlim(0, max(200, max(percentages) + 20))
        ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig('nutrition_breakdown.png', dpi=150)
        plt.show()
        
        print("✓ Visualization saved to nutrition_breakdown.png")
        
    except ImportError:
        print("⚠️ matplotlib not installed. Skipping visualization.")
