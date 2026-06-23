from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_subjects', lazy=True)

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    theory = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_chapters', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    xp = db.Column(db.Integer, default=0)
    streak_count = db.Column(db.Integer, default=0)
    last_active_date = db.Column(db.Date)
    elo_rating = db.Column(db.Integer, default=1000)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    gender = db.Column(db.String(50), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    
    # Relationships
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    created_quizzes = db.relationship('Quiz', backref='creator', lazy=True)
    badges = db.relationship('UserBadge', backref='user', lazy=True, cascade='all, delete-orphan')

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    time_limit = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    elo_rating = db.Column(db.Integer, default=1000)
    questions_per_attempt = db.Column(db.Integer, default=8, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    points = db.Column(db.Integer, default=1)
    hint = db.Column(db.Text)
    explanation = db.Column(db.Text)
    
    # Relationships
    user_answers = db.relationship('UserAnswer', backref='question', lazy=True)

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False, index=True)
    score = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    time_taken = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, index=True)
    question_ids = db.Column(db.Text, nullable=True)
    
    # Relationships
    user_answers = db.relationship('UserAnswer', backref='attempt', lazy=True, cascade='all, delete-orphan')

class UserAnswer(db.Model):
    __tablename__ = 'user_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    selected_answer = db.Column(db.String(1))
    is_correct = db.Column(db.Boolean, default=False)
    hint_used = db.Column(db.Boolean, default=False)

class CodeChallenge(db.Model):
    __tablename__ = 'code_challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    difficulty = db.Column(db.String(20), default='Medium') # Easy, Medium, Hard
    time_limit = db.Column(db.Integer, default=30)
    memory_limit = db.Column(db.Integer, default=256)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    test_cases = db.relationship('TestCase', backref='challenge', lazy=True, cascade='all, delete-orphan')
    submissions = db.relationship('CodeSubmission', backref='challenge', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_challenges', lazy=True)
    
    # We also add a relationship to Chapter so it's accessible backwards
    # chapter is already linked via backref below, but we must add backref to Chapter manually if we want
    # actually, Chapter model needs updating to include `code_challenges` if we want backref, or we just rely on explicit queries.

class TestCase(db.Model):
    __tablename__ = 'test_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('code_challenges.id'), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_hidden = db.Column(db.Boolean, default=True)

class ChallengeTemplate(db.Model):
    __tablename__ = 'challenge_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('code_challenges.id'), nullable=False)
    language = db.Column(db.String(50), nullable=False) # python, javascript, cpp, c, java, php
    template_code = db.Column(db.Text, nullable=False)
    
    # Relationships
    challenge = db.relationship('CodeChallenge', backref=db.backref('templates', cascade='all, delete-orphan'))
    
    __table_args__ = (db.UniqueConstraint('challenge_id', 'language', name='_challenge_lang_uc'),)

class CodeSubmission(db.Model):
    __tablename__ = 'code_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('code_challenges.id'), nullable=False, index=True)
    submitted_code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), nullable=False) # python, java, c, cpp, javascript, php
    status = db.Column(db.String(50), default='Pending') # Accepted, Wrong Answer, TLE, Error
    execution_time = db.Column(db.Float)
    memory_used = db.Column(db.Float)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class Badge(db.Model):
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon_url = db.Column(db.String(255))
    criteria_type = db.Column(db.String(50), nullable=False) # e.g. 'attempts', 'perfect_scores', 'streak', 'xp'
    criteria_value = db.Column(db.Integer, default=1)
    
    # Relationships
    user_badges = db.relationship('UserBadge', backref='badge', lazy=True, cascade='all, delete-orphan')

class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='comments', lazy=True)
    quiz = db.relationship('Quiz', backref=db.backref('comments', cascade='all, delete-orphan'), lazy=True)

class RecommendationCache(db.Model):
    __tablename__ = 'recommendation_caches'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    proficiency_index = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('recommendation_caches', cascade='all, delete-orphan'), lazy=True)
    chapter = db.relationship('Chapter', backref=db.backref('recommendation_caches', cascade='all, delete-orphan'), lazy=True)

class UserEloHistory(db.Model):
    __tablename__ = 'user_elo_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    elo_rating = db.Column(db.Integer, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('elo_history', cascade='all, delete-orphan'), lazy=True)
    attempt = db.relationship('QuizAttempt', backref=db.backref('elo_history'), lazy=True)

class Tournament(db.Model):
    __tablename__ = 'tournaments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    starts_at = db.Column(db.DateTime, nullable=False)
    ends_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=True)
    
    # Relationships
    creator = db.relationship('User', backref=db.backref('created_tournaments', cascade='all, delete-orphan'), lazy=True)

class TournamentParticipant(db.Model):
    __tablename__ = 'tournament_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, default=0)
    time_taken = db.Column(db.Integer, default=0)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    tournament = db.relationship('Tournament', backref=db.backref('participants', cascade='all, delete-orphan'), lazy=True)
    user = db.relationship('User', backref=db.backref('tournament_registrations', cascade='all, delete-orphan'), lazy=True)

class TournamentQuestion(db.Model):
    __tablename__ = 'tournament_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id', ondelete='CASCADE'), nullable=False)
    question_type = db.Column(db.String(20), nullable=False) # 'code' or 'quiz'
    challenge_id = db.Column(db.Integer, db.ForeignKey('code_challenges.id', ondelete='CASCADE'), nullable=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=True)
    
    # Relationships
    tournament = db.relationship('Tournament', backref=db.backref('questions', cascade='all, delete-orphan'), lazy=True)
    challenge = db.relationship('CodeChallenge', lazy=True)
    question = db.relationship('Question', lazy=True)

class TournamentSubmission(db.Model):
    __tablename__ = 'tournament_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    question_type = db.Column(db.String(20), nullable=False) # 'code' or 'quiz'
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('code_challenges.id', ondelete='CASCADE'), nullable=True)
    selected_answer = db.Column(db.String(1), nullable=True) # A, B, C, D
    is_correct = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class AIHintLog(db.Model):
    __tablename__ = 'ai_hint_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('code_challenges.id'), nullable=False)
    submitted_code = db.Column(db.Text)
    hint_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('ai_hint_logs', cascade='all, delete-orphan'), lazy=True)
    challenge = db.relationship('CodeChallenge', backref=db.backref('ai_hint_logs', cascade='all, delete-orphan'), lazy=True)

class UserBookmark(db.Model):
    __tablename__ = 'user_bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    item_type = db.Column(db.String(50), nullable=False)  # 'quiz' or 'challenge'
    item_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('bookmarks', cascade='all, delete-orphan'), lazy=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'item_type', 'item_id', name='_user_item_bookmark_uc'),)