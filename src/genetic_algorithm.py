import random
import copy
from typing import List, Tuple, Dict, Optional
from src.food_data import FOOD_DATABASE, get_food_list
from src.fitness import FitnessCalculator

class Individual:
    def __init__(self, diet: List[Tuple[str, float]] = None):
        self.diet = diet if diet else []
        self.fitness = 0
        self.fitness_details = {}
    def __repr__(self):
        return f"Individual(fitness={self.fitness:.2f}, foods={len(self.diet)})"
    def copy(self):
        new_ind = Individual(copy.deepcopy(self.diet))
        new_ind.fitness = self.fitness
        new_ind.fitness_details = copy.deepcopy(self.fitness_details)
        return new_ind

class GeneticAlgorithm:
    def __init__(self, population_size: int = 100, num_generations: int = 200, crossover_rate: float = 0.8, mutation_rate: float = 0.15, tournament_size: int = 5, elitism_count: int = 2, min_foods: int = 5, max_foods: int = 12, targets: Dict = None, budget: float = None):
        self.population_size = population_size
        self.num_generations = num_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.elitism_count = elitism_count
        self.min_foods = min_foods
        self.max_foods = max_foods
        self.fitness_calculator = FitnessCalculator(targets, budget)
        self.food_list = get_food_list()
        self.population: List[Individual] = []
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.best_individual = None
        self.on_generation_callback = None
    def set_generation_callback(self, callback):
        self.on_generation_callback = callback
    def create_random_individual(self) -> Individual:
        num_foods = random.randint(self.min_foods, self.max_foods)
        selected_foods = random.sample(self.food_list, min(num_foods, len(self.food_list)))
        diet = []
        for food_name in selected_foods:
            food_info = FOOD_DATABASE[food_name]
            min_qty = food_info["min_serving"]
            max_qty = food_info["max_serving"]
            quantity = random.uniform(min_qty, max_qty)
            diet.append((food_name, round(quantity)))
        return Individual(diet)
    def initialize_population(self):
        self.population = []
        for _ in range(self.population_size):
            self.population.append(self.create_random_individual())
        self.evaluate_population()
        print(f"✓ Initialized population with {self.population_size} individuals")
    def evaluate_individual(self, individual: Individual):
        result = self.fitness_calculator.calculate_fitness(individual.diet)
        individual.fitness = result["fitness"]
        individual.fitness_details = result
    def evaluate_population(self):
        for individual in self.population:
            self.evaluate_individual(individual)
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        if self.population:
            if self.best_individual is None or self.population[0].fitness > self.best_individual.fitness:
                self.best_individual = self.population[0].copy()
    def tournament_selection(self) -> Individual:
        tournament = random.sample(self.population, min(self.tournament_size, len(self.population)))
        winner = max(tournament, key=lambda x: x.fitness)
        return winner.copy()
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        all_foods = {}
        for food, qty in parent1.diet:
            all_foods[food] = qty
        for food, qty in parent2.diet:
            if food in all_foods:
                all_foods[food] = (all_foods[food] + qty) / 2
            else:
                all_foods[food] = qty
        foods_list = list(all_foods.items())
        if len(foods_list) < 4:
            return parent1.copy(), parent2.copy()
        random.shuffle(foods_list)
        split1 = random.randint(self.min_foods, min(len(foods_list), self.max_foods))
        split2 = random.randint(self.min_foods, min(len(foods_list), self.max_foods))
        child1_diet = foods_list[:split1]
        child2_diet = foods_list[:split2]
        return Individual(list(child1_diet)), Individual(list(child2_diet))
    def mutate(self, individual: Individual) -> Individual:
        if random.random() > self.mutation_rate:
            return individual
        mutant = individual.copy()
        if not mutant.diet:
            food = random.choice(self.food_list)
            food_info = FOOD_DATABASE[food]
            qty = random.uniform(food_info["min_serving"], food_info["max_serving"])
            mutant.diet.append((food, round(qty)))
            return mutant
        mutation_type = random.choice(["add", "remove", "quantity", "swap"])
        if mutation_type == "add" and len(mutant.diet) < self.max_foods:
            current_foods = set(f[0] for f in mutant.diet)
            available = [f for f in self.food_list if f not in current_foods]
            if available:
                food = random.choice(available)
                food_info = FOOD_DATABASE[food]
                qty = random.uniform(food_info["min_serving"], food_info["max_serving"])
                mutant.diet.append((food, round(qty)))
        elif mutation_type == "remove" and len(mutant.diet) > self.min_foods:
            idx = random.randint(0, len(mutant.diet) - 1)
            mutant.diet.pop(idx)
        elif mutation_type == "quantity":
            idx = random.randint(0, len(mutant.diet) - 1)
            food_name, old_qty = mutant.diet[idx]
            food_info = FOOD_DATABASE[food_name]
            change = random.uniform(-0.3, 0.3)
            new_qty = old_qty * (1 + change)
            new_qty = max(food_info["min_serving"], min(food_info["max_serving"], new_qty))
            mutant.diet[idx] = (food_name, round(new_qty))
        elif mutation_type == "swap":
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
        new_population = []
        for i in range(min(self.elitism_count, len(self.population))):
            new_population.append(self.population[i].copy())
        while len(new_population) < self.population_size:
            parent1 = self.tournament_selection()
            parent2 = self.tournament_selection()
            child1, child2 = self.crossover(parent1, parent2)
            child1 = self.mutate(child1)
            child2 = self.mutate(child2)
            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2)
        self.population = new_population
    def get_statistics(self) -> Dict:
        if not self.population:
            return {"best": 0, "avg": 0, "worst": 0}
        fitnesses = [ind.fitness for ind in self.population]
        return {"best": max(fitnesses), "avg": sum(fitnesses) / len(fitnesses), "worst": min(fitnesses)}
    def run(self, verbose: bool = True) -> Individual:
        if verbose:
            print("\n" + "="*60)
            print("🧬 GENETIC ALGORITHM - Diet Optimizer")
            print("="*60)
        self.initialize_population()
        for generation in range(self.num_generations):
            self.create_next_generation()
            self.evaluate_population()
            stats = self.get_statistics()
            self.best_fitness_history.append(stats["best"])
            self.avg_fitness_history.append(stats["avg"])
            if self.on_generation_callback:
                self.on_generation_callback(generation, stats, self.best_individual)
            if verbose and (generation % 20 == 0 or generation == self.num_generations - 1):
                print(f"Generation {generation:4d}: Best={stats['best']:.2f}, Avg={stats['avg']:.2f}, Worst={stats['worst']:.2f}")
            if stats["best"] >= 150:
                if verbose:
                    print(f"\n✓ Excellent solution found at generation {generation}!")
                break
        if verbose:
            print("\n" + "="*60)
            print("🏆 OPTIMIZATION COMPLETE")
            print("="*60)
        return self.best_individual
    def get_best_solution(self) -> Tuple[Individual, Dict]:
        if self.best_individual is None:
            return None, None
        analysis = self.fitness_calculator.get_detailed_analysis(self.best_individual.diet)
        return self.best_individual, analysis

def optimize_diet(targets: Dict = None, budget: float = None, population_size: int = 100, num_generations: int = 200, verbose: bool = True) -> Tuple[List[Tuple[str, float]], Dict]:
    ga = GeneticAlgorithm(population_size=population_size, num_generations=num_generations, targets=targets, budget=budget)
    best = ga.run(verbose=verbose)
    _, analysis = ga.get_best_solution()
    return best.diet if best else [], analysis
