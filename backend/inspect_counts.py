import sqlite3
import os

db_path = os.path.join('instance', 'quiz_app.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    for table in tables:
        if table != 'sqlite_sequence':
            cursor.execute(f"SELECT count(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")
            
            # Print a few sample rows for debugging if table is not empty
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 2")
                print("  Samples:", cursor.fetchall())
    conn.close()
else:
    print("Database path does not exist.")
