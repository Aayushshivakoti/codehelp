#!/usr/bin/env python3
"""
Database Migration Script
Migrates existing quiz_app.db to new schema with subjects and chapters
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'instance', 'quiz_app.db')
    
    if not os.path.exists(db_path):
        print("No existing database found. Will create new one.")
        return
    
    print("Starting database migration...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is None:
            print("Users table does not exist. Skipping migration since database is new.")
            return
            
        # Check if subjects table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subjects'")
        subjects_exists = cursor.fetchone() is not None
        
        # Check if chapters table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chapters'")
        chapters_exists = cursor.fetchone() is not None
        
        # Check if quizzes table has chapter_id column
        cursor.execute("PRAGMA table_info(quizzes)")
        columns = [column[1] for column in cursor.fetchall()]
        has_chapter_id = 'chapter_id' in columns
        
        print(f"Subjects table exists: {subjects_exists}")
        print(f"Chapters table exists: {chapters_exists}")
        print(f"Quizzes has chapter_id: {has_chapter_id}")
        
        # Create subjects table if it doesn't exist
        if not subjects_exists:
            print("Creating subjects table...")
            cursor.execute('''
                CREATE TABLE subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL UNIQUE,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # Insert default subject
            cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
            admin_user = cursor.fetchone()
            admin_id = admin_user[0] if admin_user else 1
            
            cursor.execute('''
                INSERT INTO subjects (name, description, created_by)
                VALUES ('General Knowledge', 'Default subject for existing quizzes', ?)
            ''', (admin_id,))
            
            print("Created subjects table with default subject")
        
        # Create chapters table if it doesn't exist
        if not chapters_exists:
            print("Creating chapters table...")
            cursor.execute('''
                CREATE TABLE chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    theory TEXT,
                    subject_id INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_id) REFERENCES subjects (id),
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # Insert default chapter
            cursor.execute("SELECT id FROM subjects LIMIT 1")
            subject_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
            admin_user = cursor.fetchone()
            admin_id = admin_user[0] if admin_user else 1
            
            cursor.execute('''
                INSERT INTO chapters (name, description, subject_id, created_by)
                VALUES ('General', 'Default chapter for existing quizzes', ?, ?)
            ''', (subject_id, admin_id))
            
            print("Created chapters table with default chapter")
        else:
            # Check if theory column exists
            cursor.execute("PRAGMA table_info(chapters)")
            chap_columns = [column[1] for column in cursor.fetchall()]
            if 'theory' not in chap_columns:
                print("Adding theory column to chapters table...")
                cursor.execute("ALTER TABLE chapters ADD COLUMN theory TEXT")
        
        # Add chapter_id to quizzes table if it doesn't exist
        if not has_chapter_id:
            print("Adding chapter_id to quizzes table...")
            
            # Get the default chapter ID
            cursor.execute("SELECT id FROM chapters LIMIT 1")
            chapter_result = cursor.fetchone()
            
            if not chapter_result:
                # Create default chapter if none exists
                cursor.execute("SELECT id FROM subjects LIMIT 1")
                subject_result = cursor.fetchone()
                
                if not subject_result:
                    # Create default subject if none exists
                    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
                    admin_user = cursor.fetchone()
                    admin_id = admin_user[0] if admin_user else 1
                    
                    cursor.execute('''
                        INSERT INTO subjects (name, description, created_by)
                        VALUES ('General Knowledge', 'Default subject for existing quizzes', ?)
                    ''', (admin_id,))
                    subject_id = cursor.lastrowid
                else:
                    subject_id = subject_result[0]
                
                cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
                admin_user = cursor.fetchone()
                admin_id = admin_user[0] if admin_user else 1
                
                cursor.execute('''
                    INSERT INTO chapters (name, description, subject_id, created_by)
                    VALUES ('General', 'Default chapter for existing quizzes', ?, ?)
                ''', (subject_id, admin_id))
                chapter_id = cursor.lastrowid
            else:
                chapter_id = chapter_result[0]
            
            # Create new quizzes table with chapter_id
            cursor.execute('''
                CREATE TABLE quizzes_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    chapter_id INTEGER NOT NULL,
                    time_limit INTEGER DEFAULT 30,
                    is_active BOOLEAN DEFAULT 1,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chapter_id) REFERENCES chapters (id),
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # Copy data from old table to new table
            cursor.execute(f'''
                INSERT INTO quizzes_new (id, title, description, chapter_id, time_limit, is_active, created_by, created_at)
                SELECT id, title, description, {chapter_id}, time_limit, is_active, created_by, created_at
                FROM quizzes
            ''')
            
            # Drop old table and rename new table
            cursor.execute('DROP TABLE quizzes')
            cursor.execute('ALTER TABLE quizzes_new RENAME TO quizzes')
            
            print(f"Updated quizzes table with chapter_id (default: {chapter_id})")
        
        # Check and create challenge_templates table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='challenge_templates'")
        templates_exists = cursor.fetchone() is not None
        if not templates_exists:
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
            print("Created challenge_templates table")
        
        # Check and migrate users table columns (gender and profile_pic)
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]
        if 'gender' not in user_columns:
            print("Adding gender column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN gender VARCHAR(50)")
        if 'profile_pic' not in user_columns:
            print("Adding profile_pic column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN profile_pic VARCHAR(255)")
        
        # Check and migrate quizzes table columns (questions_per_attempt)
        cursor.execute("PRAGMA table_info(quizzes)")
        quizzes_columns = [column[1] for column in cursor.fetchall()]
        if 'questions_per_attempt' not in quizzes_columns:
            print("Adding questions_per_attempt column to quizzes table...")
            cursor.execute("ALTER TABLE quizzes ADD COLUMN questions_per_attempt INTEGER DEFAULT 8")

        # Check and migrate quiz_attempts table columns (question_ids)
        cursor.execute("PRAGMA table_info(quiz_attempts)")
        quiz_attempts_columns = [column[1] for column in cursor.fetchall()]
        if 'question_ids' not in quiz_attempts_columns:
            print("Adding question_ids column to quiz_attempts table...")
            cursor.execute("ALTER TABLE quiz_attempts ADD COLUMN question_ids TEXT")
        
        # Check and create tournaments table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tournaments'")
        tournaments_exists = cursor.fetchone() is not None
        if not tournaments_exists:
            print("Creating tournaments table...")
            cursor.execute('''
                CREATE TABLE tournaments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    starts_at DATETIME NOT NULL,
                    ends_at DATETIME NOT NULL,
                    status VARCHAR(50),
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            print("Created tournaments table")
        else:
            # Check and migrate tournaments table columns (status)
            cursor.execute("PRAGMA table_info(tournaments)")
            tournaments_columns = [column[1] for column in cursor.fetchall()]
            if 'status' not in tournaments_columns:
                print("Adding status column to tournaments table...")
                cursor.execute("ALTER TABLE tournaments ADD COLUMN status VARCHAR(50)")

        # Check and create tournament_participants table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tournament_participants'")
        participants_exists = cursor.fetchone() is not None
        if not participants_exists:
            print("Creating tournament_participants table...")
            cursor.execute('''
                CREATE TABLE tournament_participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tournament_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    score INTEGER DEFAULT 0,
                    time_taken INTEGER DEFAULT 0,
                    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed BOOLEAN DEFAULT 0,
                    completed_at DATETIME,
                    FOREIGN KEY (tournament_id) REFERENCES tournaments (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            print("Created tournament_participants table")
        else:
            # Check and migrate columns
            cursor.execute("PRAGMA table_info(tournament_participants)")
            tp_columns = [column[1] for column in cursor.fetchall()]
            if 'completed' not in tp_columns:
                print("Adding completed column to tournament_participants table...")
                cursor.execute("ALTER TABLE tournament_participants ADD COLUMN completed BOOLEAN DEFAULT 0")
            if 'completed_at' not in tp_columns:
                print("Adding completed_at column to tournament_participants table...")
                cursor.execute("ALTER TABLE tournament_participants ADD COLUMN completed_at DATETIME")

        # Check and create tournament_questions table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tournament_questions'")
        tour_q_exists = cursor.fetchone() is not None
        if not tour_q_exists:
            print("Creating tournament_questions table...")
            cursor.execute('''
                CREATE TABLE tournament_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tournament_id INTEGER NOT NULL,
                    question_type VARCHAR(20) NOT NULL,
                    challenge_id INTEGER,
                    question_id INTEGER,
                    FOREIGN KEY (tournament_id) REFERENCES tournaments (id) ON DELETE CASCADE,
                    FOREIGN KEY (challenge_id) REFERENCES code_challenges (id) ON DELETE CASCADE,
                    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
                )
            ''')
            print("Created tournament_questions table")

        # Check and create tournament_submissions table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tournament_submissions'")
        tour_sub_exists = cursor.fetchone() is not None
        if not tour_sub_exists:
            print("Creating tournament_submissions table...")
            cursor.execute('''
                CREATE TABLE tournament_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tournament_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    question_type VARCHAR(20) NOT NULL,
                    question_id INTEGER,
                    challenge_id INTEGER,
                    selected_answer VARCHAR(1),
                    is_correct BOOLEAN DEFAULT 0,
                    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tournament_id) REFERENCES tournaments (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
                    FOREIGN KEY (challenge_id) REFERENCES code_challenges (id) ON DELETE CASCADE
                )
            ''')
            print("Created tournament_submissions table")

        # Check and create ai_hint_logs table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_hint_logs'")
        hint_logs_exists = cursor.fetchone() is not None
        if not hint_logs_exists:
            print("Creating ai_hint_logs table...")
            cursor.execute('''
                CREATE TABLE ai_hint_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    challenge_id INTEGER NOT NULL,
                    submitted_code TEXT,
                    hint_response TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (challenge_id) REFERENCES code_challenges (id) ON DELETE CASCADE
                )
            ''')
            print("Created ai_hint_logs table")

        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()