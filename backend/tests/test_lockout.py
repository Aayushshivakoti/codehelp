import unittest
import json
import os
import sys
from datetime import datetime, timedelta

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Subject, Chapter, Quiz, Question, QuizAttempt, UserAnswer

class LockoutTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['JWT_SECRET_KEY'] = 'test-secret'
        
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        self.client = app.test_client()
        
        import bcrypt
        self.password = 'password'
        self.hash = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.user = User(username='student', email='student@test.com', password_hash=self.hash, role='user')
        self.admin = User(username='adminuser', email='admin@test.com', password_hash=self.hash, role='admin')
        
        db.session.add(self.user)
        db.session.add(self.admin)
        db.session.commit()
        
        # Create a test subject, chapter, and quiz
        self.subject = Subject(name='Test Subject', description='Desc', created_by=self.admin.id)
        db.session.add(self.subject)
        db.session.commit()
        
        self.chapter = Chapter(name='Test Chapter', description='Desc', subject_id=self.subject.id, created_by=self.admin.id)
        db.session.add(self.chapter)
        db.session.commit()
        
        self.quiz = Quiz(title='Test Quiz 1', description='Desc', chapter_id=self.chapter.id, time_limit=10, created_by=self.admin.id)
        self.quiz2 = Quiz(title='Test Quiz 2', description='Desc', chapter_id=self.chapter.id, time_limit=10, created_by=self.admin.id)
        db.session.add(self.quiz)
        db.session.add(self.quiz2)
        db.session.commit()
        
        # Add a question
        self.question = Question(quiz_id=self.quiz.id, question='Q1', option_a='A', option_b='B', option_c='C', option_d='D', correct_answer='A')
        db.session.add(self.question)
        db.session.commit()
        
        # Get tokens
        login_res = self.client.post('/api/login', json={'username': 'student', 'password': 'password'})
        self.token = json.loads(login_res.data)['access_token']
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_start_and_resume_and_lockout(self):
        # 1. Initially check lockout-status, should be unlocked
        res = self.client.get('/api/quizzes/lockout-status', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertFalse(data['is_locked'])
        self.assertIsNone(data['active_attempt'])

        # 2. Start a quiz
        res = self.client.post(f'/api/quizzes/{self.quiz.id}/start', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        attempt_id = data['attempt_id']
        self.assertFalse(data['resumed'])

        # 3. Check lockout-status, should show locked with active attempt details
        res = self.client.get('/api/quizzes/lockout-status', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['is_locked'])
        self.assertIsNotNone(data['active_attempt'])
        self.assertEqual(data['active_attempt']['quiz_id'], self.quiz.id)

        # 4. Resume the same quiz, should return success and resumed: True
        res = self.client.post(f'/api/quizzes/{self.quiz.id}/start', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['attempt_id'], attempt_id)
        self.assertTrue(data['resumed'])

        # 5. Try starting a DIFFERENT quiz, should force abandon the first and return 403
        res = self.client.post(f'/api/quizzes/{self.quiz2.id}/start', headers=self.headers)
        self.assertEqual(res.status_code, 403)
        data = json.loads(res.data)
        self.assertIn('abandoned', data['message'])

        # 6. Lockout status should now be locked, with NO active attempt (since it was abandoned)
        res = self.client.get('/api/quizzes/lockout-status', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['is_locked'])
        self.assertIsNone(data['active_attempt'])

    def test_explicit_abandon_quiz(self):
        # 1. Start a quiz
        res = self.client.post(f'/api/quizzes/{self.quiz.id}/start', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        attempt_id = data['attempt_id']

        # 2. Abandon the attempt
        res = self.client.post(f'/api/attempts/{attempt_id}/abandon', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('abandoned', data['message'])

        # 3. Check lockout-status, should show locked with no active attempt
        res = self.client.get('/api/quizzes/lockout-status', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['is_locked'])
        self.assertIsNone(data['active_attempt'])

        # 4. Starting any quiz should be blocked (403)
        res = self.client.post(f'/api/quizzes/{self.quiz.id}/start', headers=self.headers)
        self.assertEqual(res.status_code, 403)

if __name__ == '__main__':
    unittest.main()
