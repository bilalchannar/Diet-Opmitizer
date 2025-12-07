#!/usr/bin/env python3
"""
Diet Optimizer - Main Entry Point
===================================
An AI-powered diet optimization system using Genetic Algorithms.

This project finds optimal meal plans that:
- Meet nutritional requirements (calories, protein, carbs, fat, fiber)
- Stay within budget constraints
- Provide variety in food choices

Usage:
    python main.py          # Run command line optimization
    python main.py --gui    # Run with graphical interface
    python main.py --test   # Run unit tests

Author: AI Final Term Project
Date: 2024
"""

import argparse
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.genetic_algorithm import GeneticAlgorithm, optimize_diet
from src.fitness import FitnessCalculator
from src.database import DietDatabase, get_database
from src.food_data import FOOD_DATABASE, DEFAULT_TARGETS, DEFAULT_BUDGET
from src.utils import (
    format_diet_plan, 
    visualize_optimization, 
    visualize_nutrition,
    export_diet_to_csv,
    get_recommended_targets,
    calculate_bmi
)


def print_header():
    """Print application header"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🥗 DIET OPTIMIZER - Genetic Algorithm                 ║
║                                                              ║
║        AI Final Term Project                                 ║
║        Constraint Satisfaction & Optimization                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def print_food_database():
    """Print available foods"""
    print("\n" + "="*60)
    print("📦 AVAILABLE FOOD DATABASE")
    print("="*60)
    
    # Group by category
    categories = {}
    for name, info in FOOD_DATABASE.items():
        cat = info["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((name, info))
    
    for category in sorted(categories.keys()):
        print(f"\n🏷️  {category}:")
        print("-" * 40)
        for name, info in categories[category]:
            print(f"  • {name}: {info['calories']} cal, "
                  f"P:{info['protein']}g, C:{info['carbs']}g, "
                  f"F:{info['fat']}g, ${info['price']:.2f}/100g")


def get_user_profile():
    """Get user profile interactively"""
    print("\n" + "="*60)
    print("👤 USER PROFILE SETUP")
    print("="*60)
    
    try:
        print("\nEnter your details (press Enter for defaults):\n")
        
        age_input = input("Age [25]: ").strip()
        age = int(age_input) if age_input else 25
        
        weight_input = input("Weight in kg [70]: ").strip()
        weight = float(weight_input) if weight_input else 70.0
        
        height_input = input("Height in cm [170]: ").strip()
        height = float(height_input) if height_input else 170.0
        
        gender_input = input("Gender (male/female) [male]: ").strip().lower()
        gender = gender_input if gender_input in ["male", "female"] else "male"
        
        print("\nActivity levels: sedentary, light, moderate, active, very_active")
        activity_input = input("Activity level [moderate]: ").strip().lower()
        activity = activity_input if activity_input else "moderate"
        
        print("\nGoals: lose, maintain, gain")
        goal_input = input("Goal [maintain]: ").strip().lower()
        goal = goal_input if goal_input in ["lose", "maintain", "gain"] else "maintain"
        
        budget_input = input("Daily budget in $ [15]: ").strip()
        budget = float(budget_input) if budget_input else DEFAULT_BUDGET
        
        # Calculate BMI
        bmi, bmi_category = calculate_bmi(weight, height)
        print(f"\n📊 Your BMI: {bmi} ({bmi_category})")
        
        # Get recommended targets
        targets = get_recommended_targets(weight, height, age, gender, activity, goal)
        
        print("\n📋 Calculated Nutritional Targets:")
        for nutrient, values in targets.items():
            print(f"  • {nutrient.capitalize()}: {values['min']:.0f} - {values['max']:.0f}")
        
        use_custom = input("\nUse these targets? (y/n) [y]: ").strip().lower()
        
        if use_custom == 'n':
            targets = DEFAULT_TARGETS
            print("Using default targets instead.")
        
        return targets, budget
        
    except (ValueError, KeyboardInterrupt):
        print("\nUsing default settings...")
        return DEFAULT_TARGETS, DEFAULT_BUDGET


def run_command_line():
    """Run command line interface"""
    print_header()
    
    # Initialize database
    print("\n📁 Initializing database...")
    db = get_database()
    
    # Show options
    print("\n" + "="*60)
    print("OPTIONS")
    print("="*60)
    print("1. Quick optimization (default settings)")
    print("2. Custom optimization (enter profile)")
    print("3. View food database")
    print("4. Run tests")
    print("5. Exit")
    
    choice = input("\nSelect option [1]: ").strip()
    
    if choice == "3":
        print_food_database()
        return
    
    if choice == "4":
        run_tests()
        return
    
    if choice == "5":
        print("\nGoodbye! 👋")
        return
    
    # Get settings
    if choice == "2":
        targets, budget = get_user_profile()
    else:
        targets = DEFAULT_TARGETS
        budget = DEFAULT_BUDGET
        print("\nUsing default settings...")
    
    # Get GA parameters
    print("\n" + "="*60)
    print("🧬 GENETIC ALGORITHM PARAMETERS")
    print("="*60)
    
    try:
        pop_input = input("Population size [100]: ").strip()
        population_size = int(pop_input) if pop_input else 100
        
        gen_input = input("Number of generations [200]: ").strip()
        num_generations = int(gen_input) if gen_input else 200
    except ValueError:
        population_size = 100
        num_generations = 200
    
    # Run optimization
    print("\n🚀 Starting optimization...")
    
    ga = GeneticAlgorithm(
        population_size=population_size,
        num_generations=num_generations,
        targets=targets,
        budget=budget
    )
    
    best = ga.run(verbose=True)
    
    # Get results
    best_individual, analysis = ga.get_best_solution()
    
    # Display results
    if best_individual:
        result_text = format_diet_plan(best_individual.diet, analysis)
        print(result_text)
        
        # Save to database
        try:
            db.clear_optimization_history()
            for i, (best_fit, avg_fit) in enumerate(zip(ga.best_fitness_history, 
                                                         ga.avg_fitness_history)):
                db.save_optimization_history(i, best_fit, avg_fit, 0)
            
            plan_id = db.save_diet_plan(
                plan_data={
                    "fitness": analysis["fitness"],
                    "total_cost": analysis["total_cost"],
                    "calories": analysis["nutrients"]["calories"]["value"],
                    "protein": analysis["nutrients"]["protein"]["value"],
                    "carbs": analysis["nutrients"]["carbs"]["value"],
                    "fat": analysis["nutrients"]["fat"]["value"],
                    "fiber": analysis["nutrients"]["fiber"]["value"]
                },
                food_items=best_individual.diet,
                plan_name="CLI Optimized Diet"
            )
            print(f"\n✓ Diet plan saved to database (ID: {plan_id})")
        except Exception as e:
            print(f"\n⚠️ Could not save to database: {e}")
        
        # Ask for visualization
        show_viz = input("\nShow visualization? (y/n) [y]: ").strip().lower()
        if show_viz != 'n':
            try:
                visualize_optimization(ga.best_fitness_history, ga.avg_fitness_history)
                visualize_nutrition(analysis)
            except Exception as e:
                print(f"⚠️ Visualization not available: {e}")
        
        # Ask for export
        export = input("\nExport to CSV? (y/n) [n]: ").strip().lower()
        if export == 'y':
            filename = input("Filename [diet_plan.csv]: ").strip()
            filename = filename if filename else "diet_plan.csv"
            export_diet_to_csv(best_individual.diet, filename)
    
    # Close database
    db.close()
    
    print("\n" + "="*60)
    print("Thank you for using Diet Optimizer! 🥗")
    print("="*60)


def run_gui():
    """Run graphical user interface"""
    print_header()
    print("Starting GUI application...")
    
    try:
        from gui.app import DietOptimizerGUI
        app = DietOptimizerGUI()
        app.run()
    except ImportError as e:
        print(f"Error: Could not start GUI - {e}")
        print("Make sure tkinter is installed.")
        sys.exit(1)


def run_tests():
    """Run unit tests"""
    print_header()
    print("Running unit tests...\n")
    
    from tests.test_optimizer import run_tests as execute_tests
    result = execute_tests()
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
    
    return result.wasSuccessful()


def demo_mode():
    """Run a quick demonstration"""
    print_header()
    print("🎬 DEMO MODE")
    print("="*60)
    print("Running quick optimization with default settings...\n")
    
    # Quick optimization
    diet, analysis = optimize_diet(
        population_size=50,
        num_generations=100,
        verbose=True
    )
    
    if diet:
        result_text = format_diet_plan(diet, analysis)
        print(result_text)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Diet Optimizer using Genetic Algorithm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py           Run command line interface
  python main.py --gui     Run graphical interface
  python main.py --test    Run unit tests
  python main.py --demo    Run quick demonstration
        """
    )
    
    parser.add_argument("--gui", action="store_true", 
                       help="Run with graphical interface")
    parser.add_argument("--test", action="store_true",
                       help="Run unit tests")
    parser.add_argument("--demo", action="store_true",
                       help="Run quick demonstration")
    parser.add_argument("--foods", action="store_true",
                       help="Display food database")
    
    args = parser.parse_args()
    
    if args.gui:
        run_gui()
    elif args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    elif args.demo:
        demo_mode()
    elif args.foods:
        print_food_database()
    else:
        run_command_line()


if __name__ == "__main__":
    main()
