from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import func

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
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
   
    # These relationships are defined through backrefs in other models
    grades = db.relationship('Grade', back_populates='student')
   
    def __str__(self):
        return self.username
        
    def __repr__(self):
        return f"<User {self.username}>"
   
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }

class Course(db.Model):
    __tablename__ = 'courses'
   
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    timeslot = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
   
    # Define relationships clearly
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref=db.backref('courses_teaching', lazy='dynamic'))
    students = db.relationship('User', secondary=enrollments, backref=db.backref('courses_enrolled', lazy='dynamic'))
    grades = db.relationship('Grade', back_populates='course', cascade='all, delete-orphan')
   
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return f"<Course {self.name}>"
   
    def to_dict(self, include_students=False):
        # Safely get enrolled count
        enrolled_count = 0
        try:
            # Use a direct query to count enrolled students
            enrolled_count = db.session.query(func.count(enrollments.c.user_id)).filter(
                enrollments.c.course_id == self.id
            ).scalar()
        except Exception as e:
            print(f"Error counting students: {e}")
            # Fallback to counting the list if query fails
            try:
                enrolled_count = len(list(self.students))
            except:
                enrolled_count = 0
            
        course_dict = {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity,
            'timeslot': self.timeslot,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.username if self.teacher else 'Unknown',
            'enrolled_count': enrolled_count,
        }
       
        if include_students:
            try:
                student_list = []
                for student in self.students:
                    student_list.append(student.to_dict())
                course_dict['students'] = student_list
            except Exception as e:
                print(f"Error listing students: {e}")
                course_dict['students'] = []
           
        return course_dict

class Grade(db.Model):
    __tablename__ = 'grades'
   
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
   
    student = db.relationship('User', back_populates='grades')
    course = db.relationship('Course', back_populates='grades')
   
    def __str__(self):
        student_name = self.student.username if self.student else "Unknown"
        course_name = self.course.name if self.course else "Unknown"
        return f"{student_name} - {course_name}: {self.value}"
        
    def __repr__(self):
        return f"<Grade {self.id}: {self.value}>"
   
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'value': self.value,
            'student_name': self.student.username if self.student else "Unknown",
            'course_name': self.course.name if self.course else "Unknown"
        }