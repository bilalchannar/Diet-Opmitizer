"""
Diet Optimizer - Unit Tests
Tests for the genetic algorithm and fitness functions.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.genetic_algorithm import GeneticAlgorithm, Individual
from src.fitness import FitnessCalculator, evaluate_diet
from src.food_data import FOOD_DATABASE, DEFAULT_TARGETS, get_food_list
from src.utils import calculate_bmi, calculate_bmr, calculate_tdee, get_recommended_targets


class TestFitnessCalculator(unittest.TestCase):
    """Test cases for FitnessCalculator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.calculator = FitnessCalculator()
        self.sample_diet = [
            ("Chicken Breast", 200),
            ("Brown Rice", 150),
            ("Broccoli", 100),
            ("Banana", 100),
            ("Almonds", 30)
        ]
    
    def test_calculate_nutrition(self):
        """Test nutrition calculation"""
        nutrition = self.calculator.calculate_nutrition(self.sample_diet)
        
        self.assertIn("calories", nutrition)
        self.assertIn("protein", nutrition)
        self.assertIn("carbs", nutrition)
        self.assertIn("fat", nutrition)
        self.assertIn("fiber", nutrition)
        
        # All values should be positive
        for key, value in nutrition.items():
            self.assertGreaterEqual(value, 0)
    
    def test_calculate_cost(self):
        """Test cost calculation"""
        cost = self.calculator.calculate_cost(self.sample_diet)
        
        self.assertGreater(cost, 0)
        self.assertIsInstance(cost, float)
    
    def test_empty_diet(self):
        """Test with empty diet"""
        empty_diet = []
        nutrition = self.calculator.calculate_nutrition(empty_diet)
        cost = self.calculator.calculate_cost(empty_diet)
        
        self.assertEqual(nutrition["calories"], 0)
        self.assertEqual(cost, 0)
    
    def test_fitness_calculation(self):
        """Test overall fitness calculation"""
        result = self.calculator.calculate_fitness(self.sample_diet)
        
        self.assertIn("fitness", result)
        self.assertIn("nutrition_score", result)
        self.assertIn("cost_score", result)
        self.assertGreaterEqual(result["fitness"], 0)
    
    def test_detailed_analysis(self):
        """Test detailed analysis"""
        analysis = self.calculator.get_detailed_analysis(self.sample_diet)
        
        self.assertIn("fitness", analysis)
        self.assertIn("total_cost", analysis)
        self.assertIn("nutrients", analysis)
        self.assertIn("within_budget", analysis)


class TestGeneticAlgorithm(unittest.TestCase):
    """Test cases for GeneticAlgorithm"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ga = GeneticAlgorithm(
            population_size=20,
            num_generations=10,
            crossover_rate=0.8,
            mutation_rate=0.15
        )
    
    def test_create_random_individual(self):
        """Test random individual creation"""
        individual = self.ga.create_random_individual()
        
        self.assertIsInstance(individual, Individual)
        self.assertGreater(len(individual.diet), 0)
        self.assertLessEqual(len(individual.diet), self.ga.max_foods)
        self.assertGreaterEqual(len(individual.diet), self.ga.min_foods)
    
    def test_initialize_population(self):
        """Test population initialization"""
        self.ga.initialize_population()
        
        self.assertEqual(len(self.ga.population), self.ga.population_size)
        
        for individual in self.ga.population:
            self.assertIsInstance(individual, Individual)
    
    def test_tournament_selection(self):
        """Test tournament selection"""
        self.ga.initialize_population()
        
        selected = self.ga.tournament_selection()
        
        self.assertIsInstance(selected, Individual)
    
    def test_crossover(self):
        """Test crossover operation"""
        self.ga.initialize_population()
        
        parent1 = self.ga.population[0]
        parent2 = self.ga.population[1]
        
        child1, child2 = self.ga.crossover(parent1, parent2)
        
        self.assertIsInstance(child1, Individual)
        self.assertIsInstance(child2, Individual)
    
    def test_mutation(self):
        """Test mutation operation"""
        self.ga.initialize_population()
        
        original = self.ga.population[0].copy()
        mutated = self.ga.mutate(self.ga.population[0])
        
        self.assertIsInstance(mutated, Individual)
    
    def test_run_ga(self):
        """Test running the GA"""
        best = self.ga.run(verbose=False)
        
        self.assertIsInstance(best, Individual)
        self.assertGreater(best.fitness, 0)
        self.assertGreater(len(self.ga.best_fitness_history), 0)
    
    def test_get_statistics(self):
        """Test statistics calculation"""
        self.ga.initialize_population()
        
        stats = self.ga.get_statistics()
        
        self.assertIn("best", stats)
        self.assertIn("avg", stats)
        self.assertIn("worst", stats)
        self.assertGreaterEqual(stats["best"], stats["avg"])
        self.assertGreaterEqual(stats["avg"], stats["worst"])


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions"""
    
    def test_calculate_bmi(self):
        """Test BMI calculation"""
        bmi, category = calculate_bmi(70, 170)
        
        self.assertAlmostEqual(bmi, 24.2, places=1)
        self.assertEqual(category, "Normal")
        
        # Test underweight
        bmi, category = calculate_bmi(45, 170)
        self.assertEqual(category, "Underweight")
        
        # Test overweight
        bmi, category = calculate_bmi(85, 170)
        self.assertEqual(category, "Overweight")
    
    def test_calculate_bmr(self):
        """Test BMR calculation"""
        bmr_male = calculate_bmr(70, 170, 25, "male")
        bmr_female = calculate_bmr(60, 160, 25, "female")
        
        self.assertGreater(bmr_male, 0)
        self.assertGreater(bmr_female, 0)
        self.assertGreater(bmr_male, bmr_female)  # Generally males have higher BMR
    
    def test_calculate_tdee(self):
        """Test TDEE calculation"""
        bmr = 1700
        
        tdee_sedentary = calculate_tdee(bmr, "sedentary")
        tdee_active = calculate_tdee(bmr, "active")
        
        self.assertGreater(tdee_active, tdee_sedentary)
    
    def test_get_recommended_targets(self):
        """Test personalized target calculation"""
        targets = get_recommended_targets(70, 170, 25, "male", "moderate", "maintain")
        
        self.assertIn("calories", targets)
        self.assertIn("protein", targets)
        self.assertIn("carbs", targets)
        self.assertIn("fat", targets)
        self.assertIn("fiber", targets)
        
        for nutrient, values in targets.items():
            self.assertIn("min", values)
            self.assertIn("max", values)
            self.assertLess(values["min"], values["max"])


class TestFoodData(unittest.TestCase):
    """Test cases for food data"""
    
    def test_food_database_not_empty(self):
        """Test that food database has items"""
        self.assertGreater(len(FOOD_DATABASE), 0)
    
    def test_food_item_structure(self):
        """Test food item has required fields"""
        required_fields = ["calories", "protein", "carbs", "fat", "fiber", "price", "category"]
        
        for name, info in FOOD_DATABASE.items():
            for field in required_fields:
                self.assertIn(field, info, f"{name} missing {field}")
    
    def test_get_food_list(self):
        """Test get_food_list function"""
        food_list = get_food_list()
        
        self.assertIsInstance(food_list, list)
        self.assertEqual(len(food_list), len(FOOD_DATABASE))
    
    def test_default_targets(self):
        """Test default targets are valid"""
        for nutrient, values in DEFAULT_TARGETS.items():
            self.assertIn("min", values)
            self.assertIn("max", values)
            self.assertLess(values["min"], values["max"])


class TestIndividual(unittest.TestCase):
    """Test cases for Individual class"""
    
    def test_individual_creation(self):
        """Test individual creation"""
        diet = [("Chicken Breast", 200), ("Brown Rice", 150)]
        individual = Individual(diet)
        
        self.assertEqual(len(individual.diet), 2)
        self.assertEqual(individual.fitness, 0)
    
    def test_individual_copy(self):
        """Test individual copy"""
        diet = [("Chicken Breast", 200)]
        original = Individual(diet)
        original.fitness = 100
        
        copy = original.copy()
        
        self.assertEqual(copy.fitness, 100)
        self.assertIsNot(copy.diet, original.diet)
        
        # Modifying copy shouldn't affect original
        copy.diet.append(("Eggs", 100))
        self.assertEqual(len(original.diet), 1)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_optimization_cycle(self):
        """Test complete optimization cycle"""
        ga = GeneticAlgorithm(
            population_size=30,
            num_generations=20
        )
        
        best = ga.run(verbose=False)
        best_individual, analysis = ga.get_best_solution()
        
        self.assertIsNotNone(best)
        self.assertIsNotNone(analysis)
        self.assertGreater(best.fitness, 0)
        self.assertIn("nutrients", analysis)
    
    def test_custom_targets(self):
        """Test with custom nutritional targets"""
        custom_targets = {
            "calories": {"min": 1500, "max": 2000, "weight": 1.0},
            "protein": {"min": 80, "max": 120, "weight": 1.2},
            "carbs": {"min": 150, "max": 250, "weight": 0.8},
            "fat": {"min": 40, "max": 70, "weight": 0.9},
            "fiber": {"min": 20, "max": 35, "weight": 1.0},
        }
        
        ga = GeneticAlgorithm(
            population_size=30,
            num_generations=20,
            targets=custom_targets
        )
        
        best = ga.run(verbose=False)
        
        self.assertIsNotNone(best)
        self.assertGreater(best.fitness, 0)


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFitnessCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestGeneticAlgorithm))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestFoodData))
    suite.addTests(loader.loadTestsFromTestCase(TestIndividual))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("="*60)
    print("🧪 Running Diet Optimizer Tests")
    print("="*60)
    
    result = run_tests()
    
    print("\n" + "="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)
