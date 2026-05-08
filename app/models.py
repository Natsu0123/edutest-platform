from __future__ import annotations

import json
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash

from app.extensions import bcrypt, db, login_manager


QUESTION_TYPE_ALIASES = {
    'single': 'single_choice',
    'multiple': 'multiple_choice',
    'single_choice': 'single_choice',
    'multiple_choice': 'multiple_choice',
    'matching': 'matching',
    'text': 'text',
    'ordering': 'ordering',
}


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    full_name = db.Column(db.String(120), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('student_group.id'))

    assignments = db.relationship('TestAssignment', back_populates='user', cascade='all, delete-orphan')
    attempts = db.relationship('Attempt', back_populates='user', cascade='all, delete-orphan')
    action_logs = db.relationship('ActionLog', back_populates='actor', cascade='all, delete-orphan')
    group = db.relationship('StudentGroup', back_populates='students')

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

    @property
    def is_teacher(self) -> bool:
        return self.role == 'teacher'

    @property
    def is_staff(self) -> bool:
        return self.role in ('admin', 'teacher')

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        if self.password_hash.startswith('$2'):
            return bcrypt.check_password_hash(self.password_hash, password)
        return check_password_hash(self.password_hash, password)
teacher_group_link = db.Table(
    'teacher_group_link',
    db.Column('teacher_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('student_group.id'), primary_key=True),
)

class StudentGroup(db.Model):
    __tablename__ = 'student_group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    students = db.relationship('User', back_populates='group')
    teachers = db.relationship(
        'User',
        secondary=teacher_group_link,
        backref='teaching_groups'
    )

        

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    time_limit_minutes = db.Column(db.Integer, nullable=False, default=30)
    max_attempts = db.Column(db.Integer, nullable=False, default=1)
    questions_per_student = db.Column(db.Integer, nullable=False, default=20)
    target_score = db.Column(db.Integer, nullable=False, default=20)
        
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship(
        'User',
        foreign_keys=[created_by],
        backref='created_tests'
    )

    teacher = db.relationship(
        'User',
        foreign_keys=[teacher_id],
        backref='teacher_tests'
    )

    questions = db.relationship('Question', back_populates='test', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('Attempt', back_populates='test', lazy=True, cascade='all, delete-orphan')
    assignments = db.relationship('TestAssignment', back_populates='test', cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey("test.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False, default="single_choice")
    points = db.Column(db.Integer, default=1, nullable=False)
   
    image_path = db.Column(db.String(255))

    test = db.relationship('Test', back_populates='questions')
    extra_data = db.relationship('QuestionExtraData', back_populates='question', uselist=False, cascade='all, delete-orphan')
    answer_options = db.relationship('AnswerOption', back_populates='question', cascade='all, delete-orphan')
    attempt_answers = db.relationship('AttemptAnswer', back_populates='question', cascade='all, delete-orphan')
    attempt_responses = db.relationship('AttemptResponse', back_populates='question', cascade='all, delete-orphan')

    @property
    def normalized_type(self) -> str:
        return QUESTION_TYPE_ALIASES.get(self.question_type, self.question_type)

    @property
    def payload(self) -> dict:
        if not self.extra_data or not self.extra_data.payload_json:
            return {}
        try:
            return json.loads(self.extra_data.payload_json)
        except json.JSONDecodeError:
            return {}

    def set_payload(self, payload: dict) -> None:
        if not self.extra_data:
            self.extra_data = QuestionExtraData(payload_json='{}')
        self.extra_data.payload_json = json.dumps(payload, ensure_ascii=False)

class QuestionExtraData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False, unique=True)
    payload_json = db.Column(db.Text, nullable=False, default='{}')

    question = db.relationship('Question', back_populates='extra_data')


class AnswerOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)

    question = db.relationship('Question', back_populates='answer_options')
    attempt_answers = db.relationship('AttemptAnswer', back_populates='answer_option', cascade='all, delete-orphan')


class TestAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    question_limit = db.Column(db.Integer, nullable=True)
    target_score = db.Column(db.Integer, nullable=True)

    user = db.relationship('User', back_populates='assignments')
    test = db.relationship('Test', back_populates='assignments')

    __table_args__ = (db.UniqueConstraint('user_id', 'test_id', name='uq_user_test_assignment'),)


class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    score_percent = db.Column(db.Float, default=0)
    correct_count = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    earned_score = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=0)

    tab_switch_count = db.Column(db.Integer, nullable=False, default=0)
    heartbeat_count = db.Column(db.Integer, nullable=False, default=0)
    focus_loss_count = db.Column(db.Integer, nullable=False, default=0)
    fullscreen_exit_count = db.Column(db.Integer, nullable=False, default=0)
    suspicion_score = db.Column(db.Integer, nullable=False, default=0)
    last_seen_at = db.Column(db.DateTime, nullable=True)
    suspicion_flags_json = db.Column(db.Text, nullable=False, default='{}')

    user = db.relationship('User', back_populates='attempts')
    test = db.relationship('Test', back_populates='attempts')
    answers = db.relationship('AttemptAnswer', back_populates='attempt', cascade='all, delete-orphan')
    responses = db.relationship('AttemptResponse', back_populates='attempt', cascade='all, delete-orphan')

    @property
    def suspicion_flags(self) -> dict:
        try:
            return json.loads(self.suspicion_flags_json or '{}')
        except json.JSONDecodeError:
            return {}

    def set_suspicion_flags(self, payload: dict) -> None:
        self.suspicion_flags_json = json.dumps(payload, ensure_ascii=False)

    @property
    def risk_level(self) -> str:
        if self.suspicion_score >= 8:
            return 'high'
        if self.suspicion_score >= 4:
            return 'medium'
        return 'low'


class AttemptAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_option_id = db.Column(db.Integer, db.ForeignKey('answer_option.id'), nullable=False)

    attempt = db.relationship('Attempt', back_populates='answers')
    question = db.relationship('Question', back_populates='attempt_answers')
    answer_option = db.relationship('AnswerOption', back_populates='attempt_answers')


class AttemptResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    response_json = db.Column(db.Text, nullable=False, default='{}')

    attempt = db.relationship('Attempt', back_populates='responses')
    question = db.relationship('Question', back_populates='attempt_responses')

    @property
    def data(self) -> dict:
        try:
            return json.loads(self.response_json)
        except json.JSONDecodeError:
            return {}

    def set_data(self, payload: dict) -> None:
        self.response_json = json.dumps(payload, ensure_ascii=False)

class ActionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action_type = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    actor = db.relationship('User', back_populates='action_logs')




@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))
