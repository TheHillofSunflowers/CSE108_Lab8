from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Association table for many-to-many relationship between students and courses
enrollments = db.Table('enrollments',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    
    courses_enrolled = db.relationship('Course', secondary=enrollments, back_populates='students')
    courses_teaching = db.relationship('Course', back_populates='teacher')
    grades = db.relationship('Grade', back_populates='student')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'role': self.role
        }

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    capacity = db.Column(db.Integer, nullable=False)
    timeslot = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    teacher = db.relationship('User', back_populates='courses_teaching', foreign_keys=[teacher_id])
    students = db.relationship('User', secondary=enrollments, back_populates='courses_enrolled')
    grades = db.relationship('Grade', back_populates='course', cascade='all, delete-orphan')
    
    def to_dict(self, include_students=False):
        course_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'capacity': self.capacity,
            'timeslot': self.timeslot,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.username if self.teacher else 'Unknown',
            'enrolled_count': len(self.students),
        }
        
        if include_students:
            course_dict['students'] = [student.to_dict() for student in self.students]
            
        return course_dict

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    
    student = db.relationship('User', back_populates='grades')
    course = db.relationship('Course', back_populates='grades')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'value': self.value
        }
