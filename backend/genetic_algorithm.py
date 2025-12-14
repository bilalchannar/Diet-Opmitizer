import random

def run_genetic_algorithm(input_data):
    # Example food database (replace with MongoDB in production)
    food_db = input_data.get('food_db', [
        {"name": "Chicken Breast", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "price": 2.0},
        {"name": "Brown Rice", "calories": 112, "protein": 2.3, "carbs": 23, "fat": 0.8, "price": 0.5},
        {"name": "Broccoli", "calories": 55, "protein": 3.7, "carbs": 11, "fat": 0.6, "price": 0.7},
        {"name": "Eggs", "calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "price": 0.3},
        {"name": "Apple", "calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "price": 0.4}
    ])
    targets = input_data.get('targets', {"calories": 2000, "protein": 100, "carbs": 250, "fat": 70})
    budget = input_data.get('budget', 10)
    population_size = input_data.get('population_size', 30)
    generations = input_data.get('generations', 50)

    def random_diet():
        return [random.randint(0, 3) for _ in food_db]

    def fitness(diet):
        total = {k: 0 for k in targets}
        cost = 0
        for i, qty in enumerate(diet):
            food = food_db[i]
            total["calories"] += food["calories"] * qty
            total["protein"] += food["protein"] * qty
            total["carbs"] += food["carbs"] * qty
            total["fat"] += food["fat"] * qty
            cost += food["price"] * qty
        score = 0
        for k in targets:
            diff = abs(targets[k] - total[k])
            score -= diff
        if cost > budget:
            score -= (cost - budget) * 10
        return score

    population = [random_diet() for _ in range(population_size)]
    for _ in range(generations):
        population.sort(key=fitness, reverse=True)
        next_gen = population[:2]
        while len(next_gen) < population_size:
            p1, p2 = random.choices(population[:10], k=2)
            cross = random.randint(1, len(food_db)-1)
            child = p1[:cross] + p2[cross:]
            if random.random() < 0.2:
                idx = random.randint(0, len(child)-1)
                child[idx] = random.randint(0, 3)
            next_gen.append(child)
        population = next_gen
    best = max(population, key=fitness)
    result = {
        "diet": [{"food": food_db[i]["name"], "qty": qty} for i, qty in enumerate(best) if qty > 0],
        "score": fitness(best)
    }
    return result
