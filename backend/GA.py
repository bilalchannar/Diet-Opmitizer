import random

def run_genetic_algorithm(input_data):
    food_db = input_data["food_db"]
    if not food_db:
        raise ValueError("Food database is empty. Please add foods first.")

    targets = input_data.get("targets", {"calories": 2000, "protein": 100, "carbs": 250, "fat": 70})
    budget = float(input_data.get("budget", 10))
    max_qty = int(input_data.get("max_qty_per_food", 6))
    
    def compute_totals_and_cost(diet):
        totals = {nut: 0.0 for nut in ["calories", "protein", "carbs", "fat"]}
        cost = 0.0
        for i, qty in enumerate(diet):
            if qty > 0:
                food = food_db[i]
                for nut in totals:
                    totals[nut] += food[nut] * qty
                cost += food["price"] * qty
        return totals, cost

    def repair_diet(diet):
        diet = [max(0, min(max_qty, int(q))) for q in diet]
        _, cost = compute_totals_and_cost(diet)
        if cost > budget:
            for _ in range(100):
                removed = False
                for i in sorted(range(len(food_db)), key=lambda x: food_db[x]["price"], reverse=True):
                    if diet[i] > 0:
                        diet[i] -= 1
                        removed = True
                        break
                if not removed or compute_totals_and_cost(diet)[1] <= budget:
                    break
        return diet

    def compute_fitness(diet):
        diet = repair_diet(diet[:])
        totals, cost = compute_totals_and_cost(diet)
        if cost > budget or sum(diet) == 0:
            return 0.0
        weights = {"protein": 2.0, "calories": 1.0, "carbs": 0.6, "fat": 0.6}
        err = sum(weights.get(nut, 1) * abs(targets[nut] - totals[nut]) / max(targets[nut], 1) for nut in targets)
        score = max(1.0, min(100.0, 100.0 - err * 100.0))
        return score

    population_size = int(input_data.get("population_size", 30))
    generations = int(input_data.get("generations", 50))
    mutation_rate = float(input_data.get("mutation_rate", 0.20))
    elite_count = int(input_data.get("elite_k", 4))
    tournament_size = int(input_data.get("tournament_k", 4))
    elite_count = max(1, min(elite_count, population_size))


    population_list = [repair_diet([random.randint(0, max_qty) for _ in food_db]) for _ in range(population_size)]

    for _ in range(generations):
        population_list.sort(key=compute_fitness, reverse=True)
        next_gen = [p[:] for p in population_list[:elite_count]]
        while len(next_gen) < population_size:
            p1 = max(random.sample(population_list, min(tournament_size, len(population_list))), key=compute_fitness)
            p2 = max(random.sample(population_list, min(tournament_size, len(population_list))), key=compute_fitness)
            cut = random.randint(1, len(p1) - 1) if len(p1) > 1 else 0
            child = repair_diet(p1[:cut] + p2[cut:])
            if random.random() < mutation_rate:
                for _ in range(random.randint(1, 2)):
                    idx = random.randint(0, len(child) - 1)
                    child[idx] = max(0, min(max_qty, child[idx] + random.choice([-2, -1, 1, 2])))
            next_gen.append(repair_diet(child))
        population_list = next_gen

    best_solution = max(population_list, key=compute_fitness)
    best_solution = repair_diet(best_solution)
    totals, cost = compute_totals_and_cost(best_solution)

    return {
        "diet": [{"food": food_db[i]["name"], "qty": int(q)} for i, q in enumerate(best_solution) if q > 0],
        "score": float(compute_fitness(best_solution)),
        "totals": totals,
        "cost": cost
    }
