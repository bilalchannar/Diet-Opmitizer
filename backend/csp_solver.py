from typing import Dict, List, Any, Tuple

def run_csp_solver(input_data: Dict[str, Any]) -> Dict[str, Any]:
    food_db = input_data["food_db"]
    if not food_db:
        raise ValueError("Food database is empty. Please add foods first.")

    targets = input_data.get("targets", {"calories": 2000, "protein": 100, "carbs": 250, "fat": 70})
    budget = float(input_data.get("budget", 10))
    max_qty = int(input_data.get("max_qty_per_food", 4))
    tolerance = float(input_data.get("tolerance", 0.25))
    n_foods = len(food_db)

    def totals_cost(assignment: List[int]) -> Tuple[Dict[str, float], float]:
        total = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
        cost = 0.0
        for i, qty in enumerate(assignment):
            if qty > 0:
                f = food_db[i]
                for k in total:
                    total[k] += f[k] * qty
                cost += f["price"] * qty
        return total, cost

    def is_valid(assignment: List[int], partial: bool = False) -> bool:
        total, cost = totals_cost(assignment)
        if cost > budget:
            return False
        for nut in ["calories", "protein", "carbs", "fat"]:
            t = float(targets.get(nut, 0))
            lower, upper = t * (1 - tolerance), t * (1 + tolerance)
            if partial:
                if total[nut] > upper:
                    return False
            elif total[nut] < lower or total[nut] > upper:
                return False
        return True

    def score(assignment: List[int]) -> float:
        total, cost = totals_cost(assignment)
        if cost > budget or sum(assignment) == 0:
            return 0.0
        error = sum((abs(targets[nut] - total[nut]) / max(targets[nut], 1)) * {"protein": 2, "calories": 1, "carbs": 0.6, "fat": 0.6}.get(nut, 1) for nut in targets)
        return max(1.0, min(100.0, 100.0 - error * 100.0))

    def greedy() -> List[int]:
        sol = [0] * n_foods
        budget_left = budget
        for idx in sorted(range(n_foods), key=lambda i: food_db[i].get("protein", 0) / max(food_db[i]["price"], 0.01), reverse=True):
            while sol[idx] < max_qty and budget_left >= food_db[idx]["price"]:
                sol[idx] += 1
                budget_left -= food_db[idx]["price"]
                if any(totals_cost(sol)[0][n] > targets[n] * (1 + tolerance) for n in targets):
                    sol[idx] -= 1
                    budget_left += food_db[idx]["price"]
                    break
        return sol

    best = greedy()
    best_score = [score(best) if is_valid(best) else 0.0]
    nodes = [0]

    def backtrack(assignment: List[int | None], domains: List[List[int]]):

        nodes[0] += 1
        if nodes[0] > 50000:
            return
        
        unassigned = [i for i in range(n_foods) if assignment[i] is None]
        var = min(unassigned, key=lambda i: len(domains[i])) if unassigned else -1

        if var == -1:
          if is_valid([a if a is not None else 0 for a in assignment]):
              s = score([a if a is not None else 0 for a in assignment])
              if s > best_score[0]:
                best_score[0] = s
                best[:] = [a if a is not None else 0 for a in assignment]
          return


        for val in sorted(domains[var], key=lambda q: food_db[var]["price"] * q):
            assignment[var] = val
            if is_valid([a if a is not None else 0 for a in assignment], partial=True):
                old = [d[:] for d in domains]
                current_cost = sum(food_db[i]["price"] * (assignment[i] or 0) for i in range(n_foods))
                for i in range(n_foods):
                    if assignment[i] is None:
                        domains[i] = [v for v in domains[i] if current_cost + food_db[i]["price"] * v <= budget]
                if all(len(domains[i]) > 0 for i in range(n_foods) if assignment[i] is None):
                   backtrack(assignment, domains)

                for i in range(n_foods):
                    domains[i] = old[i]
            assignment[var] = None
    assignment = [None] * n_foods
    domains = [list(range(0, max_qty + 1)) for _ in range(n_foods)]
    backtrack(assignment, domains)
        

    if is_valid(best):
        total, cost = totals_cost(best)
        return {
            "diet": [{"food": food_db[i]["name"], "qty": int(q)} for i, q in enumerate(best) if q > 0],
            "score": float(best_score[0]),
            "totals": total,
            "cost": cost,
            "nodes_explored": nodes[0],
            "technique": "CSP"
        }
    
    return {"diet": [], "score": 0.0, "totals": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}, "cost": 0.0, "nodes_explored": nodes[0], "technique": "CSP"}
