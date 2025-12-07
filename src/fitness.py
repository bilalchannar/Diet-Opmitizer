from src.food_data import FOOD_DATABASE, DEFAULT_TARGETS, DEFAULT_BUDGET

class FitnessCalculator:
    def __init__(self, targets=None, budget=None):
        self.targets = targets if targets else DEFAULT_TARGETS
        self.budget = budget if budget else DEFAULT_BUDGET
        self.nutrition_weight = 100.0
        self.cost_weight = 20.0
        self.penalty_weight = 50.0
    def calculate_nutrition(self, diet):
        totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}
        for food_name, quantity in diet:
            if food_name in FOOD_DATABASE:
                food = FOOD_DATABASE[food_name]
                factor = quantity / 100.0
                totals["calories"] += food["calories"] * factor
                totals["protein"] += food["protein"] * factor
                totals["carbs"] += food["carbs"] * factor
                totals["fat"] += food["fat"] * factor
                totals["fiber"] += food["fiber"] * factor
        return totals
    def calculate_cost(self, diet):
        total_cost = 0
        for food_name, quantity in diet:
            if food_name in FOOD_DATABASE:
                food = FOOD_DATABASE[food_name]
                factor = quantity / 100.0
                total_cost += food["price"] * factor
        return total_cost
    def calculate_nutrition_score(self, totals):
        score = 0
        for nutrient, target in self.targets.items():
            if nutrient in totals:
                value = totals[nutrient]
                min_val = target["min"]
                max_val = target["max"]
                weight = target["weight"]
                if min_val <= value <= max_val:
                    mid = (min_val + max_val) / 2
                    range_size = max_val - min_val
                    distance_from_mid = abs(value - mid) / (range_size / 2)
                    nutrient_score = (1 - 0.3 * distance_from_mid) * weight
                    score += nutrient_score
                elif value < min_val:
                    deficit_ratio = (min_val - value) / min_val
                    penalty = min(deficit_ratio * 2, 1) * weight
                    score -= penalty
                else:
                    excess_ratio = (value - max_val) / max_val
                    penalty = min(excess_ratio * 2, 1) * weight
                    score -= penalty
        return score
    def calculate_cost_score(self, total_cost):
        if total_cost <= self.budget:
            savings_ratio = (self.budget - total_cost) / self.budget
            return 1 + savings_ratio * 0.5
        else:
            excess_ratio = (total_cost - self.budget) / self.budget
            return max(0, 1 - excess_ratio * 2)
    def calculate_variety_bonus(self, diet):
        if not diet:
            return 0
        categories = set()
        for food_name, _ in diet:
            if food_name in FOOD_DATABASE:
                categories.add(FOOD_DATABASE[food_name]["category"])
        num_categories = len(categories)
        if num_categories >= 4:
            return 0.2
        elif num_categories >= 3:
            return 0.1
        elif num_categories >= 2:
            return 0.05
        return 0
    def calculate_fitness(self, diet):
        nutrition_totals = self.calculate_nutrition(diet)
        total_cost = self.calculate_cost(diet)
        nutrition_score = self.calculate_nutrition_score(nutrition_totals)
        cost_score = self.calculate_cost_score(total_cost)
        variety_bonus = self.calculate_variety_bonus(diet)
        fitness = (self.nutrition_weight * nutrition_score + self.cost_weight * cost_score + self.nutrition_weight * variety_bonus)
        fitness = max(0, fitness)
        return {"fitness": fitness, "nutrition_score": nutrition_score, "cost_score": cost_score, "variety_bonus": variety_bonus, "total_cost": total_cost, "nutrition": nutrition_totals}
    def get_detailed_analysis(self, diet):
        result = self.calculate_fitness(diet)
        nutrition = result["nutrition"]
        analysis = {"fitness": result["fitness"], "total_cost": result["total_cost"], "budget": self.budget, "within_budget": result["total_cost"] <= self.budget, "nutrients": {}}
        for nutrient, target in self.targets.items():
            value = nutrition.get(nutrient, 0)
            min_val = target["min"]
            max_val = target["max"]
            status = "OK"
            if value < min_val:
                status = "LOW"
            elif value > max_val:
                status = "HIGH"
            analysis["nutrients"][nutrient] = {"value": round(value, 1), "min": min_val, "max": max_val, "status": status, "percentage_of_min": round((value / min_val) * 100, 1) if min_val > 0 else 0}
        return analysis

def evaluate_diet(diet, targets=None, budget=None):
    calculator = FitnessCalculator(targets, budget)
    return calculator.calculate_fitness(diet)["fitness"]
