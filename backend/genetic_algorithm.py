import random

def run_genetic_algorithm(input_data):
    food_db = input_data["food_db"]
    if not food_db:
        raise ValueError("Food database is empty. Please add foods first.")

    targets = input_data.get("targets", {"calories": 2000, "protein": 100, "carbs": 250, "fat": 70})
    budget = float(input_data.get("budget", 10))
    max_qty = int(input_data.get("max_qty_per_food", 6))
    
    def totals_cost(diet):
        total = {k: 0.0 for k in ["calories", "protein", "carbs", "fat"]}
        cost = 0.0
        for i, qty in enumerate(diet):
            if qty > 0:
                f = food_db[i]
                for k in total:
                    total[k] += f[k] * qty
                cost += f["price"] * qty
        return total, cost

    def repair(diet):
        diet = [max(0, min(max_qty, int(q))) for q in diet]
        _, cost = totals_cost(diet)
        if cost > budget:
            for _ in range(100):
                removed = False
                for i in sorted(range(len(food_db)), key=lambda x: food_db[x]["price"], reverse=True):
                    if diet[i] > 0:
                        diet[i] -= 1
                        removed = True
                        break
                if not removed or totals_cost(diet)[1] <= budget:
                    break
        return diet

    def fitness(diet):
        diet = repair(diet[:])
        total, cost = totals_cost(diet)
        if cost > budget or sum(diet) == 0:
            return 0.0
        
        weights = {"protein": 2.0, "calories": 1.0, "carbs": 0.6, "fat": 0.6}
        err = sum(weights.get(k, 1) * abs(targets[k] - total[k]) / max(targets[k], 1) for k in targets)
        score = max(1.0, min(100.0, 100.0 - err * 100.0))
        return score

    pop_size = int(input_data.get("population_size", 30))
    generations = int(input_data.get("generations", 50))
    mut_rate = float(input_data.get("mutation_rate", 0.20))
    elite_k = int(input_data.get("elite_k", 4))
    tournament_k = int(input_data.get("tournament_k", 4))
    elite_k = max(1, min(elite_k, pop_size))


    population = [repair([random.randint(0, max_qty) for _ in food_db]) for _ in range(pop_size)]

    for _ in range(generations):
        population.sort(key=fitness, reverse=True)
        next_gen = [p[:] for p in population[:elite_k]]
        
        while len(next_gen) < pop_size:
            p1 = max(random.sample(population, min(tournament_k, len(population))), key=fitness)
            p2 = max(random.sample(population, min(tournament_k, len(population))), key=fitness)
            
            cut = random.randint(1, len(p1) - 1) if len(p1) > 1 else 0
            child = repair(p1[:cut] + p2[cut:])
            
            if random.random() < mut_rate:
                for _ in range(random.randint(1, 2)):
                    idx = random.randint(0, len(child) - 1)
                    child[idx] = max(0, min(max_qty, child[idx] + random.choice([-2, -1, 1, 2])))
            next_gen.append(repair(child))
        
        population = next_gen

    best = max(population, key=fitness)
    best = repair(best)
    total, cost = totals_cost(best)

    return {
        "diet": [{"food": food_db[i]["name"], "qty": int(q)} for i, q in enumerate(best) if q > 0],
        "score": float(fitness(best)),
        "totals": total,
        "cost": cost
    }
