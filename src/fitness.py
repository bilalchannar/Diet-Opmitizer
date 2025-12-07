"""
Fitness Function Module
Calculates the fitness score for diet solutions in the genetic algorithm.
"""

from src.food_data import FOOD_DATABASE, DEFAULT_TARGETS, DEFAULT_BUDGET


class FitnessCalculator:
    """
    Calculates fitness score for a diet solution.
    
    Fitness is based on:
    1. Meeting nutritional requirements (within min-max range)
    2. Minimizing cost
    3. Penalizing constraint violations
    """
    
    def __init__(self, targets=None, budget=None):
        """
        Initialize fitness calculator.
        
        Args:
            targets: Dictionary of nutritional targets with min, max, weight
            budget: Maximum daily budget in dollars
        """
        self.targets = targets if targets else DEFAULT_TARGETS
        self.budget = budget if budget else DEFAULT_BUDGET
        
        # Weights for different fitness components
        self.nutrition_weight = 100.0  # Weight for meeting nutritional goals
        self.cost_weight = 20.0         # Weight for cost minimization
        self.penalty_weight = 50.0      # Penalty for constraint violations
    
    def calculate_nutrition(self, diet):
        """
        Calculate total nutritional values for a diet.
        
        Args:
            diet: List of tuples [(food_name, quantity_in_grams), ...]
        
        Returns:
            Dictionary with total nutritional values
        """
        totals = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "fiber": 0
        }
        
        for food_name, quantity in diet:
            if food_name in FOOD_DATABASE:
                food = FOOD_DATABASE[food_name]
                factor = quantity / 100.0  # Values are per 100g
                
                totals["calories"] += food["calories"] * factor
                totals["protein"] += food["protein"] * factor
                totals["carbs"] += food["carbs"] * factor
                totals["fat"] += food["fat"] * factor
                totals["fiber"] += food["fiber"] * factor
        
        return totals
    
    def calculate_cost(self, diet):
        """
        Calculate total cost of a diet.
        
        Args:
            diet: List of tuples [(food_name, quantity_in_grams), ...]
        
        Returns:
            Total cost in dollars
        """
        total_cost = 0
        
        for food_name, quantity in diet:
            if food_name in FOOD_DATABASE:
                food = FOOD_DATABASE[food_name]
                factor = quantity / 100.0
                total_cost += food["price"] * factor
        
        return total_cost
    
    def calculate_nutrition_score(self, totals):
        """
        Calculate score based on how well nutritional targets are met.
        
        Score is higher when nutrients are within target range.
        Score decreases for values outside the range.
        
        Args:
            totals: Dictionary of total nutritional values
        
        Returns:
            Nutrition score (higher is better)
        """
        score = 0
        
        for nutrient, target in self.targets.items():
            if nutrient in totals:
                value = totals[nutrient]
                min_val = target["min"]
                max_val = target["max"]
                weight = target["weight"]
                
                if min_val <= value <= max_val:
                    # Perfect score for being in range
                    # Bonus for being closer to middle of range
                    mid = (min_val + max_val) / 2
                    range_size = max_val - min_val
                    distance_from_mid = abs(value - mid) / (range_size / 2)
                    nutrient_score = (1 - 0.3 * distance_from_mid) * weight
                    score += nutrient_score
                elif value < min_val:
                    # Penalty for being below minimum
                    deficit_ratio = (min_val - value) / min_val
                    penalty = min(deficit_ratio * 2, 1) * weight
                    score -= penalty
                else:  # value > max_val
                    # Penalty for being above maximum
                    excess_ratio = (value - max_val) / max_val
                    penalty = min(excess_ratio * 2, 1) * weight
                    score -= penalty
        
        return score
    
    def calculate_cost_score(self, total_cost):
        """
        Calculate score based on cost efficiency.
        
        Lower cost = higher score.
        
        Args:
            total_cost: Total cost of diet
        
        Returns:
            Cost score (higher is better)
        """
        if total_cost <= self.budget:
            # Reward for being under budget
            savings_ratio = (self.budget - total_cost) / self.budget
            return 1 + savings_ratio * 0.5  # Max 1.5 for very cheap diets
        else:
            # Penalty for exceeding budget
            excess_ratio = (total_cost - self.budget) / self.budget
            return max(0, 1 - excess_ratio * 2)  # Severe penalty for over budget
    
    def calculate_variety_bonus(self, diet):
        """
        Calculate bonus for diet variety.
        
        Args:
            diet: List of tuples [(food_name, quantity_in_grams), ...]
        
        Returns:
            Variety bonus score
        """
        if not diet:
            return 0
        
        # Count unique categories
        categories = set()
        for food_name, _ in diet:
            if food_name in FOOD_DATABASE:
                categories.add(FOOD_DATABASE[food_name]["category"])
        
        # Bonus for having foods from multiple categories
        # Ideal is 4-5 different categories
        num_categories = len(categories)
        if num_categories >= 4:
            return 0.2
        elif num_categories >= 3:
            return 0.1
        elif num_categories >= 2:
            return 0.05
        return 0
    
    def calculate_fitness(self, diet):
        """
        Calculate overall fitness score for a diet.
        
        Args:
            diet: List of tuples [(food_name, quantity_in_grams), ...]
        
        Returns:
            Dictionary with fitness score and detailed breakdown
        """
        # Calculate all components
        nutrition_totals = self.calculate_nutrition(diet)
        total_cost = self.calculate_cost(diet)
        
        nutrition_score = self.calculate_nutrition_score(nutrition_totals)
        cost_score = self.calculate_cost_score(total_cost)
        variety_bonus = self.calculate_variety_bonus(diet)
        
        # Weighted combination
        fitness = (
            self.nutrition_weight * nutrition_score +
            self.cost_weight * cost_score +
            self.nutrition_weight * variety_bonus
        )
        
        # Ensure fitness is non-negative
        fitness = max(0, fitness)
        
        return {
            "fitness": fitness,
            "nutrition_score": nutrition_score,
            "cost_score": cost_score,
            "variety_bonus": variety_bonus,
            "total_cost": total_cost,
            "nutrition": nutrition_totals
        }
    
    def get_detailed_analysis(self, diet):
        """
        Get detailed analysis of a diet.
        
        Args:
            diet: List of tuples [(food_name, quantity_in_grams), ...]
        
        Returns:
            Dictionary with detailed analysis
        """
        result = self.calculate_fitness(diet)
        nutrition = result["nutrition"]
        
        # Add target comparison
        analysis = {
            "fitness": result["fitness"],
            "total_cost": result["total_cost"],
            "budget": self.budget,
            "within_budget": result["total_cost"] <= self.budget,
            "nutrients": {}
        }
        
        for nutrient, target in self.targets.items():
            value = nutrition.get(nutrient, 0)
            min_val = target["min"]
            max_val = target["max"]
            
            status = "OK"
            if value < min_val:
                status = "LOW"
            elif value > max_val:
                status = "HIGH"
            
            analysis["nutrients"][nutrient] = {
                "value": round(value, 1),
                "min": min_val,
                "max": max_val,
                "status": status,
                "percentage_of_min": round((value / min_val) * 100, 1) if min_val > 0 else 0
            }
        
        return analysis


def evaluate_diet(diet, targets=None, budget=None):
    """
    Convenience function to evaluate a diet.
    
    Args:
        diet: List of tuples [(food_name, quantity_in_grams), ...]
        targets: Optional custom nutritional targets
        budget: Optional custom budget
    
    Returns:
        Fitness score
    """
    calculator = FitnessCalculator(targets, budget)
    return calculator.calculate_fitness(diet)["fitness"]
