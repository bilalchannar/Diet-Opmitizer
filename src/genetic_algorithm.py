"""
Genetic Algorithm Module
Implements the genetic algorithm for diet optimization.
"""

import random
import copy
from typing import List, Tuple, Dict, Optional
from src.food_data import FOOD_DATABASE, get_food_list
from src.fitness import FitnessCalculator


class Individual:
    """
    Represents an individual (diet solution) in the population.
    
    Chromosome representation:
    - List of (food_name, quantity) tuples
    - Each gene represents a food item and its serving size
    """
    
    def __init__(self, diet: List[Tuple[str, float]] = None):
        """
        Initialize an individual.
        
        Args:
            diet: Optional initial diet. If None, creates empty diet.
        """
        self.diet = diet if diet else []
        self.fitness = 0
        self.fitness_details = {}
    
    def __repr__(self):
        return f"Individual(fitness={self.fitness:.2f}, foods={len(self.diet)})"
    
    def copy(self):
        """Create a deep copy of this individual"""
        new_ind = Individual(copy.deepcopy(self.diet))
        new_ind.fitness = self.fitness
        new_ind.fitness_details = copy.deepcopy(self.fitness_details)
        return new_ind


class GeneticAlgorithm:
    """
    Genetic Algorithm for Diet Optimization.
    
    This GA evolves a population of diet solutions to find
    optimal meal plans that meet nutritional requirements
    while minimizing cost.
    """
    
    def __init__(
        self,
        population_size: int = 100,
        num_generations: int = 200,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.15,
        tournament_size: int = 5,
        elitism_count: int = 2,
        min_foods: int = 5,
        max_foods: int = 12,
        targets: Dict = None,
        budget: float = None
    ):
        """
        Initialize the genetic algorithm.
        
        Args:
            population_size: Number of individuals in population
            num_generations: Maximum number of generations
            crossover_rate: Probability of crossover
            mutation_rate: Probability of mutation
            tournament_size: Size of tournament for selection
            elitism_count: Number of best individuals to preserve
            min_foods: Minimum number of foods in a diet
            max_foods: Maximum number of foods in a diet
            targets: Nutritional targets dictionary
            budget: Daily budget constraint
        """
        self.population_size = population_size
        self.num_generations = num_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.elitism_count = elitism_count
        self.min_foods = min_foods
        self.max_foods = max_foods
        
        # Initialize fitness calculator
        self.fitness_calculator = FitnessCalculator(targets, budget)
        
        # Available foods
        self.food_list = get_food_list()
        
        # Population
        self.population: List[Individual] = []
        
        # Statistics
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.best_individual = None
        
        # Callbacks
        self.on_generation_callback = None
    
    def set_generation_callback(self, callback):
        """Set callback function called after each generation"""
        self.on_generation_callback = callback
    
    def create_random_individual(self) -> Individual:
        """
        Create a random individual (diet).
        
        Returns:
            A new Individual with random foods
        """
        num_foods = random.randint(self.min_foods, self.max_foods)
        
        # Select random foods
        selected_foods = random.sample(self.food_list, min(num_foods, len(self.food_list)))
        
        diet = []
        for food_name in selected_foods:
            food_info = FOOD_DATABASE[food_name]
            # Random quantity within serving limits
            min_qty = food_info["min_serving"]
            max_qty = food_info["max_serving"]
            quantity = random.uniform(min_qty, max_qty)
            diet.append((food_name, round(quantity)))
        
        return Individual(diet)
    
    def initialize_population(self):
        """Initialize the population with random individuals"""
        self.population = []
        for _ in range(self.population_size):
            self.population.append(self.create_random_individual())
        
        # Evaluate initial population
        self.evaluate_population()
        
        print(f"✓ Initialized population with {self.population_size} individuals")
    
    def evaluate_individual(self, individual: Individual):
        """
        Evaluate fitness of an individual.
        
        Args:
            individual: The individual to evaluate
        """
        result = self.fitness_calculator.calculate_fitness(individual.diet)
        individual.fitness = result["fitness"]
        individual.fitness_details = result
    
    def evaluate_population(self):
        """Evaluate fitness of all individuals in population"""
        for individual in self.population:
            self.evaluate_individual(individual)
        
        # Sort by fitness (descending)
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Update best individual
        if self.population:
            if self.best_individual is None or self.population[0].fitness > self.best_individual.fitness:
                self.best_individual = self.population[0].copy()
    
    def tournament_selection(self) -> Individual:
        """
        Select an individual using tournament selection.
        
        Returns:
            Selected individual
        """
        tournament = random.sample(self.population, min(self.tournament_size, len(self.population)))
        winner = max(tournament, key=lambda x: x.fitness)
        return winner.copy()
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """
        Perform crossover between two parents.
        
        Uses two-point crossover on the food lists.
        
        Args:
            parent1: First parent
            parent2: Second parent
        
        Returns:
            Two offspring individuals
        """
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        # Combine food pools from both parents
        all_foods = {}
        
        for food, qty in parent1.diet:
            all_foods[food] = qty
        
        for food, qty in parent2.diet:
            if food in all_foods:
                # Average the quantities if food exists in both
                all_foods[food] = (all_foods[food] + qty) / 2
            else:
                all_foods[food] = qty
        
        foods_list = list(all_foods.items())
        
        if len(foods_list) < 4:
            return parent1.copy(), parent2.copy()
        
        # Randomly split foods between offspring
        random.shuffle(foods_list)
        
        split1 = random.randint(self.min_foods, min(len(foods_list), self.max_foods))
        split2 = random.randint(self.min_foods, min(len(foods_list), self.max_foods))
        
        child1_diet = foods_list[:split1]
        child2_diet = foods_list[:split2]
        
        return Individual(list(child1_diet)), Individual(list(child2_diet))
    
    def mutate(self, individual: Individual) -> Individual:
        """
        Apply mutation to an individual.
        
        Mutation types:
        1. Add a new food
        2. Remove a food
        3. Change quantity of a food
        4. Swap a food with another
        
        Args:
            individual: The individual to mutate
        
        Returns:
            Mutated individual
        """
        if random.random() > self.mutation_rate:
            return individual
        
        mutant = individual.copy()
        
        if not mutant.diet:
            # If empty diet, add a random food
            food = random.choice(self.food_list)
            food_info = FOOD_DATABASE[food]
            qty = random.uniform(food_info["min_serving"], food_info["max_serving"])
            mutant.diet.append((food, round(qty)))
            return mutant
        
        mutation_type = random.choice(["add", "remove", "quantity", "swap"])
        
        if mutation_type == "add" and len(mutant.diet) < self.max_foods:
            # Add a new food
            current_foods = set(f[0] for f in mutant.diet)
            available = [f for f in self.food_list if f not in current_foods]
            if available:
                food = random.choice(available)
                food_info = FOOD_DATABASE[food]
                qty = random.uniform(food_info["min_serving"], food_info["max_serving"])
                mutant.diet.append((food, round(qty)))
        
        elif mutation_type == "remove" and len(mutant.diet) > self.min_foods:
            # Remove a random food
            idx = random.randint(0, len(mutant.diet) - 1)
            mutant.diet.pop(idx)
        
        elif mutation_type == "quantity":
            # Modify quantity of a random food
            idx = random.randint(0, len(mutant.diet) - 1)
            food_name, old_qty = mutant.diet[idx]
            food_info = FOOD_DATABASE[food_name]
            
            # Adjust quantity by ±30%
            change = random.uniform(-0.3, 0.3)
            new_qty = old_qty * (1 + change)
            new_qty = max(food_info["min_serving"], min(food_info["max_serving"], new_qty))
            mutant.diet[idx] = (food_name, round(new_qty))
        
        elif mutation_type == "swap":
            # Swap a food with another
            if mutant.diet:
                idx = random.randint(0, len(mutant.diet) - 1)
                old_food, _ = mutant.diet[idx]
                current_foods = set(f[0] for f in mutant.diet)
                available = [f for f in self.food_list if f not in current_foods]
                if available:
                    new_food = random.choice(available)
                    food_info = FOOD_DATABASE[new_food]
                    qty = random.uniform(food_info["min_serving"], food_info["max_serving"])
                    mutant.diet[idx] = (new_food, round(qty))
        
        return mutant
    
    def create_next_generation(self):
        """Create the next generation through selection, crossover, and mutation"""
        new_population = []
        
        # Elitism: Keep best individuals
        for i in range(min(self.elitism_count, len(self.population))):
            new_population.append(self.population[i].copy())
        
        # Fill rest with offspring
        while len(new_population) < self.population_size:
            # Selection
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            
            # Crossover
            child1, child2 = self.crossover(parent1, parent2)
            
            # Mutation
            child1 = self.mutate(child1)
            child2 = self.mutate(child2)
            
            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2)
        
        self.population = new_population
    
    def get_statistics(self) -> Dict:
        """Get current generation statistics"""
        if not self.population:
            return {"best": 0, "avg": 0, "worst": 0}
        
        fitnesses = [ind.fitness for ind in self.population]
        return {
            "best": max(fitnesses),
            "avg": sum(fitnesses) / len(fitnesses),
            "worst": min(fitnesses)
        }
    
    def run(self, verbose: bool = True) -> Individual:
        """
        Run the genetic algorithm.
        
        Args:
            verbose: Whether to print progress
        
        Returns:
            Best individual found
        """
        if verbose:
            print("\n" + "="*60)
            print("🧬 GENETIC ALGORITHM - Diet Optimizer")
            print("="*60)
        
        # Initialize population
        self.initialize_population()
        
        # Evolution loop
        for generation in range(self.num_generations):
            # Create next generation
            self.create_next_generation()
            
            # Evaluate population
            self.evaluate_population()
            
            # Get statistics
            stats = self.get_statistics()
            self.best_fitness_history.append(stats["best"])
            self.avg_fitness_history.append(stats["avg"])
            
            # Callback
            if self.on_generation_callback:
                self.on_generation_callback(generation, stats, self.best_individual)
            
            # Print progress
            if verbose and (generation % 20 == 0 or generation == self.num_generations - 1):
                print(f"Generation {generation:4d}: Best={stats['best']:.2f}, "
                      f"Avg={stats['avg']:.2f}, Worst={stats['worst']:.2f}")
            
            # Early stopping if optimal solution found
            if stats["best"] >= 150:  # Very good fitness
                if verbose:
                    print(f"\n✓ Excellent solution found at generation {generation}!")
                break
        
        if verbose:
            print("\n" + "="*60)
            print("🏆 OPTIMIZATION COMPLETE")
            print("="*60)
        
        return self.best_individual
    
    def get_best_solution(self) -> Tuple[Individual, Dict]:
        """
        Get the best solution found.
        
        Returns:
            Tuple of (best individual, detailed analysis)
        """
        if self.best_individual is None:
            return None, None
        
        analysis = self.fitness_calculator.get_detailed_analysis(self.best_individual.diet)
        return self.best_individual, analysis


def optimize_diet(
    targets: Dict = None,
    budget: float = None,
    population_size: int = 100,
    num_generations: int = 200,
    verbose: bool = True
) -> Tuple[List[Tuple[str, float]], Dict]:
    """
    Convenience function to optimize diet.
    
    Args:
        targets: Nutritional targets
        budget: Daily budget
        population_size: GA population size
        num_generations: Number of generations
        verbose: Print progress
    
    Returns:
        Tuple of (optimal diet, analysis)
    """
    ga = GeneticAlgorithm(
        population_size=population_size,
        num_generations=num_generations,
        targets=targets,
        budget=budget
    )
    
    best = ga.run(verbose=verbose)
    _, analysis = ga.get_best_solution()
    
    return best.diet if best else [], analysis
