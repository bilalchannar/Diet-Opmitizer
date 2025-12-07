"""
Database Module
Handles SQLite database operations for the Diet Optimizer.
"""

import sqlite3
import os
from src.food_data import FOOD_DATABASE, DEFAULT_TARGETS


class DietDatabase:
    """SQLite database handler for diet optimizer"""
    
    def __init__(self, db_path="data/diet_optimizer.db"):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.populate_initial_data()
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"✓ Connected to database: {self.db_path}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")
    
    def create_tables(self):
        """Create necessary tables"""
        # Foods table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                carbs REAL NOT NULL,
                fat REAL NOT NULL,
                fiber REAL NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL,
                min_serving INTEGER DEFAULT 50,
                max_serving INTEGER DEFAULT 300
            )
        ''')
        
        # Nutritional targets table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutritional_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nutrient TEXT UNIQUE NOT NULL,
                min_value REAL NOT NULL,
                max_value REAL NOT NULL,
                weight REAL DEFAULT 1.0
            )
        ''')
        
        # User profiles table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                weight REAL,
                height REAL,
                activity_level TEXT,
                goal TEXT,
                daily_budget REAL DEFAULT 15.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Saved diet plans table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                plan_name TEXT,
                fitness_score REAL,
                total_cost REAL,
                total_calories REAL,
                total_protein REAL,
                total_carbs REAL,
                total_fat REAL,
                total_fiber REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES user_profiles(id)
            )
        ''')
        
        # Diet plan items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_plan_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                food_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                FOREIGN KEY (plan_id) REFERENCES diet_plans(id),
                FOREIGN KEY (food_id) REFERENCES foods(id)
            )
        ''')
        
        # Optimization history table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generation INTEGER NOT NULL,
                best_fitness REAL NOT NULL,
                avg_fitness REAL NOT NULL,
                worst_fitness REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("✓ Database tables created successfully")
    
    def populate_initial_data(self):
        """Populate database with initial food data"""
        # Check if foods table is empty
        self.cursor.execute("SELECT COUNT(*) FROM foods")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            # Insert food data
            for name, info in FOOD_DATABASE.items():
                self.cursor.execute('''
                    INSERT INTO foods (name, calories, protein, carbs, fat, fiber, 
                                      price, category, min_serving, max_serving)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, info["calories"], info["protein"], info["carbs"],
                      info["fat"], info["fiber"], info["price"], info["category"],
                      info["min_serving"], info["max_serving"]))
            
            # Insert default nutritional targets
            for nutrient, values in DEFAULT_TARGETS.items():
                self.cursor.execute('''
                    INSERT OR IGNORE INTO nutritional_targets (nutrient, min_value, max_value, weight)
                    VALUES (?, ?, ?, ?)
                ''', (nutrient, values["min"], values["max"], values["weight"]))
            
            self.conn.commit()
            print(f"✓ Populated database with {len(FOOD_DATABASE)} food items")
    
    def get_all_foods(self):
        """Retrieve all foods from database"""
        self.cursor.execute("SELECT * FROM foods")
        columns = [description[0] for description in self.cursor.description]
        foods = []
        for row in self.cursor.fetchall():
            foods.append(dict(zip(columns, row)))
        return foods
    
    def get_food_by_name(self, name):
        """Get food item by name"""
        self.cursor.execute("SELECT * FROM foods WHERE name = ?", (name,))
        row = self.cursor.fetchone()
        if row:
            columns = [description[0] for description in self.cursor.description]
            return dict(zip(columns, row))
        return None
    
    def get_foods_by_category(self, category):
        """Get foods by category"""
        self.cursor.execute("SELECT * FROM foods WHERE category = ?", (category,))
        columns = [description[0] for description in self.cursor.description]
        foods = []
        for row in self.cursor.fetchall():
            foods.append(dict(zip(columns, row)))
        return foods
    
    def get_nutritional_targets(self):
        """Get nutritional targets"""
        self.cursor.execute("SELECT * FROM nutritional_targets")
        targets = {}
        for row in self.cursor.fetchall():
            targets[row[1]] = {
                "min": row[2],
                "max": row[3],
                "weight": row[4]
            }
        return targets
    
    def update_nutritional_target(self, nutrient, min_val, max_val, weight=1.0):
        """Update nutritional target"""
        self.cursor.execute('''
            UPDATE nutritional_targets 
            SET min_value = ?, max_value = ?, weight = ?
            WHERE nutrient = ?
        ''', (min_val, max_val, weight, nutrient))
        self.conn.commit()
    
    def save_diet_plan(self, plan_data, food_items, profile_id=None, plan_name="Optimized Diet"):
        """Save a diet plan to database"""
        self.cursor.execute('''
            INSERT INTO diet_plans (profile_id, plan_name, fitness_score, total_cost,
                                   total_calories, total_protein, total_carbs, 
                                   total_fat, total_fiber)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (profile_id, plan_name, plan_data.get("fitness", 0),
              plan_data.get("total_cost", 0), plan_data.get("calories", 0),
              plan_data.get("protein", 0), plan_data.get("carbs", 0),
              plan_data.get("fat", 0), plan_data.get("fiber", 0)))
        
        plan_id = self.cursor.lastrowid
        
        # Save diet plan items
        for food_name, quantity in food_items:
            food = self.get_food_by_name(food_name)
            if food:
                self.cursor.execute('''
                    INSERT INTO diet_plan_items (plan_id, food_id, quantity)
                    VALUES (?, ?, ?)
                ''', (plan_id, food["id"], quantity))
        
        self.conn.commit()
        return plan_id
    
    def get_saved_plans(self, limit=10):
        """Get saved diet plans"""
        self.cursor.execute('''
            SELECT * FROM diet_plans ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        columns = [description[0] for description in self.cursor.description]
        plans = []
        for row in self.cursor.fetchall():
            plans.append(dict(zip(columns, row)))
        return plans
    
    def save_optimization_history(self, generation, best_fitness, avg_fitness, worst_fitness):
        """Save optimization history for analysis"""
        self.cursor.execute('''
            INSERT INTO optimization_history (generation, best_fitness, avg_fitness, worst_fitness)
            VALUES (?, ?, ?, ?)
        ''', (generation, best_fitness, avg_fitness, worst_fitness))
        self.conn.commit()
    
    def clear_optimization_history(self):
        """Clear optimization history"""
        self.cursor.execute("DELETE FROM optimization_history")
        self.conn.commit()
    
    def get_optimization_history(self):
        """Get optimization history"""
        self.cursor.execute("SELECT * FROM optimization_history ORDER BY generation")
        columns = [description[0] for description in self.cursor.description]
        history = []
        for row in self.cursor.fetchall():
            history.append(dict(zip(columns, row)))
        return history
    
    def add_custom_food(self, name, calories, protein, carbs, fat, fiber, price, category):
        """Add a custom food item"""
        try:
            self.cursor.execute('''
                INSERT INTO foods (name, calories, protein, carbs, fat, fiber, price, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, calories, protein, carbs, fat, fiber, price, category))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Food already exists
    
    def delete_food(self, food_name):
        """Delete a food item"""
        self.cursor.execute("DELETE FROM foods WHERE name = ?", (food_name,))
        self.conn.commit()
        return self.cursor.rowcount > 0


# Singleton instance
_db_instance = None


def get_database():
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DietDatabase()
    return _db_instance
