import sqlite3
import pandas as pd

def check_database():
    try:
        # Connect to database
        print("Connecting to database...")
        conn = sqlite3.connect('okte_data.db')
        cursor = conn.cursor()
        
        # Get all tables
        print("\nListing all tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Total records: {count}")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("\nColumns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Get sample data
            if count > 0:
                print("\nSample data (first 5 rows):")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
        
        conn.close()
        print("\nDatabase check completed successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_database() 