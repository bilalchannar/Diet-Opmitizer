"""
Diet Optimizer GUI
Interactive graphical user interface using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.genetic_algorithm import GeneticAlgorithm
from src.food_data import FOOD_DATABASE, DEFAULT_TARGETS, DEFAULT_BUDGET, get_all_categories
from src.fitness import FitnessCalculator
from src.utils import format_diet_plan, calculate_bmi, get_recommended_targets


class DietOptimizerGUI:
    """Main GUI application for Diet Optimizer"""
    
    def __init__(self):
        """Initialize the GUI"""
        self.root = tk.Tk()
        self.root.title("🥗 Diet Optimizer - Genetic Algorithm")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Variables
        self.is_running = False
        self.ga = None
        self.best_diet = None
        self.analysis = None
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Left panel - Settings
        left_frame = ttk.LabelFrame(main_frame, text="⚙️ Settings", padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Right panel - Results
        right_frame = ttk.LabelFrame(main_frame, text="📊 Results", padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # === Left Panel Contents ===
        
        # User Info Section
        user_frame = ttk.LabelFrame(left_frame, text="👤 User Information", padding="5")
        user_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Age
        ttk.Label(user_frame, text="Age:").grid(row=0, column=0, sticky="w", pady=2)
        self.age_var = tk.StringVar(value="25")
        ttk.Entry(user_frame, textvariable=self.age_var, width=10).grid(row=0, column=1, pady=2)
        
        # Weight
        ttk.Label(user_frame, text="Weight (kg):").grid(row=1, column=0, sticky="w", pady=2)
        self.weight_var = tk.StringVar(value="70")
        ttk.Entry(user_frame, textvariable=self.weight_var, width=10).grid(row=1, column=1, pady=2)
        
        # Height
        ttk.Label(user_frame, text="Height (cm):").grid(row=2, column=0, sticky="w", pady=2)
        self.height_var = tk.StringVar(value="170")
        ttk.Entry(user_frame, textvariable=self.height_var, width=10).grid(row=2, column=1, pady=2)
        
        # Gender
        ttk.Label(user_frame, text="Gender:").grid(row=3, column=0, sticky="w", pady=2)
        self.gender_var = tk.StringVar(value="male")
        gender_combo = ttk.Combobox(user_frame, textvariable=self.gender_var, 
                                    values=["male", "female"], width=8, state="readonly")
        gender_combo.grid(row=3, column=1, pady=2)
        
        # Activity Level
        ttk.Label(user_frame, text="Activity:").grid(row=4, column=0, sticky="w", pady=2)
        self.activity_var = tk.StringVar(value="moderate")
        activity_combo = ttk.Combobox(user_frame, textvariable=self.activity_var,
                                      values=["sedentary", "light", "moderate", "active", "very_active"],
                                      width=10, state="readonly")
        activity_combo.grid(row=4, column=1, pady=2)
        
        # Goal
        ttk.Label(user_frame, text="Goal:").grid(row=5, column=0, sticky="w", pady=2)
        self.goal_var = tk.StringVar(value="maintain")
        goal_combo = ttk.Combobox(user_frame, textvariable=self.goal_var,
                                  values=["lose", "maintain", "gain"],
                                  width=10, state="readonly")
        goal_combo.grid(row=5, column=1, pady=2)
        
        # Budget
        ttk.Label(user_frame, text="Budget ($):").grid(row=6, column=0, sticky="w", pady=2)
        self.budget_var = tk.StringVar(value="15")
        ttk.Entry(user_frame, textvariable=self.budget_var, width=10).grid(row=6, column=1, pady=2)
        
        # Calculate BMI button
        ttk.Button(user_frame, text="Calculate BMI", 
                  command=self.calculate_bmi).grid(row=7, column=0, columnspan=2, pady=5)
        
        self.bmi_label = ttk.Label(user_frame, text="BMI: --")
        self.bmi_label.grid(row=8, column=0, columnspan=2)
        
        # GA Parameters Section
        ga_frame = ttk.LabelFrame(left_frame, text="🧬 GA Parameters", padding="5")
        ga_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Population Size
        ttk.Label(ga_frame, text="Population:").grid(row=0, column=0, sticky="w", pady=2)
        self.pop_var = tk.StringVar(value="100")
        ttk.Entry(ga_frame, textvariable=self.pop_var, width=10).grid(row=0, column=1, pady=2)
        
        # Generations
        ttk.Label(ga_frame, text="Generations:").grid(row=1, column=0, sticky="w", pady=2)
        self.gen_var = tk.StringVar(value="200")
        ttk.Entry(ga_frame, textvariable=self.gen_var, width=10).grid(row=1, column=1, pady=2)
        
        # Crossover Rate
        ttk.Label(ga_frame, text="Crossover:").grid(row=2, column=0, sticky="w", pady=2)
        self.cross_var = tk.StringVar(value="0.8")
        ttk.Entry(ga_frame, textvariable=self.cross_var, width=10).grid(row=2, column=1, pady=2)
        
        # Mutation Rate
        ttk.Label(ga_frame, text="Mutation:").grid(row=3, column=0, sticky="w", pady=2)
        self.mut_var = tk.StringVar(value="0.15")
        ttk.Entry(ga_frame, textvariable=self.mut_var, width=10).grid(row=3, column=1, pady=2)
        
        # Nutritional Targets Section
        targets_frame = ttk.LabelFrame(left_frame, text="🎯 Nutritional Targets", padding="5")
        targets_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        self.target_vars = {}
        row = 0
        for nutrient, values in DEFAULT_TARGETS.items():
            ttk.Label(targets_frame, text=f"{nutrient.capitalize()}:").grid(row=row, column=0, sticky="w")
            
            min_var = tk.StringVar(value=str(values["min"]))
            max_var = tk.StringVar(value=str(values["max"]))
            
            ttk.Entry(targets_frame, textvariable=min_var, width=6).grid(row=row, column=1)
            ttk.Label(targets_frame, text="-").grid(row=row, column=2)
            ttk.Entry(targets_frame, textvariable=max_var, width=6).grid(row=row, column=3)
            
            self.target_vars[nutrient] = (min_var, max_var)
            row += 1
        
        ttk.Button(targets_frame, text="Auto-Calculate Targets",
                  command=self.auto_calculate_targets).grid(row=row, column=0, columnspan=4, pady=5)
        
        # Control Buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="🚀 Start Optimization", 
                                    command=self.start_optimization)
        self.start_btn.pack(fill="x", pady=2)
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹️ Stop", 
                                   command=self.stop_optimization, state="disabled")
        self.stop_btn.pack(fill="x", pady=2)
        
        ttk.Button(btn_frame, text="📊 Show Visualization",
                  command=self.show_visualization).pack(fill="x", pady=2)
        
        ttk.Button(btn_frame, text="💾 Export to CSV",
                  command=self.export_csv).pack(fill="x", pady=2)
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(left_frame, variable=self.progress_var, 
                                        maximum=100, mode='determinate')
        self.progress.grid(row=4, column=0, sticky="ew", pady=5)
        
        self.status_label = ttk.Label(left_frame, text="Ready")
        self.status_label.grid(row=5, column=0)
        
        # === Right Panel Contents ===
        
        # Notebook for tabs
        notebook = ttk.Notebook(right_frame)
        notebook.grid(row=0, column=0, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Results Tab
        results_tab = ttk.Frame(notebook, padding="5")
        notebook.add(results_tab, text="📋 Diet Plan")
        
        self.results_text = scrolledtext.ScrolledText(results_tab, wrap=tk.WORD, 
                                                       font=("Consolas", 10))
        self.results_text.pack(fill="both", expand=True)
        self.results_text.insert("1.0", "Click 'Start Optimization' to generate a diet plan.\n\n"
                                       "The genetic algorithm will evolve optimal meal combinations\n"
                                       "that meet your nutritional requirements while staying within budget.")
        
        # Progress Tab
        progress_tab = ttk.Frame(notebook, padding="5")
        notebook.add(progress_tab, text="📈 Progress")
        
        self.progress_text = scrolledtext.ScrolledText(progress_tab, wrap=tk.WORD,
                                                        font=("Consolas", 9))
        self.progress_text.pack(fill="both", expand=True)
        
        # Foods Tab
        foods_tab = ttk.Frame(notebook, padding="5")
        notebook.add(foods_tab, text="🍎 Food Database")
        
        # Foods treeview
        columns = ("name", "calories", "protein", "carbs", "fat", "fiber", "price", "category")
        self.foods_tree = ttk.Treeview(foods_tab, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.foods_tree.heading(col, text=col.capitalize())
            self.foods_tree.column(col, width=80)
        
        self.foods_tree.column("name", width=150)
        
        # Add scrollbar
        foods_scroll = ttk.Scrollbar(foods_tab, orient="vertical", command=self.foods_tree.yview)
        self.foods_tree.configure(yscrollcommand=foods_scroll.set)
        
        self.foods_tree.pack(side="left", fill="both", expand=True)
        foods_scroll.pack(side="right", fill="y")
        
        # Populate foods
        self.populate_foods_tree()
        
    def populate_foods_tree(self):
        """Populate the foods treeview"""
        for name, info in FOOD_DATABASE.items():
            self.foods_tree.insert("", "end", values=(
                name,
                info["calories"],
                info["protein"],
                info["carbs"],
                info["fat"],
                info["fiber"],
                f"${info['price']:.2f}",
                info["category"]
            ))
    
    def calculate_bmi(self):
        """Calculate and display BMI"""
        try:
            weight = float(self.weight_var.get())
            height = float(self.height_var.get())
            
            from src.utils import calculate_bmi
            bmi, category = calculate_bmi(weight, height)
            
            self.bmi_label.config(text=f"BMI: {bmi} ({category})")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid weight and height values.")
    
    def auto_calculate_targets(self):
        """Auto-calculate nutritional targets based on user info"""
        try:
            weight = float(self.weight_var.get())
            height = float(self.height_var.get())
            age = int(self.age_var.get())
            gender = self.gender_var.get()
            activity = self.activity_var.get()
            goal = self.goal_var.get()
            
            targets = get_recommended_targets(weight, height, age, gender, activity, goal)
            
            for nutrient, (min_var, max_var) in self.target_vars.items():
                if nutrient in targets:
                    min_var.set(str(int(targets[nutrient]["min"])))
                    max_var.set(str(int(targets[nutrient]["max"])))
            
            messagebox.showinfo("Success", "Nutritional targets calculated based on your profile!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid user information.")
    
    def get_targets(self):
        """Get current nutritional targets from UI"""
        targets = {}
        for nutrient, (min_var, max_var) in self.target_vars.items():
            try:
                targets[nutrient] = {
                    "min": float(min_var.get()),
                    "max": float(max_var.get()),
                    "weight": DEFAULT_TARGETS[nutrient]["weight"]
                }
            except ValueError:
                targets[nutrient] = DEFAULT_TARGETS[nutrient]
        return targets
    
    def update_progress(self, generation, stats, best_individual):
        """Callback for GA progress updates"""
        if not self.is_running:
            return
        
        total_gen = int(self.gen_var.get())
        progress = (generation / total_gen) * 100
        self.progress_var.set(progress)
        
        self.status_label.config(text=f"Generation {generation}/{total_gen}")
        
        # Update progress text
        self.progress_text.insert("end", 
            f"Gen {generation:4d}: Best={stats['best']:.2f}, Avg={stats['avg']:.2f}\n")
        self.progress_text.see("end")
        
        self.root.update_idletasks()
    
    def run_optimization(self):
        """Run the genetic algorithm (in separate thread)"""
        try:
            targets = self.get_targets()
            budget = float(self.budget_var.get())
            
            self.ga = GeneticAlgorithm(
                population_size=int(self.pop_var.get()),
                num_generations=int(self.gen_var.get()),
                crossover_rate=float(self.cross_var.get()),
                mutation_rate=float(self.mut_var.get()),
                targets=targets,
                budget=budget
            )
            
            self.ga.set_generation_callback(
                lambda g, s, b: self.root.after(0, self.update_progress, g, s, b)
            )
            
            self.ga.run(verbose=False)
            
            if self.is_running:
                self.best_diet, self.analysis = self.ga.get_best_solution()
                self.root.after(0, self.display_results)
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, self.optimization_complete)
    
    def start_optimization(self):
        """Start the optimization process"""
        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress_var.set(0)
        self.progress_text.delete("1.0", "end")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", "Optimizing diet plan...\n\n")
        
        # Run in separate thread
        thread = threading.Thread(target=self.run_optimization)
        thread.daemon = True
        thread.start()
    
    def stop_optimization(self):
        """Stop the optimization process"""
        self.is_running = False
        self.status_label.config(text="Stopped")
    
    def optimization_complete(self):
        """Called when optimization completes"""
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.progress_var.set(100)
        self.status_label.config(text="Complete!")
    
    def display_results(self):
        """Display optimization results"""
        if self.best_diet and self.analysis:
            result_text = format_diet_plan(self.best_diet.diet, self.analysis)
            self.results_text.delete("1.0", "end")
            self.results_text.insert("1.0", result_text)
    
    def show_visualization(self):
        """Show optimization visualization"""
        if self.ga and self.ga.best_fitness_history:
            try:
                from src.utils import visualize_optimization, visualize_nutrition
                visualize_optimization(self.ga.best_fitness_history, self.ga.avg_fitness_history)
                
                if self.analysis:
                    visualize_nutrition(self.analysis)
            except Exception as e:
                messagebox.showinfo("Info", f"Visualization not available: {e}")
        else:
            messagebox.showinfo("Info", "Run optimization first to see visualization.")
    
    def export_csv(self):
        """Export diet plan to CSV"""
        if self.best_diet:
            from tkinter import filedialog
            from src.utils import export_diet_to_csv
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfilename="diet_plan.csv"
            )
            
            if filename:
                export_diet_to_csv(self.best_diet.diet, filename)
                messagebox.showinfo("Success", f"Diet plan exported to {filename}")
        else:
            messagebox.showinfo("Info", "Run optimization first to export results.")
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point for GUI"""
    app = DietOptimizerGUI()
    app.run()


if __name__ == "__main__":
    main()
