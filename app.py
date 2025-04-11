from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_admin import Admin, AdminIndexView
from models import db, User, Course, Grade
from admin_views import UserView, CourseView, EnhancedGradeView
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_enrollment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800

CORS(app, supports_credentials=True)
db.init_app(app)

# Setup Flask-Admin with enhanced views
app.config['FLASK_ADMIN_TEMPLATE_MODE'] = 'bootstrap3'
admin = Admin(app, name='Student Enrollment Admin', template_mode='bootstrap3', 
              base_template='admin/master.html',
              index_view=AdminIndexView(
                  url='/admin',
                  template='admin/index.html'
              ))
os.makedirs('templates/admin', exist_ok=True)

with open('templates/admin/master.html', 'w') as f:
    f.write('''
{% extends 'admin/base.html' %}

{% block access_control %}
<div class="navbar-text btn-group pull-right">
    <a href="{{ url_for('admin_logout') }}" class="btn btn-danger">Logout</a>
</div>
{% endblock %}
''')

# Initialize the context
with app.app_context():
    admin.add_view(UserView(model=User, session=db.session))
    admin.add_view(CourseView(model=Course, session=db.session))
    admin.add_view(EnhancedGradeView(model=Grade, session=db.session))

# API Routes
@app.route('/admin/logout')
def admin_logout():
    session.pop('user_id', None)
    session.pop('admin_logged_in', None)
    return redirect('http://localhost:3000/login')

@app.route('/admin/')
@app.route('/admin/<path:path>')
def check_admin_login(path=None):
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    return admin.index_view()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    
    if user and (user.password == data['password']):
        session['user_id'] = user.id
        if user.role == 'admin':
            session['admin_logged_in'] = True
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    
    return jsonify({
        'success': False,
        'error': 'Invalid username or password'
    }), 401

@app.route('/login')
def login_page():
    if 'admin_logged_in' in session:
        return redirect('/admin/')
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.role == 'admin':
            session['admin_logged_in'] = True
            return redirect('/admin/')
    
    # If not logged in as admin, render login page or redirect to frontend
    return redirect('/')

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/api/user')
def get_user():
    user_id = session.get('user_id')
    
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            })
    
    return jsonify({'authenticated': False})

@app.route('/api/student/courses')
def student_courses():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(user_id)
    
    if not user or user.role != 'student':
        return jsonify({'error': 'Permission denied'}), 403
    
    enrolled_courses = []
    for course in user.courses_enrolled:
        course_dict = course.to_dict()
        course_dict['enrolled'] = True
        grade = Grade.query.filter_by(student_id=user.id, course_id=course.id).first()
        if grade:
            course_dict['grade'] = grade.value
        enrolled_courses.append(course_dict)
    
    # Get available courses (not enrolled in)
    all_courses = Course.query.all()
    enrolled_course_ids = [c.id for c in user.courses_enrolled]
    available_courses = []
    for course in all_courses:
        if course.id not in enrolled_course_ids:
            course_dict = course.to_dict()
            course_dict['enrolled'] = False
            available_courses.append(course_dict)
    
    return jsonify({
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses
    })

@app.route('/api/teacher/courses')
def teacher_courses():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(user_id)
    
    if not user or user.role != 'teacher':
        return jsonify({'error': 'Permission denied'}), 403
    
    courses = [course.to_dict() for course in user.courses_teaching]
    
    return jsonify(courses)

@app.route('/api/teacher/course/<int:course_id>/students')
def course_students(course_id):
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    
    if not user or user.role != 'teacher' or not course or course.teacher_id != user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    students_data = []
    for student in course.students:
        student_dict = student.to_dict()
        
        grade = Grade.query.filter_by(student_id=student.id, course_id=course.id).first()
        if grade:
            student_dict['grade'] = grade.value
        else:
            student_dict['grade'] = None
        students_data.append(student_dict)
    
    return jsonify(students_data)

@app.route('/api/teacher/update-grade', methods=['POST'])
def update_grade():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(user_id)
    data = request.json
    course = Course.query.get(data['course_id'])
    
    if not user or user.role != 'teacher' or not course or course.teacher_id != user.id:
        return jsonify({'error': 'Permission denied'}), 403
    
    student = User.query.get(data['student_id'])
    if not student or course not in student.courses_enrolled:
        return jsonify({'error': 'Student not enrolled in this course'}), 400
    
    grade = Grade.query.filter_by(student_id=data['student_id'], course_id=data['course_id']).first()
    
    if grade:
        grade.value = data['value']
    else:
        grade = Grade(
            student_id=data['student_id'],
            course_id=data['course_id'],
            value=data['value']
        )
        db.session.add(grade)
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/student/enroll', methods=['POST'])
def enroll_course():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(user_id)
    data = request.json
    course = Course.query.get(data['course_id'])
    
    if not user or user.role != 'student' or not course:
        return jsonify({'error': 'Permission denied or course not found'}), 403
    
    if course in user.courses_enrolled:
        return jsonify({'error': 'Already enrolled in this course'}), 400
    
    if len(course.students) >= course.capacity:
        return jsonify({'error': 'Course is full'}), 400
    
    user.courses_enrolled.append(course)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/student/drop', methods=['POST'])
def drop_course():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(user_id)
    data = request.json
    course = Course.query.get(data['course_id'])
    
    if not user or user.role != 'student' or not course:
        return jsonify({'error': 'Permission denied or course not found'}), 403
    
    if course not in user.courses_enrolled:
        return jsonify({'error': 'Not enrolled in this course'}), 400
    
    user.courses_enrolled.remove(course)
    
    grade = Grade.query.filter_by(student_id=user.id, course_id=course.id).first()
    if grade:
        db.session.delete(grade)
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/courses')
def get_courses():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    courses = Course.query.all()
    courses_data = [course.to_dict() for course in courses]
    
    return jsonify(courses_data)

if __name__ == '__main__':
    app.run(debug=True)