from app import app, db
from models import User, Course, Grade

def create_sample_data():
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if User.query.count() > 0:
            print("Sample data already exists")
            return
        
        admin = User(username='admin', email='admin@school.com', password='admin123', role='admin')
        
        teacher1 = User(username='teacher1', email='teacher1@school.com', password='teacher123', role='teacher')
        teacher2 = User(username='teacher2', email='teacher2@school.com', password='teacher123', role='teacher')
        
        student1 = User(username='student1', email='student1@school.com', password='student123', role='student')
        student2 = User(username='student2', email='student2@school.com', password='student123', role='student')
        student3 = User(username='student3', email='student3@school.com', password='student123', role='student')
        
        db.session.add_all([admin, teacher1, teacher2, student1, student2, student3])
        db.session.commit()
        
        course1 = Course(
            name='Introduction to Python',
            description='Learn the basics of Python programming',
            capacity=30,
            timeslot='MW 10:00 AM - 11:30 AM',
            teacher_id=teacher1.id
        )
        
        course2 = Course(
            name='Web Development with Flask',
            description='Build web applications using Flask',
            capacity=25,
            timeslot='TTH 1:00 PM - 2:30 PM',
            teacher_id=teacher1.id
        )
        
        course3 = Course(
            name='Data Science Fundamentals',
            description='Introduction to data analysis and visualization',
            capacity=20,
            timeslot='MF 3:00 PM - 4:30 PM',
            teacher_id=teacher2.id
        )
        
        db.session.add_all([course1, course2, course3])
        db.session.commit()
        
        student1.courses_enrolled.append(course1)
        student1.courses_enrolled.append(course2)
        student2.courses_enrolled.append(course1)
        student3.courses_enrolled.append(course3)
        
        grade1 = Grade(student_id=student1.id, course_id=course1.id, value=85.5)
        grade2 = Grade(student_id=student1.id, course_id=course2.id, value=92.0)
        grade3 = Grade(student_id=student2.id, course_id=course1.id, value=78.5)
        grade4 = Grade(student_id=student3.id, course_id=course3.id, value=88.0)
        
        db.session.add_all([grade1, grade2, grade3, grade4])
        db.session.commit()
        
        print("Sample data created")

if __name__ == '__main__':
    create_sample_data()
