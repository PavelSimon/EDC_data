from app import create_app, db
from app.models import EDCData
from datetime import datetime
import sqlite3

def test_database():
    app = create_app()
    with app.app_context():
        try:
            # Test database connection
            print("Testing database connection...")
            db.engine.connect()
            print("✓ Database connection successful")
            
            # Get all tables in the database
            print("\nListing all tables in the database:")
            conn = sqlite3.connect('okte_data.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                print(f"\nTable: {table_name}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"Total records: {count}")
                
                # Get sample records
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                columns = [description[0] for description in cursor.description]
                print("\nColumns:", columns)
                
                print("\nSample records:")
                for row in cursor.fetchall():
                    print(dict(zip(columns, row)))
                print("-" * 50)
            
            conn.close()
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_database() 