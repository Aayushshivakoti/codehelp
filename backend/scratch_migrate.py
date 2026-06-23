import sqlite3
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'instance', 'quiz_app.db')

print(f"Connecting to database at {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if challenge_templates table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='challenge_templates'")
exists = cursor.fetchone() is not None

if not exists:
    print("Creating challenge_templates table...")
    cursor.execute('''
        CREATE TABLE challenge_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_id INTEGER NOT NULL,
            language VARCHAR(50) NOT NULL,
            template_code TEXT NOT NULL,
            FOREIGN KEY (challenge_id) REFERENCES code_challenges (id) ON DELETE CASCADE,
            UNIQUE(challenge_id, language)
        )
    ''')
    conn.commit()
    print("challenge_templates table created successfully!")
else:
    print("challenge_templates table already exists.")
conn.close()
