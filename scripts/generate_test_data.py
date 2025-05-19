#!/usr/bin/env python3
"""
Generate comprehensive test data for MCP Data Assistant.
Creates realistic data for sales.db and people.csv.
"""

import sqlite3
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
import json

# French cities for realistic data
CITIES = [
    "Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg",
    "Montpellier", "Bordeaux", "Lille", "Rennes", "Reims", "Le Havre", "Saint-Étienne",
    "Toulon", "Grenoble", "Dijon", "Angers", "Nîmes", "Villeurbanne", "Clermont-Ferrand",
    "Le Mans", "Aix-en-Provence", "Brest", "Tours", "Amiens", "Limoges", "Annecy",
    "Perpignan", "Boulogne-Billancourt", "Metz", "Besançon", "Orléans", "Rouen",
    "Nancy", "Caen", "Poitiers", "Versailles", "Avignon", "Dunkerque"
]

# Departments for employees
DEPARTMENTS = [
    "Sales", "Marketing", "Engineering", "Finance", "HR", "Operations",
    "Legal", "IT", "Customer Service", "R&D", "Logistics", "Production",
    "Quality Assurance", "Business Development", "Administration", "Procurement"
]

# Products for sales data
PRODUCTS = [
    "Widget A", "Widget B", "Widget C", "Widget Pro", "Widget Lite",
    "Gizmo", "Gizmo Plus", "Gizmo Pro", "Gizmo Enterprise",
    "Gadget X", "Gadget Y", "Gadget Z", "Gadget Ultra",
    "Tool Basic", "Tool Advanced", "Tool Professional",
    "Service Bronze", "Service Silver", "Service Gold", "Service Platinum"
]

# French first names
FIRST_NAMES = [
    "Jean", "Marie", "Pierre", "Michel", "Françoise", "Nicole", "Sophie", "Laurent",
    "Patrick", "Catherine", "Jacques", "Monique", "Philippe", "Isabelle", "Alain",
    "Nathalie", "Bernard", "Sylvie", "Daniel", "Christine", "Robert", "Valérie",
    "Claude", "Sandrine", "Marc", "Stéphanie", "François", "Martine", "Eric",
    "Dominique", "Thierry", "Brigitte", "Nicolas", "Véronique", "Vincent", "Anne",
    "Thomas", "Caroline", "Julien", "Aurélie", "Maxime", "Claire", "Alexandre",
    "Julie", "Mathieu", "Emma", "Antoine", "Léa", "Lucas", "Manon"
]

# French last names
LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand",
    "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David",
    "Bertrand", "Roux", "Vincent", "Fournier", "Morel", "Girard", "Andre", "Lefevre",
    "Mercier", "Dupont", "Lambert", "Bonnet", "Francois", "Martinez", "Legrand",
    "Garnier", "Faure", "Rousseau", "Blanc", "Guerin", "Muller", "Henry", "Roussel",
    "Nicolas", "Perrin", "Morin", "Mathieu", "Clement", "Gauthier", "Dumont", "Lopez",
    "Fontaine", "Chevalier", "Robin"
]

def generate_people_csv(num_people=500):
    """Generate people.csv with realistic employee data."""
    people_file = Path(__file__).parent.parent / "data" / "people.csv"
    people_file.parent.mkdir(exist_ok=True)
    
    people = []
    hire_start_date = datetime(2010, 1, 1)
    hire_end_date = datetime(2024, 12, 31)
    
    for i in range(1, num_people + 1):
        person = {
            "id": i,
            "first_name": random.choice(FIRST_NAMES),
            "last_name": random.choice(LAST_NAMES),
            "age": random.randint(22, 65),
            "city": random.choice(CITIES),
            "department": random.choice(DEPARTMENTS),
            "salary": round(random.normalvariate(50000, 15000), 2),
            "hire_date": (hire_start_date + timedelta(
                days=random.randint(0, (hire_end_date - hire_start_date).days)
            )).strftime("%Y-%m-%d")
        }
        
        # Ensure salary is reasonable
        if person["salary"] < 25000:
            person["salary"] = 25000
        elif person["salary"] > 120000:
            person["salary"] = 120000
            
        people.append(person)
    
    # Write to CSV
    with open(people_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["id", "first_name", "last_name", "age", "city", "department", "salary", "hire_date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(people)
    
    print(f"Generated {num_people} people records in {people_file}")
    return people

def generate_sales_db(people_data=None):
    """Generate sales.db with comprehensive sales data for 2024."""
    db_file = Path(__file__).parent.parent / "data" / "sales.db"
    db_file.parent.mkdir(exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    # Drop existing table and create new one with all columns
    cursor.execute('DROP TABLE IF EXISTS orders')
    
    # Create table with all required columns
    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            customer_id INTEGER,
            customer_name TEXT,
            region TEXT,
            payment_method TEXT,
            order_status TEXT
        )
    ''')
    
    # Generate sales data for each month of 2024
    order_id = 1
    start_date = datetime(2024, 1, 1)
    
    # Create seasonal patterns
    seasonal_multipliers = {
        1: 0.9,   # January - post-holiday slump
        2: 0.85,  # February
        3: 1.0,   # March
        4: 1.05,  # April
        5: 1.1,   # May
        6: 1.15,  # June
        7: 1.2,   # July - summer peak
        8: 1.2,   # August
        9: 1.1,   # September
        10: 1.15, # October
        11: 1.3,  # November - Black Friday
        12: 1.4   # December - Christmas
    }
    
    # Product price ranges
    product_prices = {
        "Widget A": (150, 200),
        "Widget B": (120, 180),
        "Widget C": (80, 140),
        "Widget Pro": (300, 450),
        "Widget Lite": (50, 80),
        "Gizmo": (10, 20),
        "Gizmo Plus": (25, 40),
        "Gizmo Pro": (45, 70),
        "Gizmo Enterprise": (100, 150),
        "Gadget X": (60, 90),
        "Gadget Y": (70, 100),
        "Gadget Z": (80, 120),
        "Gadget Ultra": (200, 300),
        "Tool Basic": (30, 50),
        "Tool Advanced": (60, 90),
        "Tool Professional": (100, 150),
        "Service Bronze": (99, 99),
        "Service Silver": (199, 199),
        "Service Gold": (299, 299),
        "Service Platinum": (499, 499)
    }
    
    payment_methods = ["Credit Card", "PayPal", "Bank Transfer", "Cash", "Check", "Cryptocurrency"]
    order_statuses = ["Completed", "Pending", "Shipped", "Processing", "Cancelled"]
    regions = ["North", "South", "East", "West", "Central", "International"]
    
    # Generate orders for each day of 2024
    for month in range(1, 13):
        seasonal_factor = seasonal_multipliers[month]
        days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
        
        for day in range(1, days_in_month + 1):
            current_date = datetime(2024, month, day)
            
            # Variable number of orders per day (more on weekends and holidays)
            is_weekend = current_date.weekday() >= 5
            base_orders = 15 if is_weekend else 10
            
            # Special days with more orders
            is_special_day = (
                (month == 12 and day in [24, 25, 26]) or  # Christmas
                (month == 11 and day in [24, 25, 26, 27]) or  # Black Friday weekend
                (month == 7 and day in [14, 15]) or  # Summer sale
                (month == 1 and day == 1)  # New Year
            )
            
            if is_special_day:
                base_orders *= 2
            
            num_orders = int(random.randint(base_orders - 3, base_orders + 3) * seasonal_factor)
            
            for _ in range(num_orders):
                product = random.choice(PRODUCTS)
                price_range = product_prices[product]
                base_amount = random.uniform(price_range[0], price_range[1])
                
                # Add quantity multiplier
                quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
                amount = round(base_amount * quantity, 2)
                
                # Customer data
                if people_data and random.random() < 0.3:  # 30% chance to link to employee
                    person = random.choice(people_data)
                    customer_id = person["id"]
                    customer_name = f"{person['first_name']} {person['last_name']}"
                else:
                    customer_id = random.randint(1000, 9999)
                    customer_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
                
                order = (
                    current_date.strftime("%Y-%m-%d"),
                    product,
                    amount,
                    customer_id,
                    customer_name,
                    random.choice(regions),
                    random.choice(payment_methods),
                    random.choices(order_statuses, weights=[70, 10, 10, 5, 5])[0]
                )
                
                cursor.execute('''
                    INSERT INTO orders (date, product, amount, customer_id, customer_name, 
                                      region, payment_method, order_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', order)
                
                order_id += 1
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)')
    
    # Commit and close
    conn.commit()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM orders')
    total_orders = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(amount) FROM orders')
    total_sales = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT product) FROM orders')
    num_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT customer_id) FROM orders')
    num_customers = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Generated sales database with:")
    print(f"  - {total_orders} orders")
    print(f"  - {total_sales:.2f}€ in total sales")
    print(f"  - {num_products} different products")
    print(f"  - {num_customers} unique customers")
    print(f"  - Database saved to: {db_file}")

def generate_additional_data():
    """Generate additional data files for testing."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Generate customer segments data
    segments = {
        "segments": [
            {"name": "Premium", "count": 152, "avg_purchase": 450.32, "total_revenue": 68648.64},
            {"name": "Regular", "count": 543, "avg_purchase": 125.67, "total_revenue": 68238.81},
            {"name": "Occasional", "count": 821, "avg_purchase": 45.23, "total_revenue": 37133.83},
            {"name": "New", "count": 234, "avg_purchase": 78.90, "total_revenue": 18462.60}
        ],
        "total_customers": 1750,
        "analysis_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    with open(data_dir / "customer_segments.json", 'w') as f:
        json.dump(segments, f, indent=2)
    
    # Generate product categories
    categories = {
        "categories": [
            {"name": "Widgets", "products": 5, "total_sales": 234567.89, "growth": 15.3},
            {"name": "Gizmos", "products": 4, "total_sales": 123456.78, "growth": 8.7},
            {"name": "Gadgets", "products": 4, "total_sales": 189012.34, "growth": 12.1},
            {"name": "Tools", "products": 3, "total_sales": 98765.43, "growth": -2.5},
            {"name": "Services", "products": 4, "total_sales": 321098.76, "growth": 25.8}
        ]
    }
    
    with open(data_dir / "product_categories.json", 'w') as f:
        json.dump(categories, f, indent=2)
    
    print(f"Generated additional data files in {data_dir}")

def main():
    """Generate all test data."""
    print("Generating comprehensive test data for MCP Data Assistant...\n")
    
    # Generate people data
    people_data = generate_people_csv(num_people=500)
    print()
    
    # Generate sales data
    generate_sales_db(people_data)
    print()
    
    # Generate additional data files
    generate_additional_data()
    print()
    
    print("All test data generated successfully!")
    print("\nYou can now use the MCP Data Assistant to:")
    print("  - Analyze the sales database")
    print("  - Process the people CSV file")
    print("  - Generate comprehensive PDF reports")
    print("\nTry these example queries:")
    print("  - 'Show me total sales by month for 2024'")
    print("  - 'Analyze customer distribution by product category'")
    print("  - 'Create a comprehensive report for Q4 2024'")
    print("  - 'Show me top performing products by revenue'")
    print("  - 'Analyze employee demographics by department'")

if __name__ == "__main__":
    main()