from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
from datetime import datetime, timedelta
import bcrypt
import os
from functools import wraps
from dotenv import load_dotenv
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import joinedload
import requests

# Import models and database
from models import db, User, Subject, Chapter, Quiz, Question, QuizAttempt, UserAnswer, CodeChallenge, TestCase, ChallengeTemplate, CodeSubmission, UserEloHistory, Tournament, TournamentParticipant, AIHintLog, TournamentQuestion, TournamentSubmission

# Import the job scheduler
from jobs import job_scheduler, test_user_reminders, test_admin_report, test_weekly_cleanup, test_get_inactive_users, test_get_daily_stats

load_dotenv()

app = Flask(__name__)

# Database configuration
db_url = os.getenv('DATABASE_URL')
if not db_url:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(BASE_DIR, 'instance', 'quiz_app.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_url = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_ALGORITHM'] = 'HS256'

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# CORS configuration - Fix CORS error
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173", "http://127.0.0.1:5173",
            "http://localhost:5174", "http://127.0.0.1:5174"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'message': 'Invalid token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'message': 'Authorization token is required'}), 401

# Helper for checking and awarding badges
def check_badges(user):
    try:
        from models import Badge, UserBadge, QuizAttempt
        # 1. Get attempts count
        attempts_count = QuizAttempt.query.filter_by(user_id=user.id).filter(QuizAttempt.completed_at.isnot(None)).count()
        # 2. Perfect scores count
        perfect_attempts = QuizAttempt.query.filter_by(user_id=user.id).filter(QuizAttempt.completed_at.isnot(None)).all()
        perfect_count = sum(1 for a in perfect_attempts if a.total_questions > 0 and a.score == a.total_questions)
        
        all_badges = Badge.query.all()
        unlocked_badge_ids = {ub.badge_id for ub in user.badges}
        
        for badge in all_badges:
            if badge.id in unlocked_badge_ids:
                continue
            
            should_unlock = False
            if badge.criteria_type == 'attempts' and attempts_count >= badge.criteria_value:
                should_unlock = True
            elif badge.criteria_type == 'perfect_scores' and perfect_count >= badge.criteria_value:
                should_unlock = True
            elif badge.criteria_type == 'streak' and user.streak_count >= badge.criteria_value:
                should_unlock = True
            elif badge.criteria_type == 'xp' and user.xp >= badge.criteria_value:
                should_unlock = True
                
            if should_unlock:
                new_ub = UserBadge(user_id=user.id, badge_id=badge.id)
                db.session.add(new_ub)
        db.session.commit()
    except Exception as e:
        print(f"Badge check error: {str(e)}")

# Database initialization
def init_db():
    with app.app_context():
        # Run migration first if needed
        try:
            from migrate_db import migrate_database
            migrate_database()
        except Exception as e:
            print(f"Migration warning: {str(e)}")
        
        db.create_all()
        
        # Check if admin user exists
        admin_user = User.query.filter_by(role='admin').first()
        
        if not admin_user:
            admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            admin_user = User(
                username='admin',
                email='admin@quizapp.com',
                password_hash=admin_password.decode('utf-8'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Created default admin user: admin/admin123")
            
        # Check if student user exists
        student_user = User.query.filter_by(username='student').first()
        if not student_user:
            student_password = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
            student_user = User(
                username='student',
                email='student@quizapp.com',
                password_hash=student_password.decode('utf-8'),
                role='user'
            )
            db.session.add(student_user)
            db.session.commit()
            print("Created default student user: student/password123")
            
        # Seed default badges
        from models import Badge
        if Badge.query.count() == 0:
            badges = [
                Badge(name="First Steps", description="Complete your first quiz!", icon_url="first_steps.png", criteria_type="attempts", criteria_value=1),
                Badge(name="Chapter Champion", description="Achieve a perfect 100% score on any quiz!", icon_url="champion.png", criteria_type="perfect_scores", criteria_value=1),
                Badge(name="Streak Master", description="Maintain a 3-day daily learning streak!", icon_url="streak.png", criteria_type="streak", criteria_value=3),
                Badge(name="Knowledge Collector", description="Accumulate a total of 100 XP or more!", icon_url="collector.png", criteria_type="xp", criteria_value=100)
            ]
            for badge in badges:
                db.session.add(badge)
            db.session.commit()
            print("Default badges seeded successfully!")
        
        # Create sample data if tables are empty
        quiz_count = Quiz.query.count()
        
        if quiz_count == 0:
            # Create sample quizzes
            # Create sample subjects
            sample_subjects = [
                ('Mathematics', 'Mathematical concepts and problem solving'),
                ('Science', 'Physics, Chemistry, and Biology'),
                ('History', 'World history and historical events'),
                ('General Knowledge', 'Miscellaneous topics and current affairs')
            ]
            
            for name, description in sample_subjects:
                subject = Subject(
                    name=name,
                    description=description,
                    created_by=admin_user.id
                )
                db.session.add(subject)
            
            db.session.commit()
            
            # Create sample chapters
            math_subject = Subject.query.filter_by(name='Mathematics').first()
            if math_subject:
                chapter = Chapter(
                    name='Basic Arithmetic',
                    description='Addition, subtraction, multiplication, and division',
                    subject_id=math_subject.id,
                    created_by=admin_user.id
                )
                db.session.add(chapter)
                db.session.commit()
                
                # Create sample quiz
                quiz = Quiz(
                    title='Basic Math Quiz',
                    description='Test your basic arithmetic skills',
                    chapter_id=chapter.id,
                    time_limit=20,
                    created_by=admin_user.id
                )
                db.session.add(quiz)
                db.session.commit()
                
                # Add sample questions with hints and explanations
                sample_questions = [
                    ('What is 5 + 3?', '6', '7', '8', '9', 'C', 'Count 3 integers past 5.', '5 + 3 = 8.'),
                    ('What is 12 - 4?', '6', '7', '8', '9', 'C', '12 minus 2 is 10. Subtract 2 more.', '12 - 4 = 8.'),
                    ('What is 6 × 7?', '40', '41', '42', '43', 'C', 'Basic multiplication table of 6.', '6 × 7 = 42.'),
                    ('What is 24 ÷ 6?', '3', '4', '5', '6', 'B', 'What number times 6 equals 24?', '24 ÷ 6 = 4.'),
                    ('What is 15 + 25?', '35', '40', '45', '50', 'B', 'Add tens (10+20) and then add units (5+5).', '15 + 25 = 40.')
                ]
                
                for question_text, opt_a, opt_b, opt_c, opt_d, correct, hint, explanation in sample_questions:
                    question = Question(
                        quiz_id=quiz.id,
                        question=question_text,
                        option_a=opt_a,
                        option_b=opt_b,
                        option_c=opt_c,
                        option_d=opt_d,
                        correct_answer=correct,
                        hint=hint,
                        explanation=explanation
                    )
                    db.session.add(question)
                
                db.session.commit()
                
                # Auto-seed programming subjects (Python, Java, PHP, C, C++) on new DB setup
                try:
                    print("Auto-seeding programming subjects (Python, Java, PHP, C, C++)...")
                    from seed_ai_content import seed_data
                    seed_data(app)
                except Exception as seed_err:
                    print(f"Auto-seeding of programming subjects failed: {str(seed_err)}")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # First check if we have a valid JWT token
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
            
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({'message': 'Invalid token identity'}), 401
                
            user = User.query.get(int(current_user_id))
            
            if not user or user.role != 'admin':
                return jsonify({'message': 'Admin access required'}), 403
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Admin auth error: {str(e)}")
            return jsonify({'message': 'Authentication error', 'error': str(e)}), 401
    return decorated_function

# Error handlers
@app.errorhandler(422)
def handle_unprocessable_entity(e):
    return jsonify({'message': 'Unprocessable entity', 'error': str(e)}), 422

@app.errorhandler(500)
def handle_internal_error(e):
    import traceback
    traceback.print_exc()
    return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

# Auth routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'message': 'All fields are required'}), 400
        
        # Check if user exists
        existing_user = User.query.filter(
            or_(User.username == username, User.email == email)
        ).first()
        
        if existing_user:
            return jsonify({'message': 'Username or email already exists'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash.decode('utf-8'),
            gender=data.get('gender')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500

# Subject routes
@app.route('/api/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    try:
        subjects = db.session.query(
            Subject.id,
            Subject.name,
            Subject.description,
            Subject.is_active,
            func.count(Chapter.id).label('chapter_count')
        ).outerjoin(Chapter).filter(
            Subject.is_active == True
        ).group_by(Subject.id).order_by(desc(Subject.created_at)).all()
        
        subject_list = []
        for subject in subjects:
            subject_list.append({
                'id': subject.id,
                'name': subject.name,
                'description': subject.description,
                'is_active': subject.is_active,
                'chapter_count': subject.chapter_count
            })
        
        return jsonify(subject_list), 200
        
    except Exception as e:
        print(f"Get subjects error: {str(e)}")
        return jsonify({'message': 'Failed to get subjects', 'error': str(e)}), 422

@app.route('/api/subjects', methods=['POST'])
@admin_required
def create_subject():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        name = data.get('name')
        description = data.get('description')
        current_user_id = int(get_jwt_identity())
        
        if not name:
            return jsonify({'message': 'Name is required'}), 400
        
        # Check if subject already exists
        existing_subject = Subject.query.filter_by(name=name).first()
        if existing_subject:
            return jsonify({'message': 'Subject with this name already exists'}), 400
        
        subject = Subject(
            name=name,
            description=description,
            created_by=current_user_id
        )
        
        db.session.add(subject)
        db.session.flush() # Populate subject.id
        
        # Auto-create the 4 sections as Chapter entries
        sections = [
            {'name': 'Theory', 'description': f'Theory study guide for {name}'},
            {'name': 'MCQ Part', 'description': f'Multiple Choice Quizzes for {name}'},
            {'name': 'Code Challenges', 'description': f'Coding exercises for {name}'},
            {'name': 'Daily Challenge', 'description': f'Daily practice challenge for {name}'}
        ]
        
        for sec in sections:
            chap = Chapter(
                subject_id=subject.id,
                name=sec['name'],
                description=sec['description'],
                theory='',
                created_by=current_user_id
            )
            db.session.add(chap)
            
        db.session.commit()
        
        return jsonify({'message': 'Subject created successfully', 'subject_id': subject.id}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Create subject error: {str(e)}")
        return jsonify({'message': 'Failed to create subject', 'error': str(e)}), 500

@app.route('/api/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'message': 'Subject not found'}), 404
            
        # Delete all associated data in correct order
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        for chapter in chapters:
            quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
            for quiz in quizzes:
                # Delete user answers for all questions in this quiz
                questions = Question.query.filter_by(quiz_id=quiz.id).all()
                for question in questions:
                    UserAnswer.query.filter_by(question_id=question.id).delete()
                
                # Delete all questions in this quiz
                Question.query.filter_by(quiz_id=quiz.id).delete()
                
                # Delete all quiz attempts for this quiz
                QuizAttempt.query.filter_by(quiz_id=quiz.id).delete()
                
                # Delete the quiz
                db.session.delete(quiz)
            
            # Delete the chapter
            db.session.delete(chapter)
        
        # Finally delete the subject
        db.session.delete(subject)
        db.session.commit()
        
        return jsonify({'message': 'Subject deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete subject error: {str(e)}")
        return jsonify({'message': 'Failed to delete subject', 'error': str(e)}), 500

@app.route('/api/subjects/<int:subject_id>/daily-challenge', methods=['GET'])
@jwt_required()
def get_subject_daily_challenge(subject_id):
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'message': 'Subject not found'}), 404
            
        # Look specifically for the chapter named 'Daily Challenge'
        daily_chap = Chapter.query.filter_by(subject_id=subject_id, name='Daily Challenge').first()
        if daily_chap:
            chapter_ids = [daily_chap.id]
        else:
            chapters = Chapter.query.filter_by(subject_id=subject_id, is_active=True).all()
            if not chapters:
                return jsonify({'message': 'No daily challenge available (no chapters)'}), 200
            chapter_ids = [c.id for c in chapters]
        
        quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids), Quiz.is_active==True).all()
        challenges = CodeChallenge.query.filter(CodeChallenge.chapter_id.in_(chapter_ids), CodeChallenge.is_active==True).all()
        
        items = []
        for q in quizzes:
            if q.questions:
                items.append({
                    'id': q.id,
                    'title': q.title,
                    'type': 'quiz',
                    'difficulty': 'Medium',
                    'description': q.description or 'Test your knowledge with this quiz.'
                })
        for c in challenges:
            items.append({
                'id': c.id,
                'title': c.title,
                'type': 'code',
                'difficulty': c.difficulty,
                'description': c.description or 'Solve this programming challenge.'
            })
            
        if not items:
            return jsonify({'message': 'No daily challenge available yet'}), 200
            
        # Select one item deterministically using today's date
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        index = sum(ord(char) for char in today_str) % len(items)
        selected_item = items[index]
        
        return jsonify(selected_item), 200
        
    except Exception as e:
        print(f"Daily challenge error: {str(e)}")
        return jsonify({'message': 'Failed to load daily challenge', 'error': str(e)}), 500

# Chapter routes
@app.route('/api/subjects/<int:subject_id>/chapters', methods=['GET'])
@jwt_required()
def get_chapters(subject_id):
    try:
        chapters = db.session.query(
            Chapter.id,
            Chapter.name,
            Chapter.description,
            Chapter.theory,
            Chapter.is_active,
            func.count(Quiz.id).label('quiz_count')
        ).outerjoin(Quiz).filter(
            and_(Chapter.subject_id == subject_id, Chapter.is_active == True)
        ).group_by(Chapter.id).order_by(desc(Chapter.created_at)).all()
        
        chapter_list = []
        for chapter in chapters:
            chapter_list.append({
                'id': chapter.id,
                'name': chapter.name,
                'description': chapter.description,
                'theory': chapter.theory,
                'is_active': chapter.is_active,
                'quiz_count': chapter.quiz_count
            })
        
        return jsonify(chapter_list), 200
        
    except Exception as e:
        print(f"Get chapters error: {str(e)}")
        return jsonify({'message': 'Failed to get chapters', 'error': str(e)}), 422

@app.route('/api/chapters', methods=['POST'])
@admin_required
def create_chapter():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        name = data.get('name')
        description = data.get('description')
        theory = data.get('theory')
        subject_id = data.get('subject_id')
        current_user_id = int(get_jwt_identity())
        
        if not all([name, subject_id]):
            return jsonify({'message': 'Name and subject are required'}), 400
        
        # Check if subject exists
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'message': 'Subject not found'}), 404
        
        chapter = Chapter(
            name=name,
            description=description,
            theory=theory,
            subject_id=subject_id,
            created_by=current_user_id
        )
        
        db.session.add(chapter)
        db.session.commit()
        
        return jsonify({'message': 'Chapter created successfully', 'chapter_id': chapter.id}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Create chapter error: {str(e)}")
        return jsonify({'message': 'Failed to create chapter', 'error': str(e)}), 500

@app.route('/api/chapters/<int:chapter_id>', methods=['PUT'])
@admin_required
def update_chapter(chapter_id):
    try:
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'message': 'Chapter not found'}), 404
            
        data = request.get_json() or {}
        name = data.get('name')
        description = data.get('description')
        theory = data.get('theory')
        
        if name:
            chapter.name = name.strip()
        if description is not None:
            chapter.description = description.strip()
        if theory is not None:
            chapter.theory = theory.strip()
            
        db.session.commit()
        return jsonify({'message': 'Chapter updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Update chapter error: {str(e)}")
        return jsonify({'message': 'Failed to update chapter', 'error': str(e)}), 500

@app.route('/api/chapters/<int:chapter_id>', methods=['DELETE'])
@admin_required
def delete_chapter(chapter_id):
    try:
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'message': 'Chapter not found'}), 404
            
        # Delete all associated data in correct order
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        for quiz in quizzes:
            # Delete user answers for all questions in this quiz
            questions = Question.query.filter_by(quiz_id=quiz.id).all()
            for question in questions:
                UserAnswer.query.filter_by(question_id=question.id).delete()
            
            # Delete all questions in this quiz
            Question.query.filter_by(quiz_id=quiz.id).delete()
            
            # Delete all quiz attempts for this quiz
            QuizAttempt.query.filter_by(quiz_id=quiz.id).delete()
            
            # Delete the quiz
            db.session.delete(quiz)
        
        # Finally delete the chapter
        db.session.delete(chapter)
        db.session.commit()
        
        return jsonify({'message': 'Chapter deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete chapter error: {str(e)}")
        return jsonify({'message': 'Failed to delete chapter', 'error': str(e)}), 500

# Quiz routes (updated)
@app.route('/api/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@jwt_required()
def get_chapter_quizzes(chapter_id):
    try:
        quizzes = db.session.query(
            Quiz.id,
            Quiz.title,
            Quiz.description,
            Quiz.time_limit,
            Quiz.questions_per_attempt,
            Quiz.is_active,
            func.count(Question.id).label('question_count')
        ).outerjoin(Question).filter(
            and_(Quiz.chapter_id == chapter_id, Quiz.is_active == True)
        ).group_by(Quiz.id).order_by(desc(Quiz.created_at)).all()
        
        quiz_list = []
        for quiz in quizzes:
            quiz_list.append({
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'time_limit': quiz.time_limit,
                'questions_per_attempt': quiz.questions_per_attempt,
                'is_active': quiz.is_active,
                'question_count': quiz.question_count
            })
        
        return jsonify(quiz_list), 200
        
    except Exception as e:
        print(f"Get chapter quizzes error: {str(e)}")
        return jsonify({'message': 'Failed to get quizzes', 'error': str(e)}), 422

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'message': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Create token with user ID as string to avoid JWT issues
        access_token = create_access_token(identity=str(user.id))
        
        # Update login streak
        today = datetime.utcnow().date()
        if user.last_active_date:
            delta = today - user.last_active_date
            if delta.days == 1:
                user.streak_count += 1
            elif delta.days > 1:
                user.streak_count = 1
        else:
            user.streak_count = 1
        user.last_active_date = today
        
        # Check and unlock badges for user
        check_badges(user)
        db.session.commit()
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'xp': user.xp,
                'streak_count': user.streak_count,
                'gender': user.gender,
                'profile_pic': user.profile_pic
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'gender': user.gender,
            'profile_pic': user.profile_pic
        }), 200
        
    except Exception as e:
        print(f"Profile error: {str(e)}")
        return jsonify({'message': 'Failed to get profile', 'error': str(e)}), 422

# Upload profile picture
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/profile/upload', methods=['POST'])
@jwt_required()
def upload_profile_pic():
    try:
        import uuid
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        if 'file' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No file selected for uploading'}), 400
            
        if file and allowed_file(file.filename):
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"user_{user.id}_{uuid.uuid4().hex}.{file_ext}"
            
            upload_dir = os.path.join(BASE_DIR, 'static', 'uploads', 'profile_pics')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # Delete old profile pic if it exists
            if user.profile_pic:
                old_pic_path = os.path.join(upload_dir, user.profile_pic)
                if os.path.exists(old_pic_path):
                    try:
                        os.remove(old_pic_path)
                    except Exception as err:
                        print(f"Failed to remove old profile pic: {err}")
            
            user.profile_pic = filename
            db.session.commit()
            
            return jsonify({
                'message': 'Profile picture uploaded successfully',
                'profile_pic': filename
            }), 200
        else:
            return jsonify({'message': 'Allowed image types are png, jpg, jpeg, gif'}), 400
            
    except Exception as e:
        db.session.rollback()
        print(f"Upload profile pic error: {str(e)}")
        return jsonify({'message': 'Failed to upload profile picture', 'error': str(e)}), 500

# Quiz routes
@app.route('/api/quizzes', methods=['GET'])
@jwt_required()
def get_quizzes():
    try:
        quizzes = db.session.query(
            Quiz.id,
            Quiz.title,
            Quiz.description,
            Quiz.time_limit,
            Quiz.questions_per_attempt,
            Quiz.is_active,
            func.count(Question.id).label('question_count')
        ).outerjoin(Question).filter(
            Quiz.is_active == True
        ).group_by(Quiz.id).order_by(desc(Quiz.created_at)).all()
        
        quiz_list = []
        for quiz in quizzes:
            quiz_list.append({
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'time_limit': quiz.time_limit,
                'questions_per_attempt': quiz.questions_per_attempt,
                'is_active': quiz.is_active,
                'question_count': quiz.question_count
            })
        
        return jsonify(quiz_list), 200
        
    except Exception as e:
        print(f"Get quizzes error: {str(e)}")
        return jsonify({'message': 'Failed to get quizzes', 'error': str(e)}), 422

@app.route('/api/quizzes', methods=['POST'])
@admin_required
def create_quiz():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        title = data.get('title')
        description = data.get('description')
        time_limit = data.get('time_limit', 30)
        questions_per_attempt = data.get('questions_per_attempt', 8)
        chapter_id = data.get('chapter_id')
        current_user_id = int(get_jwt_identity())
        
        if not all([title, chapter_id]):
            return jsonify({'message': 'Title and chapter are required'}), 400
        
        # Check if chapter exists
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({'message': 'Chapter not found'}), 404
        
        quiz = Quiz(
            title=title,
            description=description,
            time_limit=time_limit,
            questions_per_attempt=int(questions_per_attempt) if questions_per_attempt else 8,
            chapter_id=chapter_id,
            created_by=current_user_id
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        return jsonify({'message': 'Quiz created successfully', 'quiz_id': quiz.id}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Create quiz error: {str(e)}")
        return jsonify({'message': 'Failed to create quiz', 'error': str(e)}), 500

@app.route('/api/quizzes/<int:quiz_id>', methods=['PUT'])
@admin_required
def update_quiz(quiz_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'message': 'Quiz not found'}), 404
            
        # Update quiz fields
        if 'title' in data:
            quiz.title = data['title']
        if 'description' in data:
            quiz.description = data['description']
        if 'time_limit' in data:
            quiz.time_limit = data['time_limit']
        if 'is_active' in data:
            quiz.is_active = data['is_active']
        if 'questions_per_attempt' in data:
            quiz.questions_per_attempt = int(data['questions_per_attempt'])
        
        db.session.commit()
        
        return jsonify({'message': 'Quiz updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Update quiz error: {str(e)}")
        return jsonify({'message': 'Failed to update quiz', 'error': str(e)}), 500

@app.route('/api/quizzes/<int:quiz_id>/questions', methods=['GET'])
@jwt_required()
def get_quiz_questions(quiz_id):
    try:
        import random
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'message': 'Quiz not found'}), 404
            
        current_user_id = int(get_jwt_identity())
        
        # Use lockout status helper to clean up expired attempts
        status_info = get_quiz_lockout_status(current_user_id)
        active_attempt_info = status_info.get('active_attempt')
        
        questions = []
        if active_attempt_info and active_attempt_info['quiz_id'] == quiz_id:
            attempt = QuizAttempt.query.get(active_attempt_info['id'])
            if attempt and attempt.question_ids:
                id_list = [int(x) for x in attempt.question_ids.split(',') if x.strip()]
                db_questions = {q.id: q for q in Question.query.filter(Question.id.in_(id_list)).all()}
                questions = [db_questions[qid] for qid in id_list if qid in db_questions]
        
        if not questions:
            # If no active attempt or it doesn't have locked question_ids yet, sample them
            all_questions = Question.query.filter_by(quiz_id=quiz_id).all()
            random.shuffle(all_questions)
            k = quiz.questions_per_attempt if quiz.questions_per_attempt else 8
            questions = all_questions[:k]
        
        # Shuffling the order in which options are presented and question list is randomized
        shuffled_questions = list(questions)
        random.shuffle(shuffled_questions)
        
        question_list = []
        for question in shuffled_questions:
            options = [
                {'text': question.option_a, 'orig': 'A'},
                {'text': question.option_b, 'orig': 'B'},
                {'text': question.option_c, 'orig': 'C'},
                {'text': question.option_d, 'orig': 'D'}
            ]
            random.shuffle(options)
            
            question_list.append({
                'id': question.id,
                'question': question.question,
                'option_a': options[0]['text'],
                'option_a_orig': options[0]['orig'],
                'option_b': options[1]['text'],
                'option_b_orig': options[1]['orig'],
                'option_c': options[2]['text'],
                'option_c_orig': options[2]['orig'],
                'option_d': options[3]['text'],
                'option_d_orig': options[3]['orig'],
                'points': question.points,
                'hint': question.hint,
                'explanation': question.explanation
            })
        
        return jsonify(question_list), 200
        
    except Exception as e:
        print(f"Get quiz questions error: {str(e)}")
        return jsonify({'message': 'Failed to get questions', 'error': str(e)}), 422

@app.route('/api/quizzes/<int:quiz_id>/questions', methods=['POST'])
@admin_required
def add_question(quiz_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        question_text = data.get('question')
        option_a = data.get('option_a')
        option_b = data.get('option_b')
        option_c = data.get('option_c')
        option_d = data.get('option_d')
        correct_answer = data.get('correct_answer')
        points = data.get('points', 1)
        
        if not all([question_text, option_a, option_b, option_c, option_d, correct_answer]):
            return jsonify({'message': 'All fields are required'}), 400
        
        if correct_answer not in ['A', 'B', 'C', 'D']:
            return jsonify({'message': 'Correct answer must be A, B, C, or D'}), 400
        
        question = Question(
            quiz_id=quiz_id,
            question=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            points=points
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({'message': 'Question added successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Add question error: {str(e)}")
        return jsonify({'message': 'Failed to add question', 'error': str(e)}), 500

@app.route('/api/questions/<int:question_id>', methods=['PUT'])
@admin_required
def update_question(question_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'message': 'Question not found'}), 404
            
        # Update question fields
        if 'question' in data:
            question.question = data['question']
        if 'option_a' in data:
            question.option_a = data['option_a']
        if 'option_b' in data:
            question.option_b = data['option_b']
        if 'option_c' in data:
            question.option_c = data['option_c']
        if 'option_d' in data:
            question.option_d = data['option_d']
        if 'correct_answer' in data:
            if data['correct_answer'] not in ['A', 'B', 'C', 'D']:
                return jsonify({'message': 'Correct answer must be A, B, C, or D'}), 400
            question.correct_answer = data['correct_answer']
        if 'points' in data:
            question.points = data['points']
        
        db.session.commit()
        
        return jsonify({'message': 'Question updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Update question error: {str(e)}")
        return jsonify({'message': 'Failed to update question', 'error': str(e)}), 500

@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
@admin_required
def delete_question(question_id):
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'message': 'Question not found'}), 404
            
        # Delete associated user answers first
        UserAnswer.query.filter_by(question_id=question_id).delete()
        
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({'message': 'Question deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete question error: {str(e)}")
        return jsonify({'message': 'Failed to delete question', 'error': str(e)}), 500

@app.route('/api/quizzes/<int:quiz_id>', methods=['DELETE'])
@admin_required
def delete_quiz(quiz_id):
    try:
        current_user_id = int(get_jwt_identity())
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'message': 'Quiz not found'}), 404
            
        # Delete all associated data in the correct order
        # 1. Delete user answers for all questions in this quiz
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        for question in questions:
            UserAnswer.query.filter_by(question_id=question.id).delete()
        
        # 2. Delete all questions in this quiz
        Question.query.filter_by(quiz_id=quiz_id).delete()
        
        # 3. Delete all quiz attempts for this quiz
        QuizAttempt.query.filter_by(quiz_id=quiz_id).delete()
        
        # 4. Finally delete the quiz itself
        db.session.delete(quiz)
        db.session.commit()
        
        return jsonify({'message': 'Quiz deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete quiz error: {str(e)}")
        return jsonify({'message': 'Failed to delete quiz', 'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    try:
        current_user_id = int(get_jwt_identity())
        
        # Prevent admin from deleting themselves
        if current_user_id == user_id:
            return jsonify({'message': 'Cannot delete your own account'}), 400
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        # Delete user's quiz attempts and answers
        user_attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
        for attempt in user_attempts:
            UserAnswer.query.filter_by(attempt_id=attempt.id).delete()
            db.session.delete(attempt)
        
        # Delete user's created quizzes and their questions
        user_quizzes = Quiz.query.filter_by(created_by=user_id).all()
        for quiz in user_quizzes:
            # Delete questions and their answers
            questions = Question.query.filter_by(quiz_id=quiz.id).all()
            for question in questions:
                UserAnswer.query.filter_by(question_id=question.id).delete()
                db.session.delete(question)
            
            # Delete quiz attempts
            QuizAttempt.query.filter_by(quiz_id=quiz.id).delete()
            db.session.delete(quiz)
        
        # Finally delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete user error: {str(e)}")
        return jsonify({'message': 'Failed to delete user', 'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        # Update user fields
        if 'username' in data:
            # Check if username already exists (excluding current user)
            existing_user = User.query.filter(
                and_(User.username == data['username'], User.id != user_id)
            ).first()
            if existing_user:
                return jsonify({'message': 'Username already exists'}), 400
            user.username = data['username']
            
        if 'email' in data:
            # Check if email already exists (excluding current user)
            existing_user = User.query.filter(
                and_(User.email == data['email'], User.id != user_id)
            ).first()
            if existing_user:
                return jsonify({'message': 'Email already exists'}), 400
            user.email = data['email']
        
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Update user error: {str(e)}")
        return jsonify({'message': 'Failed to update user', 'error': str(e)}), 500

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def add_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not all([username, email, password]):
            return jsonify({'message': 'Username, email, and password are required'}), 400
        
        # Check if user exists
        existing_user = User.query.filter(
            or_(User.username == username, User.email == email)
        ).first()
        
        if existing_user:
            return jsonify({'message': 'Username or email already exists'}), 400
        
        # Validate role
        if role not in ['user', 'admin']:
            return jsonify({'message': 'Invalid role. Must be user or admin'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash.decode('utf-8'),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Add user error: {str(e)}")
        return jsonify({'message': 'Failed to create user', 'error': str(e)}), 500
def get_quiz_lockout_status(user_id):
    now = datetime.utcnow()
    lock_duration = timedelta(minutes=20)
    
    # 1. Finalize any uncompleted active attempts that have exceeded their time limit
    active_attempts = QuizAttempt.query.filter_by(user_id=user_id, completed_at=None).all()
    for attempt in active_attempts:
        quiz = Quiz.query.get(attempt.quiz_id)
        time_limit = quiz.time_limit if quiz else 30
        expired_at = attempt.started_at + timedelta(minutes=time_limit)
        if now > expired_at:
            attempt.completed_at = expired_at
            db.session.add(attempt)
    db.session.commit()
    
    # 2. Get the latest attempt
    latest_attempt = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.started_at.desc()).first()
    if not latest_attempt:
        return {
            'is_locked': False,
            'locked_until': None,
            'remaining_seconds': 0,
            'active_attempt': None
        }
        
    if latest_attempt.completed_at is not None:
        lock_until = latest_attempt.completed_at + lock_duration
        if now < lock_until:
            return {
                'is_locked': True,
                'locked_until': lock_until.isoformat() + 'Z',
                'remaining_seconds': int((lock_until - now).total_seconds()),
                'active_attempt': None
            }
    else:
        quiz = Quiz.query.get(latest_attempt.quiz_id)
        time_limit = quiz.time_limit if quiz else 30
        remaining_seconds = int(((latest_attempt.started_at + timedelta(minutes=time_limit)) - now).total_seconds())
        if remaining_seconds < 0:
            remaining_seconds = 0
            
        return {
            'is_locked': True,
            'locked_until': (latest_attempt.started_at + timedelta(minutes=time_limit) + lock_duration).isoformat() + 'Z',
            'remaining_seconds': remaining_seconds + 1200,
            'active_attempt': {
                'id': latest_attempt.id,
                'quiz_id': latest_attempt.quiz_id,
                'quiz_title': quiz.title if quiz else "Quiz",
                'time_limit': time_limit,
                'started_at': latest_attempt.started_at.isoformat() + 'Z',
                'remaining_seconds': remaining_seconds
            }
        }
        
    return {
        'is_locked': False,
        'locked_until': None,
        'remaining_seconds': 0,
        'active_attempt': None
    }

@app.route('/api/quizzes/lockout-status', methods=['GET'])
@jwt_required()
def get_lockout_status_route():
    try:
        current_user_id = int(get_jwt_identity())
        status = get_quiz_lockout_status(current_user_id)
        return jsonify(status), 200
    except Exception as e:
        print(f"Error checking lockout status: {str(e)}")
        return jsonify({'message': 'Failed to check lockout status', 'error': str(e)}), 500

@app.route('/api/attempts/<int:attempt_id>/abandon', methods=['POST'])
@jwt_required()
def abandon_quiz_route(attempt_id):
    try:
        current_user_id = int(get_jwt_identity())
        attempt = QuizAttempt.query.filter_by(id=attempt_id, user_id=current_user_id).first()
        if not attempt:
            return jsonify({'message': 'Quiz attempt not found or unauthorized'}), 404
            
        if attempt.completed_at is not None:
            return jsonify({'message': 'Quiz attempt already completed'}), 400
            
        attempt.completed_at = datetime.utcnow()
        
        # Calculate score based on user answers so far
        user_answers = UserAnswer.query.filter_by(attempt_id=attempt_id).all()
        if attempt.question_ids:
            id_list = [int(x) for x in attempt.question_ids.split(',') if x.strip()]
            db_questions = {q.id: q for q in Question.query.filter(Question.id.in_(id_list)).all()}
            questions = [db_questions[qid] for qid in id_list if qid in db_questions]
        else:
            questions = Question.query.filter_by(quiz_id=attempt.quiz_id).all()
        
        score = 0.0
        for question in questions:
            user_ans = next((ua for ua in user_answers if ua.question_id == question.id), None)
            if user_ans and user_ans.is_correct:
                score += question.points * 0.75 if user_ans.hint_used else question.points
                
        attempt.score = int(round(score))
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz attempt successfully abandoned. You are now locked out of MCQs for 20 minutes.',
            'attempt_id': attempt_id,
            'completed_at': attempt.completed_at.isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error abandoning quiz: {str(e)}")
        return jsonify({'message': 'Failed to abandon quiz', 'error': str(e)}), 500

@app.route('/api/quizzes/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    try:
        current_user_id = int(get_jwt_identity())
        
        # Check lockout status
        status = get_quiz_lockout_status(current_user_id)
        
        if status['is_locked']:
            active_attempt = status['active_attempt']
            if active_attempt:
                if active_attempt['quiz_id'] == quiz_id:
                    # Resuming the same active quiz
                    return jsonify({
                        'attempt_id': active_attempt['id'],
                        'quiz_title': active_attempt['quiz_title'],
                        'time_limit': active_attempt['time_limit'],
                        'total_questions': QuizAttempt.query.get(active_attempt['id']).total_questions,
                        'started_at': active_attempt['started_at'],
                        'remaining_seconds': active_attempt['remaining_seconds'],
                        'resumed': True
                    }), 200
                else:
                    # Abandoning previous active quiz for a different one
                    old_attempt_id = active_attempt['id']
                    old_attempt = QuizAttempt.query.get(old_attempt_id)
                    if old_attempt:
                        old_attempt.completed_at = datetime.utcnow()
                        db.session.add(old_attempt)
                        db.session.commit()
                        
                    status = get_quiz_lockout_status(current_user_id)
                    return jsonify({
                        'message': 'You have abandoned your previous active quiz. MCQ quizzes are now locked for 20 minutes.',
                        'is_locked': True,
                        'locked_until': status['locked_until'],
                        'remaining_seconds': status['remaining_seconds']
                    }), 403
            else:
                return jsonify({
                    'message': 'MCQ Quizzes are locked for 20 minutes.',
                    'is_locked': True,
                    'locked_until': status['locked_until'],
                    'remaining_seconds': status['remaining_seconds']
                }), 403

        # Get quiz details
        quiz = Quiz.query.filter_by(id=quiz_id, is_active=True).first()
        
        if not quiz:
            return jsonify({'message': 'Quiz not found or inactive'}), 404
        
        # Get questions list and configure questions_per_attempt limit
        data = request.get_json() or {}
        client_question_ids = data.get('question_ids', [])
        
        k = quiz.questions_per_attempt if quiz.questions_per_attempt else 8
        
        if client_question_ids:
            clean_ids = [int(qid) for qid in client_question_ids if qid]
            # Verify they all belong to this quiz
            db_questions = Question.query.filter(Question.id.in_(clean_ids), Question.quiz_id == quiz_id).all()
            final_ids = [q.id for q in db_questions]
            question_ids_str = ",".join(str(qid) for qid in final_ids)
            question_count = len(final_ids)
        else:
            # Fallback selection
            all_questions = Question.query.filter_by(quiz_id=quiz_id).all()
            import random
            random.shuffle(all_questions)
            selected = all_questions[:k]
            question_ids_str = ",".join(str(q.id) for q in selected)
            question_count = len(selected)
            
        # Create quiz attempt
        attempt = QuizAttempt(
            user_id=current_user_id,
            quiz_id=quiz_id,
            total_questions=question_count,
            question_ids=question_ids_str
        )
        
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            'attempt_id': attempt.id,
            'quiz_title': quiz.title,
            'time_limit': quiz.time_limit,
            'total_questions': question_count,
            'started_at': attempt.started_at.isoformat() + 'Z',
            'remaining_seconds': quiz.time_limit * 60,
            'resumed': False
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Start quiz error: {str(e)}")
        return jsonify({'message': 'Failed to start quiz', 'error': str(e)}), 500

@app.route('/api/attempts/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(attempt_id):
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)
        hints_revealed = data.get('hints_used', {})
        
        # Verify attempt belongs to current user
        attempt = QuizAttempt.query.filter_by(id=attempt_id, user_id=current_user_id).first()
        
        if not attempt:
            return jsonify({'message': 'Attempt not found or unauthorized'}), 404
        
        # Get attempt questions
        if attempt.question_ids:
            id_list = [int(x) for x in attempt.question_ids.split(',') if x.strip()]
            db_questions = {q.id: q for q in Question.query.filter(Question.id.in_(id_list)).all()}
            questions = [db_questions[qid] for qid in id_list if qid in db_questions]
        else:
            questions = Question.query.filter_by(quiz_id=attempt.quiz_id).all()
        
        score = 0.0
        total_points = 0
        
        for question in questions:
            selected_answer = answers.get(str(question.id))
            is_correct = selected_answer == question.correct_answer
            
            # Check if hint was used
            hint_used = str(question.id) in hints_revealed or hints_revealed.get(str(question.id)) == True
            
            points_obtained = 0.0
            if is_correct:
                points_obtained = question.points * 0.75 if hint_used else question.points
                score += points_obtained
            
            total_points += question.points
            
            # Save user answer
            user_answer = UserAnswer(
                attempt_id=attempt_id,
                question_id=question.id,
                selected_answer=selected_answer,
                is_correct=is_correct,
                hint_used=hint_used
            )
            db.session.add(user_answer)
        
        # Update user gamification info
        user = User.query.get(current_user_id)
        today = datetime.utcnow().date()
        if user.last_active_date:
            delta = today - user.last_active_date
            if delta.days == 1:
                user.streak_count += 1
            elif delta.days > 1:
                user.streak_count = 1
        else:
            user.streak_count = 1
        user.last_active_date = today
        
        # Calculate XP gained
        xp_gained = int(round(score * 10))
        is_perfect = (score == total_points)
        if is_perfect:
            xp_gained += 50 # 50 XP bonus for perfect score
        
        user.xp += xp_gained
        
        # Fetch target quiz details
        quiz = Quiz.query.get(attempt.quiz_id)
        
        # Calculate Elo changes
        R_U = user.elo_rating or 1000
        R_Q = quiz.elo_rating or 1000
        
        # Expected score
        E_U = 1.0 / (1.0 + 10.0 ** ((R_Q - R_U) / 400.0))
        
        # Actual score percentage (0.0 to 1.0)
        S_U = (score / total_points) if total_points > 0 else 0.0
        
        # K-factor
        K = 32
        delta = K * (S_U - E_U)
        
        new_user_elo = int(round(R_U + delta))
        new_quiz_elo = int(round(R_Q - delta))
        
        # Prevent Elo from dropping below a sensible floor, e.g., 100
        if new_user_elo < 100: new_user_elo = 100
        if new_quiz_elo < 100: new_quiz_elo = 100
        
        # Apply updates
        user.elo_rating = new_user_elo
        quiz.elo_rating = new_quiz_elo
        
        # Log Elo history
        elo_history = UserEloHistory(
            user_id=user.id,
            elo_rating=new_user_elo,
            attempt_id=attempt.id
        )
        db.session.add(elo_history)
        
        # Update quiz attempt
        attempt.score = int(round(score))
        attempt.time_taken = time_taken
        attempt.completed_at = datetime.utcnow()
        
        # Check badges
        check_badges(user)
        
        db.session.commit()
        
        return jsonify({
            'score': attempt.score,
            'total_points': total_points,
            'percentage': round((score / total_points * 100) if total_points > 0 else 0, 2),
            'xp_gained': xp_gained,
            'streak_count': user.streak_count,
            'elo_rating': user.elo_rating,
            'elo_change': int(round(delta))
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Submit quiz error: {str(e)}")
        return jsonify({'message': 'Failed to submit quiz', 'error': str(e)}), 500

# Admin routes
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    try:
        users = User.query.order_by(desc(User.created_at)).all()
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify(user_list), 200
        
    except Exception as e:
        print(f"Get users error: {str(e)}")
        return jsonify({'message': 'Failed to get users', 'error': str(e)}), 422

@app.route('/api/admin/reports', methods=['GET'])
@admin_required
def get_reports():
    try:
        # Get all completed quiz attempts with explicit joins
        completed_attempts = db.session.query(
            QuizAttempt.id,
            QuizAttempt.user_id,
            QuizAttempt.quiz_id,
            QuizAttempt.score,
            QuizAttempt.total_questions,
            QuizAttempt.completed_at,
            Quiz.title.label('quiz_title'),
            User.username
        ).select_from(QuizAttempt).join(
            Quiz, QuizAttempt.quiz_id == Quiz.id
        ).join(
            User, QuizAttempt.user_id == User.id
        ).filter(
            QuizAttempt.completed_at.isnot(None)
        ).all()
        
        # Process quiz statistics
        quiz_stats_dict = {}
        user_stats_dict = {}
        daily_stats = {}
        score_counts = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        for attempt in completed_attempts:
            # Calculate percentage safely
            if attempt.total_questions > 0:
                percentage = (attempt.score / attempt.total_questions) * 100
            else:
                percentage = 0
            
            # Quiz statistics
            quiz_title = attempt.quiz_title
            if quiz_title not in quiz_stats_dict:
                quiz_stats_dict[quiz_title] = {
                    'quiz_title': quiz_title,
                    'attempts': 0,
                    'total_percentage': 0,
                    'max_score': 0,
                    'min_score': 100
                }
            
            quiz_stats_dict[quiz_title]['attempts'] += 1
            quiz_stats_dict[quiz_title]['total_percentage'] += percentage
            quiz_stats_dict[quiz_title]['max_score'] = max(quiz_stats_dict[quiz_title]['max_score'], percentage)
            quiz_stats_dict[quiz_title]['min_score'] = min(quiz_stats_dict[quiz_title]['min_score'], percentage)
            
            # User statistics
            username = attempt.username
            if username not in user_stats_dict:
                user_stats_dict[username] = {
                    'username': username,
                    'attempts': 0,
                    'total_percentage': 0,
                    'best_score': 0
                }
            
            user_stats_dict[username]['attempts'] += 1
            user_stats_dict[username]['total_percentage'] += percentage
            user_stats_dict[username]['best_score'] = max(user_stats_dict[username]['best_score'], percentage)
            
            # Daily activity (last 7 days)
            if attempt.completed_at >= datetime.utcnow() - timedelta(days=7):
                date_str = attempt.completed_at.date().isoformat()
                if date_str not in daily_stats:
                    daily_stats[date_str] = {'total_percentage': 0, 'count': 0}
                daily_stats[date_str]['total_percentage'] += percentage
                daily_stats[date_str]['count'] += 1
            
            # Score distribution
            if percentage >= 80:
                score_counts['excellent'] += 1
            elif percentage >= 60:
                score_counts['good'] += 1
            elif percentage >= 40:
                score_counts['fair'] += 1
            else:
                score_counts['poor'] += 1
        
        # Calculate averages for quiz stats
        quiz_statistics = []
        for stats in quiz_stats_dict.values():
            avg_score = stats['total_percentage'] / stats['attempts'] if stats['attempts'] > 0 else 0
            min_score = stats['min_score'] if stats['attempts'] > 0 else 0
            quiz_statistics.append({
                'quiz_title': stats['quiz_title'],
                'attempts': stats['attempts'],
                'avg_score': round(avg_score, 2),
                'max_score': round(stats['max_score'], 2),
                'min_score': round(min_score, 2)
            })
        
        # Calculate averages for user stats
        user_performance = []
        for stats in user_stats_dict.values():
            avg_score = stats['total_percentage'] / stats['attempts'] if stats['attempts'] > 0 else 0
            user_performance.append({
                'username': stats['username'],
                'attempts': stats['attempts'],
                'avg_score': round(avg_score, 2),
                'best_score': round(stats['best_score'], 2)
            })
        
        # Calculate daily averages
        user_activity = []
        for date_str, stats in daily_stats.items():
            avg_percentage = stats['total_percentage'] / stats['count'] if stats['count'] > 0 else 0
            user_activity.append({
                'date': date_str,
                'avg_percentage': round(avg_percentage, 2)
            })
        
        # Sort results
        quiz_statistics.sort(key=lambda x: x['attempts'], reverse=True)
        user_performance.sort(key=lambda x: x['avg_score'], reverse=True)
        user_activity.sort(key=lambda x: x['date'])
        
        return jsonify({
            'quiz_statistics': quiz_statistics,
            'user_performance': user_performance,
            'user_activity': user_activity,
            'score_distribution': score_counts
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Get reports error: {str(e)}")
        return jsonify({'message': 'Failed to get reports', 'error': str(e)}), 422

@app.route('/api/user/attempts', methods=['GET'])
@jwt_required()
def get_user_attempts():
    try:
        current_user_id = int(get_jwt_identity())
        target_username = request.args.get('username')
        
        if target_username:
            user = User.query.filter_by(username=target_username).first()
            if not user:
                return jsonify({'message': 'User not found'}), 404
            user_id = user.id
        else:
            user_id = current_user_id
        
        attempts = db.session.query(
            QuizAttempt.id,
            Quiz.title,
            QuizAttempt.score,
            QuizAttempt.total_questions,
            QuizAttempt.time_taken,
            QuizAttempt.started_at,
            QuizAttempt.completed_at,
            func.coalesce(
                (func.cast(QuizAttempt.score, db.Float) / 
                 func.nullif(QuizAttempt.total_questions, 0) * 100), 0
            ).label('percentage')
        ).join(Quiz).filter(
            and_(
                QuizAttempt.user_id == user_id,
                QuizAttempt.completed_at.isnot(None)
            )
        ).order_by(desc(QuizAttempt.completed_at)).all()
        
        attempt_list = []
        for attempt in attempts:
            attempt_list.append({
                'id': attempt.id,
                'quiz_title': attempt.title,
                'score': attempt.score,
                'total_questions': attempt.total_questions,
                'time_taken': attempt.time_taken,
                'started_at': attempt.started_at.isoformat(),
                'completed_at': attempt.completed_at.isoformat(),
                'percentage': round(attempt.percentage, 2) if attempt.percentage else 0
            })
        
        return jsonify(attempt_list), 200
        
    except Exception as e:
        print(f"Get user attempts error: {str(e)}")
        return jsonify({'message': 'Failed to get user attempts', 'error': str(e)}), 422

@app.route('/api/quizzes/<int:quiz_id>/attempts', methods=['GET'])
@jwt_required()
def get_quiz_attempts(quiz_id):
    try:
        # Check if user is admin or if it's their own quiz attempts
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if current_user.role == 'admin':
            # Admin can see all attempts for any quiz
            attempts = db.session.query(
                QuizAttempt.id,
                QuizAttempt.score,
                QuizAttempt.total_questions,
                QuizAttempt.time_taken,
                QuizAttempt.completed_at,
                User.username,
                func.coalesce(
                    (func.cast(QuizAttempt.score, db.Float) / 
                     func.nullif(QuizAttempt.total_questions, 0) * 100), 0
                ).label('percentage')
            ).join(User).filter(
                and_(
                    QuizAttempt.quiz_id == quiz_id,
                    QuizAttempt.completed_at.isnot(None)
                )
            ).order_by(desc(QuizAttempt.completed_at)).all()
        else:
            # Regular users can only see their own attempts
            attempts = db.session.query(
                QuizAttempt.id,
                QuizAttempt.score,
                QuizAttempt.total_questions,
                QuizAttempt.time_taken,
                QuizAttempt.completed_at,
                User.username,
                func.coalesce(
                    (func.cast(QuizAttempt.score, db.Float) / 
                     func.nullif(QuizAttempt.total_questions, 0) * 100), 0
                ).label('percentage')
            ).join(User).filter(
                and_(
                    QuizAttempt.quiz_id == quiz_id,
                    QuizAttempt.user_id == current_user_id,
                    QuizAttempt.completed_at.isnot(None)
                )
            ).order_by(desc(QuizAttempt.completed_at)).all()
        
        attempt_list = []
        for attempt in attempts:
            attempt_list.append({
                'id': attempt.id,
                'username': attempt.username,
                'score': attempt.score,
                'total_questions': attempt.total_questions,
                'time_taken': attempt.time_taken,
                'completed_at': attempt.completed_at.isoformat(),
                'percentage': round(attempt.percentage, 2) if attempt.percentage else 0
            })
        
        return jsonify(attempt_list), 200
        
    except Exception as e:
        print(f"Get quiz attempts error: {str(e)}")
        return jsonify({'message': 'Failed to get quiz attempts', 'error': str(e)}), 422

# Job management routes (Admin only)
@app.route('/api/admin/jobs/test-reminders', methods=['POST'])
@admin_required
def test_reminders():
    try:
        count = test_user_reminders()
        return jsonify({
            'message': f'Successfully sent {count} reminder emails',
            'count': count
        }), 200
    except Exception as e:
        print(f"Test reminders error: {str(e)}")
        return jsonify({'message': 'Failed to send reminders', 'error': str(e)}), 500

@app.route('/api/admin/jobs/test-admin-report', methods=['POST'])
@admin_required
def test_admin_report():
    try:
        count = test_admin_report()
        return jsonify({
            'message': f'Successfully sent {count} admin report emails',
            'count': count
        }), 200
    except Exception as e:
        print(f"Test admin report error: {str(e)}")
        return jsonify({'message': 'Failed to send admin report', 'error': str(e)}), 500

@app.route('/api/admin/jobs/test-cleanup', methods=['POST'])
@admin_required
def test_cleanup():
    try:
        success = test_weekly_cleanup()
        return jsonify({
            'message': 'Weekly cleanup completed successfully' if success else 'Weekly cleanup failed',
            'success': success
        }), 200
    except Exception as e:
        print(f"Test cleanup error: {str(e)}")
        return jsonify({'message': 'Failed to run cleanup', 'error': str(e)}), 500

@app.route('/api/admin/jobs/inactive-users', methods=['GET'])
@admin_required
def get_inactive_users():
    try:
        users = test_get_inactive_users()
        return jsonify({
            'message': f'Found {len(users)} inactive users',
            'users': users
        }), 200
    except Exception as e:
        print(f"Get inactive users error: {str(e)}")
        return jsonify({'message': 'Failed to get inactive users', 'error': str(e)}), 500

@app.route('/api/admin/jobs/daily-stats', methods=['GET'])
@admin_required
def get_daily_stats():
    try:
        stats = test_get_daily_stats()
        return jsonify({
            'message': 'Daily statistics retrieved successfully',
            'stats': stats
        }), 200
    except Exception as e:
        print(f"Get daily stats error: {str(e)}")
        return jsonify({'message': 'Failed to get daily stats', 'error': str(e)}), 500

# --- CODE CHALLENGE ROUTES ---

@app.route('/api/challenges/all', methods=['GET'])
@admin_required
def get_all_challenges():
    """Admin: list every challenge across all chapters."""
    try:
        challenges = CodeChallenge.query.order_by(CodeChallenge.created_at.desc()).all()
        return jsonify([{
            'id': c.id, 'title': c.title, 'description': c.description,
            'difficulty': c.difficulty, 'time_limit': c.time_limit,
            'memory_limit': c.memory_limit, 'chapter_id': c.chapter_id,
            'is_active': c.is_active,
            'test_case_count': len(c.test_cases),
            'submission_count': len(c.submissions),
        } for c in challenges]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to get challenges', 'error': str(e)}), 500

@app.route('/api/challenges/<int:challenge_id>', methods=['GET'])
@jwt_required()
def get_challenge(challenge_id):
    """Get a single challenge by ID (for the editor page)."""
    try:
        c = CodeChallenge.query.get_or_404(challenge_id)
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        is_admin = user and user.role == 'admin'
        
        # Starter templates
        templates_list = [{
            'language': t.language,
            'template_code': t.template_code
        } for t in c.templates]
        
        # Test cases
        if is_admin:
            # Admins get everything
            test_cases_list = [{
                'id': tc.id,
                'input_data': tc.input_data,
                'expected_output': tc.expected_output,
                'is_hidden': tc.is_hidden
            } for tc in c.test_cases]
        else:
            # Users only get public example test cases
            test_cases_list = [{
                'input': tc.input_data,
                'output': tc.expected_output
            } for tc in c.test_cases if not tc.is_hidden]
            
        challenge_data = {
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'difficulty': c.difficulty,
            'time_limit': c.time_limit,
            'memory_limit': c.memory_limit,
            'chapter_id': c.chapter_id,
            'is_active': c.is_active,
            'templates': templates_list
        }
        
        if is_admin:
            challenge_data['test_cases'] = test_cases_list
        else:
            challenge_data['examples'] = test_cases_list
            
        return jsonify(challenge_data), 200
    except Exception as e:
        return jsonify({'message': 'Challenge not found', 'error': str(e)}), 404

@app.route('/api/challenges/<int:challenge_id>', methods=['DELETE'])
@admin_required
def delete_challenge(challenge_id):
    """Admin: delete a challenge and its test cases."""
    try:
        challenge = CodeChallenge.query.get_or_404(challenge_id)
        db.session.delete(challenge)
        db.session.commit()
        return jsonify({'message': 'Challenge deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete challenge', 'error': str(e)}), 500

@app.route('/api/challenges/<int:challenge_id>/toggle', methods=['POST'])
@admin_required
def toggle_challenge(challenge_id):
    """Admin: toggle active/inactive status."""
    try:
        challenge = CodeChallenge.query.get_or_404(challenge_id)
        challenge.is_active = not challenge.is_active
        db.session.commit()
        return jsonify({'message': 'Updated', 'is_active': challenge.is_active}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to toggle challenge', 'error': str(e)}), 500

@app.route('/api/user/submissions', methods=['GET'])
@jwt_required()
def get_user_submissions():
    """User: get their own code submission history."""
    try:
        current_user_id = int(get_jwt_identity())
        subs = CodeSubmission.query.filter_by(user_id=current_user_id)\
            .order_by(CodeSubmission.submitted_at.desc()).limit(20).all()
        return jsonify([{
            'id': s.id,
            'challenge_id': s.challenge_id,
            'challenge_title': s.challenge.title if s.challenge else 'Unknown',
            'language': s.language,
            'status': s.status,
            'execution_time': s.execution_time,
            'memory_used': s.memory_used,
            'submitted_at': s.submitted_at.isoformat() if s.submitted_at else None,
        } for s in subs]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to get submissions', 'error': str(e)}), 500

@app.route('/api/chapters/<int:chapter_id>/challenges', methods=['GET'])
@jwt_required()
def get_chapter_challenges(chapter_id):
    try:
        challenges = CodeChallenge.query.filter_by(chapter_id=chapter_id, is_active=True).all()
        return jsonify([{
            'id': c.id, 'title': c.title, 'description': c.description,
            'difficulty': c.difficulty, 'time_limit': c.time_limit,
            'memory_limit': c.memory_limit
        } for c in challenges]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to get challenges', 'error': str(e)}), 422

@app.route('/api/challenges', methods=['POST'])
@admin_required
def create_challenge():
    try:
        data = request.get_json()
        current_user_id = int(get_jwt_identity())
        
        challenge = CodeChallenge(
            title=data['title'],
            description=data['description'],
            chapter_id=data['chapter_id'],
            difficulty=data.get('difficulty', 'Medium'),
            time_limit=data.get('time_limit', 30),
            memory_limit=data.get('memory_limit', 256),
            created_by=current_user_id
        )
        db.session.add(challenge)
        db.session.flush() # Get ID
        
        # Save templates if provided in the creation payload
        templates_data = data.get('templates', {}) # dict e.g. {"python": "...", "cpp": "..."}
        if isinstance(templates_data, dict):
            for lang, code in templates_data.items():
                tpl = ChallengeTemplate(challenge_id=challenge.id, language=lang, template_code=code)
                db.session.add(tpl)
        
        db.session.commit()
        return jsonify({'message': 'Challenge created', 'challenge_id': challenge.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create challenge', 'error': str(e)}), 500

@app.route('/api/challenges/<int:challenge_id>', methods=['PUT'])
@admin_required
def update_challenge(challenge_id):
    try:
        data = request.get_json()
        challenge = CodeChallenge.query.get_or_404(challenge_id)
        
        challenge.title = data.get('title', challenge.title)
        challenge.description = data.get('description', challenge.description)
        challenge.difficulty = data.get('difficulty', challenge.difficulty)
        challenge.time_limit = data.get('time_limit', challenge.time_limit)
        challenge.memory_limit = data.get('memory_limit', challenge.memory_limit)
        challenge.chapter_id = data.get('chapter_id', challenge.chapter_id)
        if 'is_active' in data:
            challenge.is_active = data['is_active']
            
        # Update starter templates
        templates_data = data.get('templates', {})
        if isinstance(templates_data, dict):
            for lang, code in templates_data.items():
                tpl = ChallengeTemplate.query.filter_by(challenge_id=challenge_id, language=lang).first()
                if tpl:
                    tpl.template_code = code
                else:
                    tpl = ChallengeTemplate(challenge_id=challenge_id, language=lang, template_code=code)
                    db.session.add(tpl)
                    
        db.session.commit()
        return jsonify({'message': 'Challenge updated successfully', 'challenge_id': challenge.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update challenge', 'error': str(e)}), 500

@app.route('/api/challenges/<int:challenge_id>/testcases', methods=['POST'])
@admin_required
def add_testcase(challenge_id):
    try:
        data = request.get_json()
        tc = TestCase(
            challenge_id=challenge_id,
            input_data=data['input_data'],
            expected_output=data['expected_output'],
            is_hidden=data.get('is_hidden', True)
        )
        db.session.add(tc)
        db.session.commit()
        return jsonify({'message': 'Test case added'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add testcase', 'error': str(e)}), 500

@app.route('/api/challenges/<int:challenge_id>/testcases', methods=['PUT'])
@admin_required
def sync_testcases(challenge_id):
    try:
        data = request.get_json() # list of dicts
        challenge = CodeChallenge.query.get_or_404(challenge_id)
        
        submitted_ids = []
        for tc_data in data:
            tc_id = tc_data.get('id')
            if tc_id:
                tc = TestCase.query.filter_by(id=tc_id, challenge_id=challenge_id).first()
                if tc:
                    tc.input_data = tc_data['input_data']
                    tc.expected_output = tc_data['expected_output']
                    tc.is_hidden = tc_data.get('is_hidden', True)
                    submitted_ids.append(tc_id)
            else:
                new_tc = TestCase(
                    challenge_id=challenge_id,
                    input_data=tc_data['input_data'],
                    expected_output=tc_data['expected_output'],
                    is_hidden=tc_data.get('is_hidden', True)
                )
                db.session.add(new_tc)
                db.session.flush() # get ID
                submitted_ids.append(new_tc.id)
        
        # Delete test cases that were not in the submitted payload
        TestCase.query.filter(
            TestCase.challenge_id == challenge_id,
            ~TestCase.id.in_(submitted_ids)
        ).delete(synchronize_session=False)
        
        db.session.commit()
        return jsonify({'message': 'Test cases synchronized successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to sync test cases', 'error': str(e)}), 500

@app.route('/api/challenges/<int:challenge_id>/testcases/bulk', methods=['POST'])
@admin_required
def bulk_testcases(challenge_id):
    try:
        data = request.get_json()
        input_text = data.get('input_text', '')
        output_text = data.get('output_text', '')
        delimiter = data.get('delimiter', '===')
        is_hidden = data.get('is_hidden', True)
        
        # Split inputs and outputs by delimiter
        inputs = [i.strip() for i in input_text.split(delimiter) if i.strip()]
        outputs = [o.strip() for o in output_text.split(delimiter) if o.strip()]
        
        count = 0
        for i in range(len(inputs)):
            expected = outputs[i] if i < len(outputs) else ""
            tc = TestCase(
                challenge_id=challenge_id,
                input_data=inputs[i],
                expected_output=expected,
                is_hidden=is_hidden
            )
            db.session.add(tc)
            count += 1
            
        db.session.commit()
        return jsonify({'message': f'Successfully imported {count} test cases'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to bulk import test cases', 'error': str(e)}), 500

@app.route('/api/challenges/<int:challenge_id>/test-solution', methods=['POST'])
@admin_required
def test_solution(challenge_id):
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        auto_fill = data.get('auto_fill', False)
        
        test_cases = TestCase.query.filter_by(challenge_id=challenge_id).all()
        results = []
        
        for tc in test_cases:
            res = execute_code_api(code, language, tc.input_data)
            output_val = res.get('output', '').strip()
            status = res.get('status', 'Error')
            
            if auto_fill and status == 'Accepted':
                tc.expected_output = output_val
                
            results.append({
                'test_case_id': tc.id,
                'input': tc.input_data,
                'expected_before': tc.expected_output,
                'actual_output': output_val,
                'status': status,
                'time': res.get('time', 0),
                'memory': res.get('memory', 0)
            })
            
        if auto_fill:
            db.session.commit()
            
        return jsonify({
            'message': 'Verification complete',
            'results': results
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to verify solution', 'error': str(e)}), 500

LANGUAGE_MAP = {
    'python': 71,
    'java': 62,
    'c': 50,
    'cpp': 54,
    'javascript': 63,
    'php': 68
}

# Piston uses different language identifiers than common names.
# node = JavaScript (Node.js), gcc = C and C++
# These values come from `GET /api/v2/runtimes` — use the "language" field.
PISTON_LANG_MAP = {
    'python':     'python',
    'java':       'java',
    'c':          'c',          # Piston exposes 'c' via gcc runtime
    'cpp':        'c++',        # Piston exposes 'c++' via gcc runtime
    'javascript': 'javascript', # Piston exposes 'javascript' via node runtime
    'php':        'php',
}

# For C vs C++ we pass a different filename extension so gcc knows which compiler to use
PISTON_FILE_EXT = {
    'python':     'py',
    'java':       'java',
    'c':          'c',
    'cpp':        'cpp',
    'javascript': 'js',
    'php':        'php',
}

def execute_code_api(code, language, input_data=None, expected_output=None):
    piston_url = os.getenv('PISTON_URL', '') # e.g. http://127.0.0.1:2000/api/v2/execute
    
    if piston_url:
        lang_key = language.lower()
        piston_lang = PISTON_LANG_MAP.get(lang_key, lang_key)
        file_ext    = PISTON_FILE_EXT.get(lang_key, 'txt')
        # Java requires the filename to match the public class name
        filename    = 'Main.java' if lang_key == 'java' else f'solution.{file_ext}'
        payload = {
            "language": piston_lang,
            "version": "*",
            "files": [{"name": filename, "content": code}],
            "stdin": input_data or ""
        }
        try:
            response = requests.post(piston_url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                compile_result = result.get('compile', {})
                run_result = result.get('run', {})
                
                output = ""
                status = "Accepted"
                
                if compile_result.get('code', 0) != 0:
                    status = "Compilation Error"
                    output = compile_result.get('output', '')
                elif run_result.get('signal'):
                    status = f"Runtime Error (Signal {run_result.get('signal')})"
                    output = run_result.get('output', '')
                elif run_result.get('code', 0) != 0:
                    status = "Runtime Error"
                    output = run_result.get('output', '')
                else:
                    output = run_result.get('output', '')
                    if expected_output is not None:
                        if output.strip() != expected_output.strip():
                            status = "Wrong Answer"
                
                return {
                    'status': status,
                    'output': output,
                    'time': 0.1, 
                    'memory': 10.0
                }
            else:
                raise Exception(f"Piston Local API Error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            # If local piston is unreachable, fall back to mock
            return {
                'status': 'Accepted (Mock - Local Piston Unreachable)',
                'output': f'Failed to connect to local Piston at {piston_url}. Please ensure Docker container is running.\nError: {str(e)}',
                'time': 0.05,
                'memory': 10.5
            }
    
    # Fallback to Judge0 Logic if PISTON_URL is not set
    language_id = LANGUAGE_MAP.get(language.lower(), 71)
    judge0_key = os.getenv('JUDGE0_KEY', '')
    judge0_host = os.getenv('JUDGE0_HOST', 'judge0-ce.p.rapidapi.com')
    judge0_url = f"https://{judge0_host}"

    if not judge0_key:
        # Fallback to mock if no key is configured, so app doesn't crash in dev
        return {
            'status': 'Accepted (Mock - Configure JUDGE0_KEY in .env)',
            'output': 'Hello World (Mock Output)',
            'time': 0.05,
            'memory': 10.5
        }

    headers = {
        'x-rapidapi-key': judge0_key,
        'x-rapidapi-host': judge0_host,
        'Content-Type': 'application/json'
    }
    payload = {
        "language_id": language_id,
        "source_code": code,
        "stdin": input_data or "",
        "expected_output": expected_output or ""
    }

    response = requests.post(f"{judge0_url}/submissions?base64_encoded=false&wait=true", json=payload, headers=headers)
    if response.status_code in [200, 201]:
        result = response.json()
        status_description = result.get('status', {}).get('description', 'Unknown')
        output = result.get('stdout') or result.get('stderr') or result.get('compile_output') or ""
        return {
            'status': status_description,
            'output': output,
            'time': float(result.get('time') or 0),
            'memory': float(result.get('memory') or 0) / 1024 # KB to MB
        }
    else:
        raise Exception(f"Judge0 API Error: {response.status_code} - {response.text}")

@app.route('/api/code/run', methods=['POST'])
@jwt_required()
def run_code():
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        stdin = data.get('stdin', '')   # Custom stdin from the editor console

        result = execute_code_api(code, language, input_data=stdin)

        return jsonify({
            'status': result['status'],
            'output': result['output'],
            'execution_time': result['time'],
            'memory': result['memory']
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to execute code', 'error': str(e)}), 500

@app.route('/api/code/submit', methods=['POST'])
@jwt_required()
def submit_code():
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        challenge_id = data['challenge_id']
        code = data['code']
        language = data['language']
        
        # Get hidden test cases
        test_cases = TestCase.query.filter_by(challenge_id=challenge_id).all()
        
        final_status = 'Accepted'
        max_time = 0.0
        max_memory = 0.0
        case_results = []
        
        # If no test cases exist, return a descriptive error
        if not test_cases:
            final_status = 'Error'
            case_results.append({
                'test_case_id': 0,
                'is_hidden': False,
                'status': 'Error',
                'time': 0.0,
                'memory': 0.0,
                'input': '',
                'expected': '',
                'actual': 'No test cases are configured for this challenge. Please contact the administrator to add test cases.'
            })
        else:
            for tc in test_cases:
                result = execute_code_api(code, language, tc.input_data, tc.expected_output)
                if result['time'] > max_time: max_time = result['time']
                if result['memory'] > max_memory: max_memory = result['memory']
                
                res_dict = {
                    'test_case_id': tc.id,
                    'is_hidden': tc.is_hidden,
                    'status': result['status'],
                    'time': result['time'],
                    'memory': result['memory']
                }
                
                # Only expose inputs/outputs for public test cases
                if not tc.is_hidden:
                    res_dict['input'] = tc.input_data
                    res_dict['expected'] = tc.expected_output
                    res_dict['actual'] = result['output']
                
                case_results.append(res_dict)
                
                if result['status'] != 'Accepted' and final_status == 'Accepted':
                    final_status = result['status']
        
        submission = CodeSubmission(
            user_id=current_user_id,
            challenge_id=challenge_id,
            submitted_code=code,
            language=language,
            status=final_status,
            execution_time=max_time,
            memory_used=max_memory
        )
        db.session.add(submission)
        db.session.commit()
        
        # Update tournament scoring if active
        try:
            now = datetime.utcnow()
            active_tournaments = Tournament.query.filter(Tournament.starts_at <= now, Tournament.ends_at >= now).all()
            for t in active_tournaments:
                part = TournamentParticipant.query.filter_by(tournament_id=t.id, user_id=current_user_id).first()
                if part:
                    if final_status == 'Accepted':
                        prev_accepted = CodeSubmission.query.filter_by(
                            user_id=current_user_id,
                            challenge_id=challenge_id,
                            status='Accepted'
                        ).filter(CodeSubmission.submitted_at >= t.starts_at, CodeSubmission.submitted_at <= now).count()
                        
                        if prev_accepted <= 1:
                            part.score += 100
                            part.time_taken += int(max_time or 0)
                            db.session.commit()
        except Exception as e_t:
            print(f"Tournament score update warning: {str(e_t)}")

        # Update live combat room progress
        try:
            for rid, room in COMBAT_ROOMS.items():
                if current_user_id in room['players'] and room['challenge_id'] == challenge_id:
                    passed_count = sum(1 for cr in case_results if cr['status'] == 'Accepted')
                    room['players'][current_user_id]['progress'] = passed_count
                    room['players'][current_user_id]['status'] = 'Success' if final_status == 'Accepted' else 'Failed'
                    room['players'][current_user_id]['last_seen'] = datetime.utcnow()
        except Exception as e_c:
            print(f"Combat progress update warning: {str(e_c)}")
            
        return jsonify({
            'message': 'Submission complete',
            'status': final_status,
            'results': case_results
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Submission error: {str(e)}")
        return jsonify({'message': 'Failed to submit code', 'error': str(e)}), 500

# Trace function for execution visualizer
def trace_python_code(code_str, inputs_str=""):
    import sys
    import json
    import io
    
    steps = []
    max_steps = 100
    step_count = 0
    
    # Save standard stdin/stdout
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    
    # Prepare standard input buffer
    sys.stdin = io.StringIO(inputs_str)
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    # Trace function
    def tracer(frame, event, arg):
        nonlocal step_count
        if step_count >= max_steps:
            return None
        if frame.f_code.co_filename != "<string>":
            return tracer
            
        if event == 'line':
            step_count += 1
            local_vars = {}
            for name, val in frame.f_locals.items():
                if name.startswith('__'):
                    continue
                if isinstance(val, (int, float, str, bool, list, dict, set, tuple)):
                    try:
                        if isinstance(val, set):
                            local_vars[name] = list(val)
                        else:
                            json.dumps(val)
                            local_vars[name] = val
                    except:
                        local_vars[name] = str(val)
                else:
                    local_vars[name] = str(val)
            
            steps.append({
                'line': frame.f_lineno,
                'vars': local_vars,
                'event': event
            })
        return tracer

    try:
        compiled = compile(code_str, "<string>", "exec")
        sys.settrace(tracer)
        exec(compiled, {})
        sys.settrace(None)
        stdout_output = new_stdout.getvalue()
    except Exception as exc:
        sys.settrace(None)
        # Safely find line number of exception
        tb = sys.exc_info()[2]
        exc_line = 0
        while tb:
            if tb.tb_frame.f_code.co_filename == "<string>":
                exc_line = tb.tb_lineno
            tb = tb.tb_next
            
        steps.append({
            'line': exc_line,
            'vars': {'error': str(exc)},
            'event': 'exception'
        })
        stdout_output = new_stdout.getvalue()
    finally:
        sys.stdout = old_stdout
        sys.stdin = old_stdin
        
    return steps, stdout_output

# AI Code Reviewer & Hint Assistant
@app.route('/api/challenges/<int:challenge_id>/ai-hint', methods=['POST'])
@jwt_required()
def get_ai_hint(challenge_id):
    try:
        current_user_id = int(get_jwt_identity())
        challenge = CodeChallenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'message': 'Challenge not found'}), 404
            
        data = request.get_json() or {}
        code = data.get('code', '').strip()
        language = data.get('language', 'python').lower()
        
        if not code:
            return jsonify({'message': 'Please write some code before requesting a hint.'}), 400
            
        hint_markdown = ""
        analysis_points = []
        
        loop_count = 0
        if language == 'python':
            import ast
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.For, ast.While)):
                        loop_count += 1
                        for child in ast.walk(node):
                            if child is not node and isinstance(child, (ast.For, ast.While)):
                                loop_count += 1
            except SyntaxError as se:
                analysis_points.append(f"Syntax Error: Line {se.lineno}: {se.msg}")
                hint_markdown = f"### 💡 Syntax Correction Needed\n\nYour code has a syntax error on **line {se.lineno}**: `{se.text.strip() if se.text else ''}` ({se.msg}). Please check brackets, indentation, and colon alignments."
        else:
            loop_count = code.count('for(') + code.count('for (') + code.count('while(') + code.count('while (')

        if not hint_markdown:
            title_lower = challenge.title.lower()
            if 'two sum' in title_lower or 'sum' in title_lower:
                if loop_count >= 2:
                    hint_markdown = (
                        "### 🧠 Complexity Improvement Tip\n\n"
                        "I notice you are using nested loops ($O(N^2)$ brute-force complexity). This will run slowly on large datasets.\n\n"
                        "**Try this:** Can you use a **Hash Map / Dictionary** to store the elements you've seen so far? "
                        "This will let you look up the complement target in $O(1)$ time, reducing total complexity to $O(N)$!"
                    )
                    analysis_points.append("Complexity: O(N^2) detected. HashMap suggestion triggered.")
                else:
                    hint_markdown = (
                        "### 🔍 Algorithm Focus\n\n"
                        "Your loop structure looks optimal. Ensure that for each element `x`, you check if `target - x` is in your records. "
                        "Watch out for index duplicates (you cannot reuse the same element twice)!"
                    )
                    analysis_points.append("O(N) structure verified.")
            elif 'palindrome' in title_lower or 'reverse' in title_lower:
                hint_markdown = (
                    "### 💡 Palindrome Strategy\n\n"
                    "**Two-Pointer Approach:** Have you tried using two pointers? Initialize one at the start (`0`) and one at the end (`len(s) - 1`). "
                    "Move them towards the center, comparing characters at each step.\n\n"
                    "Make sure to clean the string (remove spaces, punctuation, convert to lowercase) first if required by the rules!"
                )
                analysis_points.append("Palindrome helper triggered.")
            elif 'fibonacci' in title_lower or 'stairs' in title_lower:
                is_recursive = code.count(challenge.title.split()[0].lower()) > 1
                if is_recursive and 'memo' not in code and 'dp' not in code:
                    hint_markdown = (
                        "### ⚡ Recursion Overhead Alert\n\n"
                        "Your recursive approach will cause a stack overflow or TLE for large values because it recalculates states repeatedly (Exponential time complexity $O(2^N)$).\n\n"
                        "**Try this:** Add **Memoization** (store results of inputs in a dictionary) or use **Dynamic Programming** "
                        "iteratively with an array/variables to compute results in $O(N)$ time!"
                    )
                    analysis_points.append("Recursive code detected.")
                else:
                    hint_markdown = (
                        "### ⚙️ DP Approach\n\n"
                        "Your Dynamic Programming setup looks solid! Ensure that your base cases (e.g. `n == 0` or `n == 1`) return correct values before the loop begins."
                    )
                    analysis_points.append("DP structure verified.")
            else:
                hint_markdown = (
                    "### 💡 Algorithm Guide\n\n"
                    f"To solve **{challenge.title}**:\n"
                    "1. Double-check your **base cases** (empty inputs, negative bounds, or single element states).\n"
                    "2. Avoid nesting loops if possible; trace your logic using a single loop or a helper hash set to log past matches.\n"
                    "3. Make sure you return the final output array/variable inside the main execution thread."
                )
                analysis_points.append("Default challenge heuristic triggered.")

        hint_log = AIHintLog(
            user_id=current_user_id,
            challenge_id=challenge_id,
            submitted_code=code,
            hint_response=hint_markdown
        )
        db.session.add(hint_log)
        db.session.commit()
        
        return jsonify({
            'hint': hint_markdown,
            'analysis': analysis_points
        }), 200
    except Exception as e:
        print(f"AI Hint error: {str(e)}")
        return jsonify({'message': 'Failed to generate hint', 'error': str(e)}), 500

# Code Execution Visualizer (Line-by-Line Debugger)
@app.route('/api/code/visualize', methods=['POST'])
@jwt_required()
def visualize_code():
    try:
        data = request.get_json() or {}
        code = data.get('code', '').strip()
        inputs = data.get('input', '')
        language = data.get('language', 'python').lower()
        
        if not code:
            return jsonify({'message': 'No code provided'}), 400
            
        if language != 'python':
            lines = code.split('\n')
            mock_steps = []
            for idx, line in enumerate(lines, 1):
                if line.strip() and not line.strip().startswith(('//', '#', '/*')):
                    mock_steps.append({
                        'line': idx,
                        'vars': {'info': 'Visual debugging trace is supported in Python mode. Standard compilation for this language.'},
                        'event': 'line'
                    })
            return jsonify({
                'steps': mock_steps[:30],
                'stdout': 'Compilation succeeded'
            }), 200
            
        steps, stdout_output = trace_python_code(code, inputs)
        return jsonify({
            'steps': steps,
            'stdout': stdout_output
        }), 200
    except Exception as e:
        print(f"Visualization error: {str(e)}")
        return jsonify({'message': 'Failed to visualize code', 'error': str(e)}), 500

# Tournaments / Hackathons API
@app.route('/api/tournaments', methods=['GET'])
@jwt_required()
def get_tournaments():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        is_admin = user and user.role == 'admin'
        
        tournaments = Tournament.query.order_by(Tournament.starts_at.desc()).all()
        now = datetime.utcnow()
        results = []
        for t in tournaments:
            registered = TournamentParticipant.query.filter_by(tournament_id=t.id, user_id=current_user_id).first() is not None
            
            # Determine effective status: respect manual override if set
            if t.status and t.status not in ('Auto', ''):
                status = t.status
            else:
                status = 'Active' if t.starts_at <= now <= t.ends_at else ('Upcoming' if now < t.starts_at else 'Completed')
                
            # Non-admins should only see Active tournaments
            if not is_admin and status != 'Active':
                continue
                
            results.append({
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'starts_at': t.starts_at.isoformat(),
                'ends_at': t.ends_at.isoformat(),
                'status': status,
                'raw_status': t.status or 'Auto',
                'creator': t.creator.username if t.creator else 'Admin',
                'registered': registered,
                'participant_count': len(t.participants)
            })
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'message': 'Failed to load tournaments', 'error': str(e)}), 500

@app.route('/api/tournaments', methods=['POST'])
@admin_required
def create_tournament():
    try:
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        starts_at_str = data.get('starts_at')
        ends_at_str = data.get('ends_at')
        status = data.get('status', 'Auto')
        
        if not title or not starts_at_str or not ends_at_str:
            return jsonify({'message': 'Missing title, starts_at, or ends_at fields'}), 400
            
        starts_at = datetime.fromisoformat(starts_at_str.replace('Z', ''))
        ends_at = datetime.fromisoformat(ends_at_str.replace('Z', ''))
        
        current_admin_id = int(get_jwt_identity())
        
        t = Tournament(
            title=title,
            description=description,
            starts_at=starts_at,
            ends_at=ends_at,
            created_by=current_admin_id,
            status=status
        )
        db.session.add(t)
        db.session.commit()
        return jsonify({'message': 'Tournament created successfully', 'id': t.id}), 201
    except Exception as e:
        return jsonify({'message': 'Failed to create tournament', 'error': str(e)}), 500

@app.route('/api/tournaments/<int:id>', methods=['PUT'])
@admin_required
def update_tournament(id):
    try:
        t = Tournament.query.get(id)
        if not t:
            return jsonify({'message': 'Tournament not found'}), 404
            
        data = request.get_json() or {}
        
        if 'title' in data:
            t.title = data['title'].strip()
        if 'description' in data:
            t.description = data['description'].strip()
        if 'starts_at' in data:
            starts_at_str = data['starts_at']
            t.starts_at = datetime.fromisoformat(starts_at_str.replace('Z', ''))
        if 'ends_at' in data:
            ends_at_str = data['ends_at']
            t.ends_at = datetime.fromisoformat(ends_at_str.replace('Z', ''))
        if 'status' in data:
            t.status = data['status']
            
        db.session.commit()
        return jsonify({'message': 'Tournament updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to update tournament', 'error': str(e)}), 500

@app.route('/api/tournaments/<int:id>', methods=['DELETE'])
@admin_required
def delete_tournament(id):
    try:
        t = Tournament.query.get(id)
        if not t:
            return jsonify({'message': 'Tournament not found'}), 404
        db.session.delete(t)
        db.session.commit()
        return jsonify({'message': 'Tournament deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to delete tournament', 'error': str(e)}), 500

@app.route('/api/tournaments/<int:id>/register', methods=['POST'])
@jwt_required()
def register_tournament(id):
    try:
        current_user_id = int(get_jwt_identity())
        t = Tournament.query.get(id)
        if not t:
            return jsonify({'message': 'Tournament not found'}), 404
            
        now = datetime.utcnow()
        if now > t.ends_at:
            return jsonify({'message': 'Tournament has already ended'}), 400
            
        existing = TournamentParticipant.query.filter_by(tournament_id=id, user_id=current_user_id).first()
        if existing:
            return jsonify({'message': 'You are already registered'}), 200
            
        tp = TournamentParticipant(tournament_id=id, user_id=current_user_id)
        db.session.add(tp)
        db.session.commit()
        return jsonify({'message': 'Registered successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to register', 'error': str(e)}), 500

@app.route('/api/tournaments/<int:id>/leaderboard', methods=['GET'])
@jwt_required()
def get_tournament_leaderboard(id):
    try:
        t = Tournament.query.get(id)
        if not t:
            return jsonify({'message': 'Tournament not found'}), 404
            
        # Only show students who completed the tournament, limited to top 10
        participants = TournamentParticipant.query.filter_by(tournament_id=id, completed=True).order_by(
            desc(TournamentParticipant.score),
            TournamentParticipant.time_taken
        ).limit(10).all()
        
        results = []
        for idx, p in enumerate(participants, 1):
            results.append({
                'rank': idx,
                'username': p.user.username if p.user else f"User {p.user_id}",
                'score': p.score,
                'time_taken': p.time_taken,
                'elo': p.user.elo_rating if p.user else 1000
            })
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'message': 'Failed to load leaderboard', 'error': str(e)}), 500

@app.route('/api/tournaments/<int:id>/questions', methods=['GET'])
@jwt_required()
def get_tournament_questions(id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        is_admin = user and user.role == 'admin'
        
        t = Tournament.query.get(id)
        if not t:
            return jsonify({'message': 'Tournament not found'}), 404
            
        # Check registration for student
        if not is_admin:
            tp = TournamentParticipant.query.filter_by(tournament_id=id, user_id=current_user_id).first()
            if not tp:
                return jsonify({'message': 'You must be registered to the tournament to access its questions'}), 403
                
        t_qs = TournamentQuestion.query.filter_by(tournament_id=id).all()
        results = []
        for t_q in t_qs:
            q_info = {
                'id': t_q.id,
                'question_type': t_q.question_type,
                'submitted': False,
                'points': 0
            }
            
            if t_q.question_type == 'code' and t_q.challenge:
                ch = t_q.challenge
                q_info.update({
                    'challenge_id': ch.id,
                    'title': ch.title,
                    'description': ch.description,
                    'difficulty': ch.difficulty,
                    'time_limit': ch.time_limit,
                    'memory_limit': ch.memory_limit
                })
                # Check student's submission status
                if not is_admin:
                    sub = CodeSubmission.query.filter_by(
                        user_id=current_user_id,
                        challenge_id=ch.id,
                        status='Accepted'
                    ).filter(CodeSubmission.submitted_at >= t.starts_at, CodeSubmission.submitted_at <= t.ends_at).first()
                    if sub:
                        q_info['submitted'] = True
                        
            elif t_q.question_type == 'quiz' and t_q.question:
                q = t_q.question
                q_info.update({
                    'question_id': q.id,
                    'question': q.question,
                    'option_a': q.option_a,
                    'option_b': q.option_b,
                    'option_c': q.option_c,
                    'option_d': q.option_d,
                    'points': q.points
                })
                if is_admin:
                    q_info['correct_answer'] = q.correct_answer
                    
                # Check student's submission status
                if not is_admin:
                    sub = TournamentSubmission.query.filter_by(
                        tournament_id=id,
                        user_id=current_user_id,
                        question_type='quiz',
                        question_id=q.id
                    ).first()
                    if sub:
                        q_info['submitted'] = True
                        q_info['selected_answer'] = sub.selected_answer
                        
            results.append(q_info)
            
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'message': 'Failed to load tournament questions', 'error': str(e)}), 500

def get_or_create_tournament_placeholders(admin_user_id):
    # Find or create Subject
    sub = Subject.query.filter_by(name='Tournament Events').first()
    if not sub:
        sub = Subject(name='Tournament Events', description='Placeholder for tournament custom questions', created_by=admin_user_id)
        db.session.add(sub)
        db.session.flush()
        
    # Find or create Chapter
    chap = Chapter.query.filter_by(subject_id=sub.id, name='Tournament Questions').first()
    if not chap:
        chap = Chapter(name='Tournament Questions', description='Chapter for tournament questions', subject_id=sub.id, created_by=admin_user_id)
        db.session.add(chap)
        db.session.flush()
        
    # Find or create Quiz
    quiz = Quiz.query.filter_by(chapter_id=chap.id, title='Tournament MCQ Questions').first()
    if not quiz:
        quiz = Quiz(title='Tournament MCQ Questions', description='Quiz containing custom tournament questions', chapter_id=chap.id, created_by=admin_user_id)
        db.session.add(quiz)
        db.session.flush()
        
    db.session.commit()
    return chap.id, quiz.id

@app.route('/api/tournaments/<int:id>/custom-question', methods=['POST'])
@admin_required
def create_tournament_custom_question(id):
    try:
        t = Tournament.query.get(id)
        if not t:
            return jsonify({'message': 'Tournament not found'}), 404
            
        data = request.get_json() or {}
        question_type = data.get('question_type')
        if not question_type:
            return jsonify({'message': 'Missing question_type'}), 400
            
        current_admin_id = int(get_jwt_identity())
        
        # Get or create placeholder chapter and quiz for custom tournament questions
        placeholder_chap_id, placeholder_quiz_id = get_or_create_tournament_placeholders(current_admin_id)
        
        if question_type == 'quiz':
            question_text = data.get('question', '').strip()
            option_a = data.get('option_a', '').strip()
            option_b = data.get('option_b', '').strip()
            option_c = data.get('option_c', '').strip()
            option_d = data.get('option_d', '').strip()
            correct_answer = data.get('correct_answer', '').strip().upper()
            points = int(data.get('points', 1))
            
            if not question_text or not option_a or not option_b or not option_c or not option_d or not correct_answer:
                return jsonify({'message': 'Missing required MCQ quiz fields'}), 400
                
            if correct_answer not in ('A', 'B', 'C', 'D'):
                return jsonify({'message': 'Correct answer must be A, B, C, or D'}), 400
                
            q = Question(
                quiz_id=placeholder_quiz_id,
                question=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer,
                points=points
            )
            db.session.add(q)
            db.session.flush()
            
            t_q = TournamentQuestion(
                tournament_id=id,
                question_type='quiz',
                question_id=q.id
            )
            db.session.add(t_q)
            db.session.commit()
            return jsonify({'message': 'Custom Quiz MCQ created and linked successfully', 'id': t_q.id}), 201
            
        elif question_type == 'code':
            title = data.get('title', '').strip()
            description = data.get('description', '').strip()
            difficulty = data.get('difficulty', 'Medium').strip()
            time_limit = int(data.get('time_limit', 2))
            memory_limit = int(data.get('memory_limit', 256))
            test_cases = data.get('test_cases', [])
            
            if not title or not description:
                return jsonify({'message': 'Missing title or description for coding challenge'}), 400
                
            ch = CodeChallenge(
                title=title,
                description=description,
                chapter_id=placeholder_chap_id,
                difficulty=difficulty,
                time_limit=time_limit,
                memory_limit=memory_limit,
                created_by=current_admin_id
            )
            db.session.add(ch)
            db.session.flush()
            
            # Add test cases
            for tc in test_cases:
                input_data = tc.get('input_data', '')
                expected_output = tc.get('expected_output', '')
                is_hidden = bool(tc.get('is_hidden', False))
                
                tc_obj = TestCase(
                    challenge_id=ch.id,
                    input_data=input_data,
                    expected_output=expected_output,
                    is_hidden=is_hidden
                )
                db.session.add(tc_obj)
            
            # Set up default starter templates
            tpl_py = ChallengeTemplate(
                challenge_id=ch.id,
                language='python',
                template_code='# Write your Python solution here\n'
            )
            tpl_js = ChallengeTemplate(
                challenge_id=ch.id,
                language='javascript',
                template_code='// Write your JavaScript solution here\n'
            )
            db.session.add(tpl_py)
            db.session.add(tpl_js)
            
            t_q = TournamentQuestion(
                tournament_id=id,
                question_type='code',
                challenge_id=ch.id
            )
            db.session.add(t_q)
            db.session.commit()
            return jsonify({'message': 'Custom Coding Challenge created and linked successfully', 'id': t_q.id}), 201
            
        else:
            return jsonify({'message': 'Invalid question_type'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create custom question', 'error': str(e)}), 500

@app.route('/api/tournaments/<int:id>/questions', methods=['POST'])
@admin_required
def add_tournament_question(id):
    try:
        data = request.get_json() or {}
        question_type = data.get('question_type')
        q_id = data.get('question_id')
        
        if not question_type or not q_id:
            return jsonify({'message': 'Missing question_type or question_id'}), 400
            
        if question_type == 'code':
            existing = TournamentQuestion.query.filter_by(tournament_id=id, question_type='code', challenge_id=q_id).first()
            if existing:
                return jsonify({'message': 'This coding challenge is already added to this tournament'}), 400
            t_q = TournamentQuestion(tournament_id=id, question_type='code', challenge_id=q_id)
        elif question_type == 'quiz':
            existing = TournamentQuestion.query.filter_by(tournament_id=id, question_type='quiz', question_id=q_id).first()
            if existing:
                return jsonify({'message': 'This quiz question is already added to this tournament'}), 400
            t_q = TournamentQuestion(tournament_id=id, question_type='quiz', question_id=q_id)
        else:
            return jsonify({'message': 'Invalid question_type'}), 400
            
        db.session.add(t_q)
        db.session.commit()
        return jsonify({'message': 'Question added to tournament successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to add question', 'error': str(e)}), 500

@app.route('/api/tournaments/<int:id>/questions/<int:t_q_id>', methods=['DELETE'])
@admin_required
def remove_tournament_question(id, t_q_id):
    try:
        t_q = TournamentQuestion.query.filter_by(tournament_id=id, id=t_q_id).first()
        if not t_q:
            return jsonify({'message': 'Question link not found'}), 404
            
        db.session.delete(t_q)
        db.session.commit()
        return jsonify({'message': 'Question removed from tournament successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to remove question', 'error': str(e)}), 500

@app.route('/api/tournaments/<int:id>/submit-quiz-answer', methods=['POST'])
@jwt_required()
def submit_tournament_quiz_answer(id):
    try:
        current_user_id = int(get_jwt_identity())
        t = Tournament.query.get(id)
        if not t:
            return jsonify({'message': 'Tournament not found'}), 404
            
        tp = TournamentParticipant.query.filter_by(tournament_id=id, user_id=current_user_id).first()
        if not tp:
            return jsonify({'message': 'You are not registered to this tournament'}), 403
            
        now = datetime.utcnow()
        if t.status and t.status not in ('Auto', ''):
            status = t.status
        else:
            status = 'Active' if t.starts_at <= now <= t.ends_at else ('Upcoming' if now < t.starts_at else 'Completed')
            
        if status != 'Active':
            return jsonify({'message': 'Tournament is not currently active'}), 400
            
        if tp.completed:
            return jsonify({'message': 'You have already completed this tournament'}), 400
            
        data = request.get_json() or {}
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        
        if not question_id or not selected_answer:
            return jsonify({'message': 'Missing question_id or selected_answer'}), 400
            
        t_q = TournamentQuestion.query.filter_by(tournament_id=id, question_type='quiz', question_id=question_id).first()
        if not t_q:
            return jsonify({'message': 'This question is not part of this tournament'}), 400
            
        existing_sub = TournamentSubmission.query.filter_by(
            tournament_id=id,
            user_id=current_user_id,
            question_type='quiz',
            question_id=question_id
        ).first()
        
        q = t_q.question
        is_correct = (q.correct_answer.upper() == selected_answer.upper())
        
        if existing_sub:
            existing_sub.selected_answer = selected_answer
            existing_sub.is_correct = is_correct
            existing_sub.submitted_at = datetime.utcnow()
        else:
            sub = TournamentSubmission(
                tournament_id=id,
                user_id=current_user_id,
                question_type='quiz',
                question_id=question_id,
                selected_answer=selected_answer,
                is_correct=is_correct
            )
            db.session.add(sub)
            
        db.session.commit()
        return jsonify({'message': 'Answer submitted successfully', 'is_correct': is_correct}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to submit answer', 'error': str(e)}), 500

@app.route('/api/tournaments/<int:id>/complete', methods=['POST'])
@jwt_required()
def complete_tournament(id):
    try:
        current_user_id = int(get_jwt_identity())
        t = Tournament.query.get(id)
        if not t:
            return jsonify({'message': 'Tournament not found'}), 404
            
        tp = TournamentParticipant.query.filter_by(tournament_id=id, user_id=current_user_id).first()
        if not tp:
            return jsonify({'message': 'You are not registered to this tournament'}), 403
            
        if tp.completed:
            return jsonify({'message': 'You have already completed this tournament'}), 400
            
        t_qs = TournamentQuestion.query.filter_by(tournament_id=id).all()
        total_score = 0
        total_time = 0
        
        now = datetime.utcnow()
        
        for t_q in t_qs:
            if t_q.question_type == 'quiz' and t_q.question:
                sub = TournamentSubmission.query.filter_by(
                    tournament_id=id,
                    user_id=current_user_id,
                    question_type='quiz',
                    question_id=t_q.question_id,
                    is_correct=True
                ).first()
                if sub:
                    total_score += (t_q.question.points or 1) * 10
            elif t_q.question_type == 'code' and t_q.challenge:
                sub = CodeSubmission.query.filter_by(
                    user_id=current_user_id,
                    challenge_id=t_q.challenge_id,
                    status='Accepted'
                ).filter(CodeSubmission.submitted_at >= t.starts_at, CodeSubmission.submitted_at <= t.ends_at).first()
                if sub:
                    total_score += 100
                    total_time += int(sub.execution_time or 0)
                    
        tp.completed = True
        tp.completed_at = now
        tp.score = total_score
        
        start_time = max(t.starts_at, tp.registered_at)
        duration = int((now - start_time).total_seconds())
        tp.time_taken = duration if duration > 0 else 0
        
        db.session.commit()
        return jsonify({
            'message': 'Tournament completed successfully!',
            'score': total_score,
            'time_taken': tp.time_taken
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to complete tournament', 'error': str(e)}), 500

@app.route('/api/admin/questions/all', methods=['GET'])
@admin_required
def get_all_questions():
    try:
        questions = Question.query.all()
        results = []
        for q in questions:
            results.append({
                'id': q.id,
                'question': q.question,
                'quiz_title': q.quiz.title if q.quiz else 'Unknown Quiz'
              })
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'message': 'Failed to load questions', 'error': str(e)}), 500

# Combat Rooms State dictionary
COMBAT_ROOMS = {}

@app.route('/api/combat/room/<room_id>/status', methods=['GET'])
@jwt_required()
def get_combat_status(room_id):
    try:
        current_user_id = int(get_jwt_identity())
        if room_id not in COMBAT_ROOMS:
            return jsonify({'message': 'Combat room not found or expired'}), 404
            
        room = COMBAT_ROOMS[room_id]
        if current_user_id in room['players']:
            room['players'][current_user_id]['last_seen'] = datetime.utcnow()
            
        stale_rooms = [rid for rid, rinfo in COMBAT_ROOMS.items() if (datetime.utcnow() - rinfo['matched_at']).total_seconds() > 900]
        for rid in stale_rooms:
            if rid in COMBAT_ROOMS:
                del COMBAT_ROOMS[rid]
                
        players_info = {}
        for pid, pinfo in room['players'].items():
            players_info[pid] = {
                'username': pinfo['username'],
                'progress': pinfo['progress'],
                'status': pinfo['status'],
                'active': (datetime.utcnow() - pinfo['last_seen']).total_seconds() < 10
            }
            
        return jsonify({
            'room_id': room_id,
            'challenge_id': room['challenge_id'],
            'players': players_info,
            'time_elapsed': int((datetime.utcnow() - room['matched_at']).total_seconds())
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch combat status', 'error': str(e)}), 500

@app.route('/api/combat/room/<room_id>/progress', methods=['POST'])
@jwt_required()
def update_combat_progress(room_id):
    try:
        current_user_id = int(get_jwt_identity())
        if room_id not in COMBAT_ROOMS:
            return jsonify({'message': 'Combat room not found'}), 404
            
        data = request.get_json() or {}
        progress = int(data.get('progress', 0))
        status = data.get('status', 'Coding')
        
        room = COMBAT_ROOMS[room_id]
        if current_user_id in room['players']:
            room['players'][current_user_id]['progress'] = progress
            room['players'][current_user_id]['status'] = status
            room['players'][current_user_id]['last_seen'] = datetime.utcnow()
            
        return jsonify({'message': 'Progress updated'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to update progress', 'error': str(e)}), 500

# --- NEW QUIZ APP ENHANCEMENT ROUTES ---

@app.route('/api/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        # Fetch chapters
        chapters = Chapter.query.filter_by(is_active=True).all()
        if not chapters:
            return jsonify([]), 200
            
        # Get all completed quiz attempts for the current user
        completed_quiz_ids = {
            att.quiz_id for att in QuizAttempt.query.filter_by(
                user_id=current_user_id
            ).filter(QuizAttempt.completed_at.isnot(None)).all()
        }

        # 1. Fetch all quiz attempts in database to build vectors
        all_attempts = QuizAttempt.query.filter(QuizAttempt.completed_at.isnot(None)).all()
        
        # Build user-chapter scores map: {user_id: {chapter_id: [scores]}}
        user_chapter_scores = {}
        for att in all_attempts:
            uid = att.user_id
            # Get chapter_id for this quiz
            quiz = Quiz.query.get(att.quiz_id)
            if not quiz or not quiz.is_active:
                continue
            cid = quiz.chapter_id
            
            if uid not in user_chapter_scores:
                user_chapter_scores[uid] = {}
            if cid not in user_chapter_scores[uid]:
                user_chapter_scores[uid][cid] = []
                
            pct = (att.score / att.total_questions * 100) if att.total_questions > 0 else 0.0
            user_chapter_scores[uid][cid].append(pct)
            
        # Convert list of scores to average score: {user_id: {chapter_id: avg_score}}
        user_profiles = {}
        for uid, c_scores in user_chapter_scores.items():
            user_profiles[uid] = {cid: sum(scores)/len(scores) for cid, scores in c_scores.items()}
            
        # 2. Get current user profile
        current_profile = user_profiles.get(current_user_id, {})
        
        # If current user has no history (cold start), fallback to Elo-based prediction
        if not current_profile:
            # ELO fallback (existing flow zone recommendation)
            R_U = user.elo_rating or 1000
            recommendations = []
            for chapter in chapters:
                quizzes = Quiz.query.filter_by(chapter_id=chapter.id, is_active=True).all()
                uncompleted_quizzes = [q for q in quizzes if q.id not in completed_quiz_ids]
                if not uncompleted_quizzes:
                    continue
                recommended_quiz = min(uncompleted_quizzes, key=lambda q: abs((q.elo_rating or 1000) - R_U))
                R_Q = recommended_quiz.elo_rating or 1000
                E_U = 1.0 / (1.0 + 10.0 ** ((R_Q - R_U) / 400.0))
                proficiency = E_U * 100.0
                
                status = 'Optimal Challenge (Flow Zone)' if E_U >= 0.50 else 'Advanced Challenge'
                
                recommendations.append({
                    'chapter_id': chapter.id,
                    'chapter_name': chapter.name,
                    'subject_name': chapter.subject.name if chapter.subject else 'General',
                    'proficiency': round(proficiency, 2),
                    'status': f"{status} (Success Prediction: {int(round(proficiency))}% | ELO Rank)",
                    'recommended_quiz': {
                        'id': recommended_quiz.id,
                        'title': recommended_quiz.title,
                        'description': recommended_quiz.description or '',
                        'time_limit': recommended_quiz.time_limit
                    }
                })
            recommendations.sort(key=lambda x: abs(x['proficiency'] - 65.0))
            return jsonify(recommendations[:3]), 200

        # 3. Collaborative Filtering via Cosine Similarity
        import math
        def get_cosine_similarity(v1, v2):
            # Both v1, v2 are dictionaries of {chapter_id: score}
            common_keys = set(v1.keys()).intersection(set(v2.keys()))
            if not common_keys:
                return 0.0
                
            dot_product = sum(v1[k] * v2[k] for k in common_keys)
            norm_v1 = math.sqrt(sum(val ** 2 for val in v1.values()))
            norm_v2 = math.sqrt(sum(val ** 2 for val in v2.values()))
            
            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0
            return dot_product / (norm_v1 * norm_v2)

        # Calculate similarity with other users
        similarities = []
        for other_user_id, other_profile in user_profiles.items():
            if other_user_id == current_user_id:
                continue
            sim = get_cosine_similarity(current_profile, other_profile)
            if sim > 0:
                similarities.append((other_user_id, sim))
                
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_neighbors = similarities[:5]  # Top 5 similar users
        
        # 4. Predict scores for unattempted chapters
        recommendations = []
        for chapter in chapters:
            # Skip if user already completed this chapter
            if chapter.id in current_profile:
                continue
                
            quizzes = Quiz.query.filter_by(chapter_id=chapter.id, is_active=True).all()
            uncompleted_quizzes = [q for q in quizzes if q.id not in completed_quiz_ids]
            if not uncompleted_quizzes:
                continue
                
            # Predict score using weighted average of neighbors
            total_sim = 0.0
            weighted_score_sum = 0.0
            for neighbor_id, sim in top_neighbors:
                neighbor_profile = user_profiles[neighbor_id]
                if chapter.id in neighbor_profile:
                    total_sim += sim
                    weighted_score_sum += sim * neighbor_profile[chapter.id]
                    
            if total_sim > 0:
                predicted_score = weighted_score_sum / total_sim
            else:
                # Fallback to Elo expected score if neighbors haven't done it
                recommended_quiz = uncompleted_quizzes[0]
                R_Q = recommended_quiz.elo_rating or 1000
                R_U = user.elo_rating or 1000
                E_U = 1.0 / (1.0 + 10.0 ** ((R_Q - R_U) / 400.0))
                predicted_score = E_U * 100.0
                
            # Find the best recommended quiz inside the chapter closest to user ELO
            R_U = user.elo_rating or 1000
            recommended_quiz = min(uncompleted_quizzes, key=lambda q: abs((q.elo_rating or 1000) - R_U))
            
            status = 'Recommended Choice'
            if predicted_score >= 80:
                status = 'High Success Probability'
            elif predicted_score >= 50:
                status = 'Growth Zone (Flow)'
            else:
                status = 'Stretch Challenge'
                
            recommendations.append({
                'chapter_id': chapter.id,
                'chapter_name': chapter.name,
                'subject_name': chapter.subject.name if chapter.subject else 'General',
                'proficiency': round(predicted_score, 2),
                'status': f"{status} (Predicted Score: {int(round(predicted_score))}% via Cosine similarity)",
                'recommended_quiz': {
                    'id': recommended_quiz.id,
                    'title': recommended_quiz.title,
                    'description': recommended_quiz.description or '',
                    'time_limit': recommended_quiz.time_limit
                }
            })
            
        # If we have no similarities/recommendations, fallback to basic Elo
        if not recommendations:
            R_U = user.elo_rating or 1000
            for chapter in chapters:
                quizzes = Quiz.query.filter_by(chapter_id=chapter.id, is_active=True).all()
                uncompleted_quizzes = [q for q in quizzes if q.id not in completed_quiz_ids]
                if not uncompleted_quizzes:
                    continue
                recommended_quiz = min(uncompleted_quizzes, key=lambda q: abs((q.elo_rating or 1000) - R_U))
                R_Q = recommended_quiz.elo_rating or 1000
                E_U = 1.0 / (1.0 + 10.0 ** ((R_Q - R_U) / 400.0))
                proficiency = E_U * 100.0
                recommendations.append({
                    'chapter_id': chapter.id,
                    'chapter_name': chapter.name,
                    'subject_name': chapter.subject.name if chapter.subject else 'General',
                    'proficiency': round(proficiency, 2),
                    'status': f"Optimal Challenge (Success: {int(round(proficiency))}%)",
                    'recommended_quiz': {
                        'id': recommended_quiz.id,
                        'title': recommended_quiz.title,
                        'description': recommended_quiz.description or '',
                        'time_limit': recommended_quiz.time_limit
                    }
                })
                
        # Sort recommendations: closest to 65% (Optimal flow zone) first
        recommendations.sort(key=lambda x: abs(x['proficiency'] - 65.0))
        return jsonify(recommendations[:3]), 200
        
    except Exception as e:
        print(f"Recommendations error: {str(e)}")
        return jsonify({'message': 'Failed to get recommendations', 'error': str(e)}), 500

@app.route('/api/quizzes/<int:quiz_id>/comments', methods=['GET'])
@jwt_required()
def get_quiz_comments(quiz_id):
    try:
        from models import Comment
        comments = Comment.query.filter_by(quiz_id=quiz_id).order_by(desc(Comment.created_at)).all()
        return jsonify([{
            'id': c.id,
            'content': c.content,
            'created_at': c.created_at.isoformat(),
            'user': {
                'id': c.user.id,
                'username': c.user.username
            }
        } for c in comments]), 200
    except Exception as e:
        return jsonify({'message': 'Failed to get comments', 'error': str(e)}), 500

@app.route('/api/quizzes/<int:quiz_id>/comments', methods=['POST'])
@jwt_required()
def add_quiz_comment(quiz_id):
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'message': 'Comment content is required'}), 400
            
        from models import Comment
        new_comment = Comment(
            quiz_id=quiz_id,
            user_id=current_user_id,
            content=data['content']
        )
        db.session.add(new_comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': {
                'id': new_comment.id,
                'content': new_comment.content,
                'created_at': new_comment.created_at.isoformat(),
                'user': {
                    'id': new_comment.user.id,
                    'username': new_comment.user.username
                }
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add comment', 'error': str(e)}), 500

@app.route('/api/user/analytics', methods=['GET'])
@jwt_required()
def get_user_analytics():
    try:
        current_user_id = int(get_jwt_identity())
        target_username = request.args.get('username')
        
        if target_username:
            user = User.query.filter_by(username=target_username).first()
        else:
            user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        # 1. Subject-wise proficiency (Radar chart)
        subjects = Subject.query.filter_by(is_active=True).all()
        radar_labels = []
        radar_data = []
        
        for subject in subjects:
            chapters = Chapter.query.filter_by(subject_id=subject.id, is_active=True).all()
            if not chapters:
                continue
            
            chapter_ids = [c.id for c in chapters]
            quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()
            if not quizzes:
                continue
            
            quiz_ids = [q.id for q in quizzes]
            attempts = QuizAttempt.query.filter(
                QuizAttempt.user_id == user.id,
                QuizAttempt.quiz_id.in_(quiz_ids),
                QuizAttempt.completed_at.isnot(None)
            ).all()
            
            avg_score = 0.0
            if attempts:
                total_pct = sum((a.score / a.total_questions * 100) if a.total_questions > 0 else 0 for a in attempts)
                avg_score = total_pct / len(attempts)
            
            radar_labels.append(subject.name)
            radar_data.append(round(avg_score, 2))
            
        # 2. Elo over time (Line chart)
        elo_history_records = UserEloHistory.query.filter_by(user_id=user.id).order_by(UserEloHistory.recorded_at).all()
        
        elo_timeline_labels = []
        elo_timeline_values = []
        
        # Add initial starting Elo rating
        elo_timeline_labels.append("Initial")
        elo_timeline_values.append(1000)
        
        for record in elo_history_records:
            elo_timeline_labels.append(record.recorded_at.date().isoformat())
            elo_timeline_values.append(record.elo_rating)
            
        elo_timeline_labels = elo_timeline_labels[-10:]
        elo_timeline_values = elo_timeline_values[-10:]
        
        # 3. Badges details
        from models import Badge
        all_badges = Badge.query.all()
        unlocked_badge_ids = {ub.badge_id for ub in user.badges}
        
        badge_list = []
        for badge in all_badges:
            badge_list.append({
                'id': badge.id,
                'name': badge.name,
                'description': badge.description,
                'icon_url': badge.icon_url,
                'unlocked': badge.id in unlocked_badge_ids
            })
            
        # 4. Leaderboard (Top 10 users by Elo)
        top_users = User.query.order_by(desc(User.elo_rating)).limit(10).all()
        leaderboard = [{
            'username': u.username,
            'xp': u.xp,
            'streak_count': u.streak_count,
            'level': (u.xp // 100) + 1,
            'elo_rating': u.elo_rating or 1000
        } for u in top_users]
        
        # Rank Tier
        elo = user.elo_rating or 1000
        if elo < 1100:
            rank_tier = "Bronze"
        elif elo < 1300:
            rank_tier = "Silver"
        elif elo < 1600:
            rank_tier = "Gold"
        else:
            rank_tier = "Platinum"
            
        return jsonify({
            'username': user.username,
            'xp': user.xp,
            'streak_count': user.streak_count,
            'level': (user.xp // 100) + 1,
            'elo_rating': elo,
            'rank_tier': rank_tier,
            'gender': user.gender,
            'profile_pic': user.profile_pic,
            'radar_chart': {
                'labels': radar_labels,
                'datasets': [{
                    'label': 'Average Score (%)',
                    'data': radar_data
                }]
            },
            'line_chart': {
                'labels': elo_timeline_labels,
                'data': elo_timeline_values
            },
            'badges': badge_list,
            'leaderboard': leaderboard
        }), 200
        
    except Exception as e:
        print(f"Analytics error: {str(e)}")
        return jsonify({'message': 'Failed to get analytics', 'error': str(e)}), 500

@app.route('/api/admin/impersonate/<int:user_id>', methods=['POST'])
@admin_required
def impersonate_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        if user.role == 'admin':
            return jsonify({'message': 'Cannot impersonate an admin'}), 400
            
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            },
            'impersonating': True
        }), 200
    except Exception as e:
        return jsonify({'message': 'Failed to impersonate user', 'error': str(e)}), 500

# Fuzzy Search (Levenshtein Distance)
@app.route('/api/search', methods=['GET'])
@jwt_required()
def search_content():
    try:
        query = request.args.get('q', '').strip().lower()
        if not query:
            return jsonify({'subjects': [], 'quizzes': [], 'challenges': []}), 200
            
        def get_levenshtein(s1, s2):
            m, n = len(s1), len(s2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            for i in range(m + 1): dp[i][0] = i
            for j in range(n + 1): dp[0][j] = j
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    cost = 0 if s1[i-1] == s2[j-1] else 1
                    dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + cost)
            return dp[m][n]

        subjects = Subject.query.filter_by(is_active=True).all()
        quizzes = Quiz.query.filter_by(is_active=True).all()
        challenges = CodeChallenge.query.filter_by(is_active=True).all()
        
        subject_results = []
        for s in subjects:
            name_lower = s.name.lower()
            if query in name_lower:
                dist = 0
            else:
                dist = get_levenshtein(query, name_lower)
            if dist <= max(3, len(name_lower) // 2) or query in name_lower:
                subject_results.append({
                    'id': s.id,
                    'name': s.name,
                    'description': s.description,
                    'distance': dist
                })
        
        quiz_results = []
        for q in quizzes:
            title_lower = q.title.lower()
            if query in title_lower:
                dist = 0
            else:
                dist = get_levenshtein(query, title_lower)
            if dist <= max(3, len(title_lower) // 2) or query in title_lower:
                quiz_results.append({
                    'id': q.id,
                    'title': q.title,
                    'description': q.description,
                    'distance': dist
                })
                
        challenge_results = []
        for c in challenges:
            title_lower = c.title.lower()
            if query in title_lower:
                dist = 0
            else:
                dist = get_levenshtein(query, title_lower)
            if dist <= max(3, len(title_lower) // 2) or query in title_lower:
                challenge_results.append({
                    'id': c.id,
                    'title': c.title,
                    'difficulty': c.difficulty,
                    'distance': dist
                })
                
        subject_results.sort(key=lambda x: x['distance'])
        quiz_results.sort(key=lambda x: x['distance'])
        challenge_results.sort(key=lambda x: x['distance'])
        
        return jsonify({
            'subjects': subject_results[:5],
            'quizzes': quiz_results[:5],
            'challenges': challenge_results[:5]
        }), 200
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'message': 'Search failed', 'error': str(e)}), 500

# Plagiarism Detection (AST Winnowing)
@app.route('/api/admin/challenges/<int:challenge_id>/plagiarism', methods=['GET'])
@admin_required
def check_plagiarism(challenge_id):
    try:
        import ast
        import hashlib
        
        submissions = CodeSubmission.query.filter_by(challenge_id=challenge_id).all()
        if len(submissions) < 2:
            return jsonify({'message': 'Need at least 2 submissions to run plagiarism check', 'results': []}), 200
            
        def get_ast_tokens(code_str):
            try:
                tree = ast.parse(code_str)
            except SyntaxError:
                return code_str.split()
            tokens = []
            for node in ast.walk(tree):
                tokens.append(type(node).__name__)
            return tokens

        def get_fingerprints(tokens, k=5, w=4):
            kgrams = []
            for i in range(len(tokens) - k + 1):
                kgram = "".join(tokens[i:i+k])
                h = int(hashlib.md5(kgram.encode('utf-8')).hexdigest()[:8], 16)
                kgrams.append(h)
            if not kgrams:
                return set()
            fingerprints = set()
            for i in range(len(kgrams) - w + 1):
                window = kgrams[i:i+w]
                min_val = min(window)
                fingerprints.add(min_val)
            return fingerprints

        student_fingerprints = {}
        for sub in submissions:
            if sub.user_id in student_fingerprints:
                continue
            tokens = get_ast_tokens(sub.submitted_code)
            fingerprints = get_fingerprints(tokens)
            if fingerprints:
                student_fingerprints[sub.user_id] = {
                    'username': sub.user.username if sub.user else f"User {sub.user_id}",
                    'fingerprints': fingerprints
                }
                
        results = []
        user_ids = list(student_fingerprints.keys())
        for i in range(len(user_ids)):
            for j in range(i + 1, len(user_ids)):
                uid1, uid2 = user_ids[i], user_ids[j]
                f1 = student_fingerprints[uid1]['fingerprints']
                f2 = student_fingerprints[uid2]['fingerprints']
                if not f1 or not f2:
                    continue
                intersection = len(f1.intersection(f2))
                union = len(f1.union(f2))
                similarity = (intersection / union) * 100 if union > 0 else 0
                if similarity >= 50.0:
                    results.append({
                        'student1': student_fingerprints[uid1]['username'],
                        'student2': student_fingerprints[uid2]['username'],
                        'similarity': round(similarity, 2),
                        'shared_fingerprints_count': intersection
                    })
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return jsonify({
            'challenge_id': challenge_id,
            'submissions_checked': len(student_fingerprints),
            'results': results
        }), 200
    except Exception as e:
        print(f"Plagiarism check error: {str(e)}")
        return jsonify({'message': 'Failed to check plagiarism', 'error': str(e)}), 500

# Elo-based Competitive Matchmaking
MATCHMAKING_QUEUE = {}

@app.route('/api/matchmaking/join', methods=['POST'])
@jwt_required()
def join_matchmaking():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        stale_threshold = datetime.utcnow() - timedelta(minutes=5)
        stale_ids = [uid for uid, info in MATCHMAKING_QUEUE.items() if info['joined_at'] < stale_threshold]
        for uid in stale_ids:
            del MATCHMAKING_QUEUE[uid]
            
        MATCHMAKING_QUEUE[current_user_id] = {
            'username': user.username,
            'elo': user.elo_rating or 1000,
            'joined_at': datetime.utcnow(),
            'matched_with': None,
            'challenge_id': None
        }
        
        user_info = MATCHMAKING_QUEUE[current_user_id]
        match_found_id = None
        
        time_in_queue = (datetime.utcnow() - user_info['joined_at']).total_seconds()
        elo_tolerance = 50 + int(time_in_queue * 10)
        
        for other_id, other_info in MATCHMAKING_QUEUE.items():
            if other_id == current_user_id or other_info['matched_with'] is not None:
                continue
            other_time = (datetime.utcnow() - other_info['joined_at']).total_seconds()
            other_tolerance = 50 + int(other_time * 10)
            elo_diff = abs(user_info['elo'] - other_info['elo'])
            
            if elo_diff <= elo_tolerance or elo_diff <= other_tolerance:
                match_found_id = other_id
                break
                
        if match_found_id:
            challenge = CodeChallenge.query.filter_by(is_active=True).first()
            challenge_id = challenge.id if challenge else 1
            room_id = f"room_{min(current_user_id, match_found_id)}_{max(current_user_id, match_found_id)}"
            
            MATCHMAKING_QUEUE[current_user_id]['matched_with'] = match_found_id
            MATCHMAKING_QUEUE[current_user_id]['challenge_id'] = challenge_id
            MATCHMAKING_QUEUE[current_user_id]['room_id'] = room_id
            
            MATCHMAKING_QUEUE[match_found_id]['matched_with'] = current_user_id
            MATCHMAKING_QUEUE[match_found_id]['challenge_id'] = challenge_id
            MATCHMAKING_QUEUE[match_found_id]['room_id'] = room_id
            
            COMBAT_ROOMS[room_id] = {
                'challenge_id': challenge_id,
                'players': {
                    current_user_id: {'username': user.username, 'progress': 0, 'status': 'Coding', 'last_seen': datetime.utcnow()},
                    match_found_id: {'username': other_info['username'], 'progress': 0, 'status': 'Coding', 'last_seen': datetime.utcnow()}
                },
                'matched_at': datetime.utcnow()
            }
            
            return jsonify({
                'status': 'Matched',
                'opponent': other_info['username'],
                'opponent_elo': other_info['elo'],
                'challenge_id': challenge_id,
                'room_id': room_id
            }), 200
            
        return jsonify({'status': 'Searching', 'message': 'Searching for opponent...'}), 200
    except Exception as e:
        print(f"Matchmaking join error: {str(e)}")
        return jsonify({'message': 'Failed to join matchmaking', 'error': str(e)}), 500

@app.route('/api/matchmaking/status', methods=['GET'])
@jwt_required()
def get_matchmaking_status():
    try:
        current_user_id = int(get_jwt_identity())
        if current_user_id not in MATCHMAKING_QUEUE:
            return jsonify({'status': 'NotQueued', 'message': 'You are not in matchmaking queue'}), 200
            
        info = MATCHMAKING_QUEUE[current_user_id]
        if info['matched_with']:
            opponent_id = info['matched_with']
            opponent_info = MATCHMAKING_QUEUE.get(opponent_id, {'username': 'Opponent', 'elo': 1000})
            challenge_id = info['challenge_id']
            room_id = info.get('room_id')
            
            del MATCHMAKING_QUEUE[current_user_id]
            return jsonify({
                'status': 'Matched',
                'opponent': opponent_info['username'],
                'opponent_elo': opponent_info.get('elo', 1000),
                'challenge_id': challenge_id,
                'room_id': room_id
            }), 200
            
        time_in_queue = (datetime.utcnow() - info['joined_at']).total_seconds()
        elo_tolerance = 50 + int(time_in_queue * 10)
        return jsonify({
            'status': 'Searching',
            'time_in_queue': int(time_in_queue),
            'elo_tolerance': elo_tolerance
        }), 200
    except Exception as e:
        print(f"Matchmaking status error: {str(e)}")
        return jsonify({'message': 'Failed to check status', 'error': str(e)}), 500

# Bookmarks API
@app.route('/api/bookmarks', methods=['POST'])
@jwt_required()
def toggle_bookmark():
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        item_type = data.get('item_type')  # 'quiz' or 'challenge'
        item_id = data.get('item_id')

        if not item_type or not item_id:
            return jsonify({'message': 'item_type and item_id are required'}), 400

        if item_type not in ['quiz', 'challenge']:
            return jsonify({'message': 'Invalid item_type'}), 400

        from models import UserBookmark
        existing = UserBookmark.query.filter_by(
            user_id=current_user_id,
            item_type=item_type,
            item_id=item_id
        ).first()

        if existing:
            db.session.delete(existing)
            db.session.commit()
            return jsonify({'bookmarked': False, 'message': 'Bookmark removed successfully'}), 200
        else:
            bookmark = UserBookmark(
                user_id=current_user_id,
                item_type=item_type,
                item_id=item_id
            )
            db.session.add(bookmark)
            db.session.commit()
            return jsonify({'bookmarked': True, 'message': 'Bookmark added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to toggle bookmark', 'error': str(e)}), 500

@app.route('/api/bookmarks', methods=['GET'])
@jwt_required()
def get_bookmarks():
    try:
        current_user_id = int(get_jwt_identity())
        from models import UserBookmark, Quiz, CodeChallenge
        
        bookmarks = UserBookmark.query.filter_by(user_id=current_user_id).order_by(UserBookmark.created_at.desc()).all()
        
        results = []
        for b in bookmarks:
            info = {
                'id': b.id,
                'item_type': b.item_type,
                'item_id': b.item_id,
                'created_at': b.created_at.isoformat()
            }
            if b.item_type == 'quiz':
                quiz = Quiz.query.get(b.item_id)
                if quiz:
                    info['title'] = quiz.title
                    info['description'] = quiz.description
                else:
                    continue
            elif b.item_type == 'challenge':
                challenge = CodeChallenge.query.get(b.item_id)
                if challenge:
                    info['title'] = challenge.title
                    info['description'] = challenge.description
                    info['difficulty'] = challenge.difficulty
                else:
                    continue
            results.append(info)
            
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'message': 'Failed to retrieve bookmarks', 'error': str(e)}), 500

# AI Tutor Chat API
@app.route('/api/challenges/<int:challenge_id>/ai-chat', methods=['POST'])
@jwt_required()
def get_ai_chat(challenge_id):
    try:
        current_user_id = int(get_jwt_identity())
        challenge = CodeChallenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'message': 'Challenge not found'}), 404
            
        data = request.get_json() or {}
        message = data.get('message', '').strip()
        history = data.get('history', [])
        code = data.get('code', '').strip()
        language = data.get('language', 'python').lower()
        
        if not message:
            return jsonify({'message': 'Please type a message.'}), 400
            
        gemini_key = os.getenv('GEMINI_API_KEY')
        response_text = ""
        
        if gemini_key:
            formatted_history = ""
            for chat in history[-6:]:
                sender = "Student" if chat.get('sender') == 'user' else "AI Tutor"
                formatted_history += f"{sender}: {chat.get('text')}\n"
                
            prompt = (
                f"You are an encouraging and friendly AI coding mentor for students.\n"
                f"The student is working on the coding challenge: '{challenge.title}'.\n"
                f"Challenge Description:\n{challenge.description}\n\n"
                f"The student is writing in {language}. Here is their current code:\n"
                f"```\n{code}\n```\n\n"
                f"Recent chat history:\n{formatted_history}\n"
                f"Student's new message: \"{message}\"\n\n"
                f"Instructions:\n"
                f"1. Be encouraging, warm, and explain concepts simply (using analogies or ELI5 style if asked).\n"
                f"2. DO NOT write the complete solution code for the student. Give snippets or pseudocode if helpful, but guide them to code it themselves.\n"
                f"3. Help debug their logical or syntax errors step-by-step."
            )
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    resp_json = response.json()
                    response_text = resp_json['candidates'][0]['content']['parts'][0]['text']
            except Exception as gemini_err:
                print(f"Gemini API request failed: {str(gemini_err)}")
                
        if not response_text:
            msg_lower = message.lower()
            title_lower = challenge.title.lower()
            
            if "explain" in msg_lower or "how to solve" in msg_lower or "concept" in msg_lower:
                if "sum" in title_lower:
                    response_text = (
                        "Sure! Let's break down the **Sum** challenge like we're 5.\n\n"
                        "Imagine you have a box of toys, and you want to find two toys that together weigh exactly a target amount. "
                        "Instead of picking up every pair and adding them up (which takes a long time), you can write down the weight of each toy in a notebook. "
                        "Then, for each toy, you check your notebook to see if the 'remaining weight' we need is already written down!\n\n"
                        "**Hint:** In programming, that 'notebook' is a **Dictionary / Hash Map**. Do you want to try writing that?"
                    )
                elif "palindrome" in title_lower:
                    response_text = (
                        "A palindrome is like a word that reads the same forwards and backwards, like *radar* or *madam*.\n\n"
                        "To check this, put a pointer finger at the very beginning of the word, and another pointer finger at the very end. "
                        "Compare the letters. If they match, move both fingers inwards by one step and compare again. If they mismatch, it's not a palindrome!\n\n"
                        "Try creating a loop or using two variables (pointers) to move towards the center!"
                    )
                else:
                    response_text = (
                        f"Let's look at **{challenge.title}** step-by-step.\n\n"
                        f"1. First, think about the **base case**: what happens if the input is empty or zero?\n"
                        f"2. Then, define the core logic: how do we transform our input to match the expected output?\n"
                        f"3. Make sure you read from standard input (`stdin`) and write back to output.\n\n"
                        f"What part of your code are you unsure about?"
                    )
            elif "give me code" in msg_lower or "give me the solution" in msg_lower or "solution code" in msg_lower:
                response_text = (
                    "I can't just give you the direct solution code, because that would steal the learning moment from you! 🎓\n\n"
                    "However, here is the pseudocode structure you can follow:\n"
                    "```text\n"
                    "1. Read input values\n"
                    "2. Initialize a helper record/state (e.g. dictionary or index pointers)\n"
                    "3. Loop through elements:\n"
                    "    - Calculate target condition\n"
                    "    - If condition met, return indices/values\n"
                    "    - Else, update records\n"
                    "```\n"
                    "Why don't you try to draft this loop structure in your editor first?"
                )
            elif "error" in msg_lower or "bug" in msg_lower or "wrong" in msg_lower or "failing" in msg_lower:
                response_text = (
                    "Ah, debugging is like being a detective in a crime movie where you are also the criminal! 🕵️‍♂️\n\n"
                    "Let's look at your code. Make sure that:\n"
                    "- You are reading the correct number of inputs from standard input.\n"
                    "- Your function actually returns the value instead of just printing it (or vice versa, depending on what the starter code expects).\n"
                    "- You don't have syntax errors like mismatched parentheses `()` or missing colons `()`."
                )
            else:
                response_text = (
                    "Hello! I am your AI Mentor. I can explain code structure, suggest better algorithms, or help debug errors.\n\n"
                    "Could you tell me what specific part of the challenge or your code you would like to explain?"
                )
                
        hint_log = AIHintLog(
            user_id=current_user_id,
            challenge_id=challenge_id,
            submitted_code=code,
            hint_response=f"CHAT MSG: {message}\nRESPONSE: {response_text}"
        )
        db.session.add(hint_log)
        db.session.commit()
        
        return jsonify({'response': response_text}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to process AI chat request', 'error': str(e)}), 500

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    
    # Start the job scheduler
    print("Starting job scheduler...")
    job_scheduler.start()
    
    try:
        print("Starting Flask server on http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        # Stop the job scheduler when the app shuts down
        job_scheduler.stop()