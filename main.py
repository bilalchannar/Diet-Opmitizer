import argparse
import sys
from src.genetic_algorithm import GeneticAlgorithm
from src.food_data import DEFAULT_TARGETS, DEFAULT_BUDGET
from src.utils import format_diet_plan

def run_cli(args):
    print("=" * 60)
    print("🥗 Diet Optimizer - Genetic Algorithm")
    print("=" * 60)
    print(f"\nParameters:")
    print(f"  Population Size: {args.population}")
    print(f"  Generations: {args.generations}")
    print(f"  Crossover Rate: {args.crossover}")
    print(f"  Mutation Rate: {args.mutation}")
    print(f"  Budget: ${args.budget}")
    print("\n" + "=" * 60)
    ga = GeneticAlgorithm(population_size=args.population, num_generations=args.generations, crossover_rate=args.crossover, mutation_rate=args.mutation, targets=DEFAULT_TARGETS, budget=args.budget)
    ga.run(verbose=True)
    best_individual, analysis = ga.get_best_solution()
    print("\n" + "=" * 60)
    print("🏆 OPTIMIZATION COMPLETE")
    print("=" * 60)
    result = format_diet_plan(best_individual.diet, analysis)
    print(result)
    if args.export:
        from src.utils import export_diet_to_csv
        export_diet_to_csv(best_individual.diet, args.export)
        print(f"\n✅ Diet plan exported to: {args.export}")
    return best_individual, analysis

def run_gui():
    from gui.app import DietOptimizerGUI
    app = DietOptimizerGUI()
    app.run()

def run_demo():
    print("=" * 60)
    print("🥗 Diet Optimizer - Demo Mode")
    print("=" * 60)
    ga = GeneticAlgorithm(population_size=50, num_generations=100, crossover_rate=0.8, mutation_rate=0.15, targets=DEFAULT_TARGETS, budget=DEFAULT_BUDGET)
    def simple_callback(gen, stats, best):
        if gen % 20 == 0:
            print(f"Generation {gen}: Best Fitness = {stats['best']:.2f}")
    ga.set_generation_callback(simple_callback)
    ga.run(verbose=False)
    best_individual, analysis = ga.get_best_solution()
    print("\n" + "=" * 60)
    print("🏆 DEMO RESULTS")
    print("=" * 60)
    result = format_diet_plan(best_individual.diet, analysis)
    print(result)
    return best_individual, analysis

def main():
    parser = argparse.ArgumentParser(description="Diet Optimizer using Genetic Algorithm", formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""
Examples:
  python main.py --gui                  Launch graphical interface
  python main.py --demo                 Run quick demo
  python main.py -p 100 -g 200          Custom optimization
  python main.py --export diet.csv      Export results to CSV
    """)
    parser.add_argument("--gui", action="store_true", help="Launch graphical user interface")
    parser.add_argument("--demo", action="store_true", help="Run demo with default parameters")
    parser.add_argument("-p", "--population", type=int, default=100, help="Population size (default: 100)")
    parser.add_argument("-g", "--generations", type=int, default=200, help="Number of generations (default: 200)")
    parser.add_argument("-c", "--crossover", type=float, default=0.8, help="Crossover rate (default: 0.8)")
    parser.add_argument("-m", "--mutation", type=float, default=0.15, help="Mutation rate (default: 0.15)")
    parser.add_argument("-b", "--budget", type=float, default=DEFAULT_BUDGET, help=f"Daily budget (default: ${DEFAULT_BUDGET})")
    parser.add_argument("--export", type=str, help="Export results to CSV file")
    args = parser.parse_args()
    if args.gui:
        run_gui()
    elif args.demo:
        run_demo()
    else:
        run_cli(args)

if __name__ == "__main__":
    main()
