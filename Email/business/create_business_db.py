import sqlite3
import json
import os

DB_PATH = 'Email/business.db'
BUSINESS_INFO_JSON = 'Email/business_info.json'

def create_tables():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create businesses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS businesses (
                business_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                device TEXT
            )
        ''')

        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT NOT NULL,
                email TEXT NOT NULL,
                sent BOOLEAN,
                date TEXT,
                FOREIGN KEY (business_id) REFERENCES businesses (business_id)
            )
        ''')
        conn.commit()
        print("Tables 'businesses' and 'customers' created successfully in business.db")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

def insert_initial_data():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if not os.path.exists(BUSINESS_INFO_JSON):
            print(f"Error: {BUSINESS_INFO_JSON} not found. Skipping data insertion.")
            return

        with open(BUSINESS_INFO_JSON, 'r', encoding='utf-8') as f:
            business_data = json.load(f)

        for business_id, info in business_data.items():
            # Insert into businesses table
            cursor.execute("INSERT OR IGNORE INTO businesses (business_id, name, device) VALUES (?, ?, ?)",
                           (business_id, info['name'], info['device']))

            # Insert into customers table
            for customer in info['customers']:
                sent_status = 1 if customer.get('sent') else 0 # SQLite stores booleans as 0 or 1
                cursor.execute("INSERT INTO customers (business_id, email, sent, date) VALUES (?, ?, ?, ?)",
                               (business_id, customer['email'], sent_status, customer.get('date')))
        conn.commit()
        print("Initial data inserted successfully from business_info.json")

    except sqlite3.Error as e:
        print(f"SQLite error during data insertion: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_tables()
    insert_initial_data()
