from typing import List, Tuple, Dict
from src.food_data import FOOD_DATABASE

def format_diet_plan(diet: List[Tuple[str, float]], analysis: Dict = None) -> str:
    lines = []
    lines.append("\n" + "="*60)
    lines.append("🥗 OPTIMIZED DIET PLAN")
    lines.append("="*60)
    if not diet:
        lines.append("No diet plan available.")
        return "\n".join(lines)
    categorized = {}
    for food_name, quantity in diet:
        if food_name in FOOD_DATABASE:
            category = FOOD_DATABASE[food_name]["category"]
            if category not in categorized:
                categorized[category] = []
            categorized[category].append((food_name, quantity))
    total_cost = 0
    for category in sorted(categorized.keys()):
        lines.append(f"\n📦 {category}")
        lines.append("-" * 40)
        for food_name, quantity in categorized[category]:
            food = FOOD_DATABASE[food_name]
            cost = food["price"] * (quantity / 100)
            total_cost += cost
            lines.append(f"  • {food_name}: {quantity}g (${cost:.2f})")
    lines.append("\n" + "="*60)
    lines.append("📊 NUTRITIONAL SUMMARY")
    lines.append("="*60)
    if analysis:
        nutrients = analysis.get("nutrients", {})
        for nutrient, info in nutrients.items():
            status_icon = "✅" if info["status"] == "OK" else "⚠️"
            lines.append(f"  {status_icon} {nutrient.capitalize()}: {info['value']:.1f} (Target: {info['min']}-{info['max']}) [{info['status']}]")
        lines.append(f"\n💰 Total Cost: ${analysis.get('total_cost', 0):.2f}")
        lines.append(f"📈 Fitness Score: {analysis.get('fitness', 0):.2f}")
        if analysis.get("within_budget", True):
            lines.append(f"✅ Within budget (${analysis.get('budget', 15):.2f})")
        else:
            lines.append(f"⚠️ Over budget (${analysis.get('budget', 15):.2f})")
    lines.append("="*60)
    return "\n".join(lines)

def calculate_bmi(weight_kg: float, height_cm: float) -> Tuple[float, str]:
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
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    return round(bmr)

def calculate_tdee(bmr: float, activity_level: str) -> float:
    multipliers = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "very_active": 1.9}
    multiplier = multipliers.get(activity_level.lower(), 1.55)
    return round(bmr * multiplier)

def get_recommended_targets(weight_kg: float, height_cm: float, age: int, gender: str, activity_level: str, goal: str = "maintain") -> Dict:
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    if goal == "lose":
        target_calories = tdee - 500
    elif goal == "gain":
        target_calories = tdee + 300
    else:
        target_calories = tdee
    target_calories = max(1200, target_calories)
    protein_min = round(weight_kg * 1.6)
    protein_max = round(weight_kg * 2.2)
    fat_min = round((target_calories * 0.20) / 9)
    fat_max = round((target_calories * 0.35) / 9)
    carb_min = round((target_calories * 0.40) / 4)
    carb_max = round((target_calories * 0.55) / 4)
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
    import csv
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Food', 'Quantity (g)', 'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Fiber (g)', 'Cost ($)'])
        for food_name, quantity in diet:
            if food_name in FOOD_DATABASE:
                food = FOOD_DATABASE[food_name]
                factor = quantity / 100
                writer.writerow([food_name, quantity, round(food["calories"] * factor, 1), round(food["protein"] * factor, 1), round(food["carbs"] * factor, 1), round(food["fat"] * factor, 1), round(food["fiber"] * factor, 1), round(food["price"] * factor, 2)])
    print(f"✓ Diet plan exported to {filename}")

def visualize_optimization(best_history: List[float], avg_history: List[float]):
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
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        nutrients = analysis.get("nutrients", {})
        if not nutrients:
            return
        names = list(nutrients.keys())
        values = [nutrients[n]["value"] for n in names]
        mins = [nutrients[n]["min"] for n in names]
        maxs = [nutrients[n]["max"] for n in names]
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
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
        percentages = [(nutrients[n]["value"] / nutrients[n]["min"]) * 100 for n in names]
        colors = ['green' if 80 <= p <= 150 else 'orange' if 50 <= p else 'red' for p in percentages]
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
