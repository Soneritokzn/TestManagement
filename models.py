from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Enum as SQLEnum
import enum

db = SQLAlchemy()

class TestStatus(enum.Enum):
    NOT_RUN = "Not Run"
    PASSED = "Passed"
    FAILED = "Failed"
    BLOCKED = "Blocked"
    SKIPPED = "Skipped"

class Priority(enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    precondition = db.Column(db.Text, nullable=True)
    postcondition = db.Column(db.Text, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default=TestStatus.NOT_RUN.value)
    priority = db.Column(db.String(20), default=Priority.MEDIUM.value)
    category = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.String(500), nullable=True)  # Comma-separated tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    template_id = db.Column(db.Integer, db.ForeignKey('test_case_template.id'), nullable=True)
    related_to = db.Column(db.Integer, db.ForeignKey('test_case.id'), nullable=True)
    
    steps = db.relationship('Step', backref='test_case', cascade="all, delete-orphan", order_by='Step.order')
    comments = db.relationship('TestCaseComment', backref='test_case', cascade="all, delete-orphan")
    attachments = db.relationship('Attachment', backref='test_case', cascade="all, delete-orphan")
    versions = db.relationship('TestCaseVersion', backref='test_case', cascade="all, delete-orphan")
    test_runs = db.relationship('TestCaseExecution', backref='test_case', cascade="all, delete-orphan")

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text, nullable=False)
    actual_result = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TestCaseComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'), nullable=True)
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TestCaseTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    precondition = db.Column(db.Text, nullable=True)
    postcondition = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    template_steps = db.relationship('TemplateStep', backref='template', cascade="all, delete-orphan")
    test_cases = db.relationship('TestCase', backref='template', lazy=True)

class TemplateStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('test_case_template.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)

class TestRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    executions = db.relationship('TestCaseExecution', backref='test_run', cascade="all, delete-orphan")

class TestCaseExecution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'), nullable=False)
    test_run_id = db.Column(db.Integer, db.ForeignKey('test_run.id'), nullable=True)
    status = db.Column(db.String(20), default=TestStatus.NOT_RUN.value)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

class TestCaseVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    precondition = db.Column(db.Text, nullable=True)
    postcondition = db.Column(db.Text, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    version_steps = db.relationship('VersionStep', backref='version', cascade="all, delete-orphan")

class VersionStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('test_case_version.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)
