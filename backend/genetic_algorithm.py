import random

def run_genetic_algorithm(input_data):
    food_db = input_data["food_db"]

    if not food_db:
       raise ValueError("Food database is empty. Please add foods first.")

    targets = input_data.get("targets", {"calories": 2000, "protein": 100, "carbs": 250, "fat": 70})
    budget = float(input_data.get("budget", 10))
    population_size = int(input_data.get("population_size", 30))
    generations = int(input_data.get("generations", 50))
    
    max_qty = int(input_data.get("max_qty_per_food", 6))     
    mutation_rate = float(input_data.get("mutation_rate", 0.20))
    elite_k = int(input_data.get("elite_k", 4))              
    tournament_k = int(input_data.get("tournament_k", 4))    

    weights = input_data.get("fitness_weights", {
        "protein": 2.0,
        "calories": 1.0,
        "carbs": 0.6,
        "fat": 0.6,
    })

    def totals_and_cost(diet):
        total = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
        cost = 0.0
        for i, qty in enumerate(diet):
            if qty <= 0:
                continue
            f = food_db[i]
            total["calories"] += f["calories"] * qty
            total["protein"] += f["protein"] * qty
            total["carbs"] += f["carbs"] * qty
            total["fat"] += f["fat"] * qty
            cost += f["price"] * qty
        return total, cost

    def repair(diet):
        for i in range(len(diet)):
            diet[i] = max(0, min(max_qty, int(diet[i])))

        total, cost = totals_and_cost(diet)
        if cost > budget:

            idxs = sorted(range(len(food_db)), key=lambda i: food_db[i]["price"], reverse=True)
            while cost > budget:
                changed = False
                for i in idxs:
                    if diet[i] > 0:
                        diet[i] -= 1
                        changed = True
                        break
                if not changed:
                    break
                total, cost = totals_and_cost(diet)

        return diet

    def random_diet():
        diet = [random.randint(0, max_qty) for _ in food_db]
        return repair(diet)

    def fitness(diet):
        diet = repair(diet[:]) 
        total, cost = totals_and_cost(diet)

        err = 0.0
        for k in targets:
            t = float(targets[k]) if float(targets[k]) != 0 else 1.0
            diff_pct = abs(t - float(total[k])) / t
            err += weights.get(k, 1.0) * diff_pct

        if cost > budget:
            err += (cost - budget) * 5.0

        if sum(diet) == 0:
            err += 10.0

        # Map error to a positive 1..100 score (higher is better)
        # err == 0 -> 100 (perfect); larger err -> lower score; clamp to [1,100]
        score = 100.0 - (err * 100.0)
        if score < 1.0:
            score = 1.0
        if score > 100.0:
            score = 100.0
        return float(score)

    def tournament_select(pop):
        candidates = random.sample(pop, k=min(tournament_k, len(pop)))
        return max(candidates, key=fitness)

    def crossover(p1, p2):
        if len(p1) <= 1:
            return p1[:]
        cut = random.randint(1, len(p1) - 1)
        child = p1[:cut] + p2[cut:]
        return repair(child)

    def mutate(child):
        if random.random() < mutation_rate:
            for _ in range(random.randint(1, 2)):
                idx = random.randint(0, len(child) - 1)
                step = random.choice([-1, +1, +2, -2])
                child[idx] = max(0, min(max_qty, child[idx] + step))
        return repair(child)

    population = [random_diet() for _ in range(population_size)]

    for _ in range(generations):
        population.sort(key=fitness, reverse=True)

        next_gen = [p[:] for p in population[:max(1, elite_k)]]

        while len(next_gen) < population_size:
            p1 = tournament_select(population)
            p2 = tournament_select(population)
            child = crossover(p1, p2)
            child = mutate(child)
            next_gen.append(child)

        population = next_gen

    best = max(population, key=fitness)
    best = repair(best[:])
    total, cost = totals_and_cost(best)

    return {
        "diet": [{"food": food_db[i]["name"], "qty": int(qty)} for i, qty in enumerate(best) if qty > 0],
        "score": float(fitness(best)),
        "totals": total,
        "cost": cost
    }
