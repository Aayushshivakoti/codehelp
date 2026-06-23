import unittest
import json
import os
import sys

# Add backend directory to sys.path so we can import app and models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Subject

class QuizAppTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['JWT_SECRET_KEY'] = 'test-secret'
        
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        self.client = app.test_client()
        
        # Seed test admin and user
        import bcrypt
        self.admin_password = 'adminpassword'
        self.admin_hash = bcrypt.hashpw(self.admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.admin = User(username='testadmin', email='admin@test.com', password_hash=self.admin_hash, role='admin')
        
        self.user_password = 'userpassword'
        self.user_hash = bcrypt.hashpw(self.user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.user = User(username='testuser', email='user@test.com', password_hash=self.user_hash, role='user')
        
        db.session.add(self.admin)
        db.session.add(self.user)
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_register_user(self):
        # Test registering a new user
        response = self.client.post('/api/register', json={
            'username': 'newuser',
            'email': 'new@user.com',
            'password': 'newpassword',
            'gender': 'Male'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User created successfully')
        
    def test_login_user(self):
        # Test valid login
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'userpassword'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertEqual(data['user']['username'], 'testuser')
        
        # Test invalid login
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        
    def test_get_subjects_auth_required(self):
        # Test accessing protected endpoint without token
        response = self.client.get('/api/subjects')
        self.assertEqual(response.status_code, 401)
        
        # Test accessing with token
        login_response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'userpassword'
        })
        token = json.loads(login_response.data)['access_token']
        
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/subjects', headers=headers)
        self.assertEqual(response.status_code, 200)
        
    def test_admin_route_authorization(self):
        # Log in as normal user
        login_response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'userpassword'
        })
        token = json.loads(login_response.data)['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Attempt to access admin endpoint
        response = self.client.get('/api/admin/users', headers=headers)
        self.assertEqual(response.status_code, 403)
        
        # Log in as admin user
        admin_login_response = self.client.post('/api/login', json={
            'username': 'testadmin',
            'password': 'adminpassword'
        })
        admin_token = json.loads(admin_login_response.data)['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Access admin endpoint
        response = self.client.get('/api/admin/users', headers=admin_headers)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
