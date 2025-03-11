from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    precondition = db.Column(db.String(500), nullable=True)
    postcondition = db.Column(db.String(500), nullable=True)
    comment = db.Column(db.String(500), nullable=True)

class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_case.id'), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    expected_result = db.Column(db.String(500), nullable=False)
