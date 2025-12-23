from typing import Dict, List, Any

def run_csp_solver(input_data: Dict[str, Any]) -> Dict[str, Any]:
    food_db = input_data["food_db"]
    if not food_db:
        raise ValueError("Food database is empty. Please add foods first.")
    
    targets = input_data.get("targets", {"calories": 2000, "protein": 100, "carbs": 250, "fat": 70})
    budget = float(input_data.get("budget", 10))
    max_qty = int(input_data.get("max_qty_per_food", 4))
    tolerance = float(input_data.get("tolerance", 0.25))

    def calc_totals(diet):
        totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
        cost = 0.0
        
        for i, qty in enumerate(diet):
            if qty > 0:
                food = food_db[i]
                totals["calories"] += food["calories"] * qty
                totals["protein"] += food["protein"] * qty
                totals["carbs"] += food["carbs"] * qty
                totals["fat"] += food["fat"] * qty
                cost += food["price"] * qty
        
        return totals, cost

    def is_valid(diet):
        totals, cost = calc_totals(diet)
        
        if cost > budget:
            return False
        
        for nutrient in ["calories", "protein", "carbs", "fat"]:
            target = targets[nutrient]
            min_allowed = target * (1 - tolerance)
            max_allowed = target * (1 + tolerance)
            
            if totals[nutrient] < min_allowed or totals[nutrient] > max_allowed:
                return False
        
        return True

    def calc_score(diet):
        totals, cost = calc_totals(diet)
        
        if cost > budget or sum(diet) == 0:
            return 0.0

        weights = {"protein": 2.0, "calories": 1.0, "carbs": 0.6, "fat": 0.6}
        total_error = 0.0
        
        for nutrient in targets:
            target_val = targets[nutrient]
            actual_val = totals[nutrient]
            error = abs(target_val - actual_val) / max(target_val, 1)
            total_error += error * weights.get(nutrient, 1.0)
        
        score = 100.0 - (total_error * 100.0)
        return max(1.0, min(100.0, score))

    def greedy_start():
        diet = [0] * len(food_db)
        budget_left = budget

        food_indices = sorted(
            range(len(food_db)), 
            key=lambda i: food_db[i]["protein"] / max(food_db[i]["price"], 0.01),
            reverse=True
        )

        for idx in food_indices:
            food = food_db[idx]

            while diet[idx] < max_qty and budget_left >= food["price"]:
                diet[idx] += 1
                budget_left -= food["price"]

                totals, _ = calc_totals(diet)
                exceeded = False
                for nutrient in targets:
                    if totals[nutrient] > targets[nutrient] * (1 + tolerance):
                        exceeded = True
                        break

                if exceeded:
                    diet[idx] -= 1
                    budget_left += food["price"]
                    break
        
        return diet

    def search(diet, food_index, attempts):

        attempts[0] += 1
        if attempts[0] > 50000:
            return None

        if food_index >= len(food_db):
            if is_valid(diet):
                return diet[:] 
            else:
                return None

        _, current_cost = calc_totals(diet)

        for qty in range(max_qty + 1):
            if current_cost + (food_db[food_index]["price"] * qty) > budget:
                continue

            diet[food_index] = qty

            result = search(diet, food_index + 1, attempts)

            if result is not None:
                return result

        diet[food_index] = 0
        return None

    best_diet = greedy_start()
    best_score = calc_score(best_diet) if is_valid(best_diet) else 0.0

    attempts = [0]
    initial_diet = [0] * len(food_db)
    found_diet = search(initial_diet, 0, attempts)

    if found_diet and is_valid(found_diet):
        found_score = calc_score(found_diet)
        if found_score > best_score:
            best_diet = found_diet
            best_score = found_score

    if is_valid(best_diet):
        totals, cost = calc_totals(best_diet)
        return {
            "diet": [
                {"food": food_db[i]["name"], "qty": int(qty)} 
                for i, qty in enumerate(best_diet) 
                if qty > 0
            ],
            "score": float(best_score),
            "totals": totals,
            "cost": cost,
            "nodes_explored": attempts[0],
            "technique": "CSP"
        }

    return {
        "diet": [],
        "score": 0.0,
        "totals": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
        "cost": 0.0,
        "nodes_explored": attempts[0],
        "technique": "CSP"
    }