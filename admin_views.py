from flask_admin.contrib.sqla import ModelView
from wtforms import Form, StringField, PasswordField, SelectField, FloatField
from wtforms.validators import DataRequired
from models import User, Course, Grade, db
from flask import flash, redirect, request, url_for
from flask_admin.base import expose

class UserView(ModelView):
    column_list = ('id', 'username', 'role')
    form_columns = ('username', 'password', 'role')
    
    # Use this for role options
    form_choices = {
        'role': [
            ('student', 'Student'),
            ('teacher', 'Teacher'),
            ('admin', 'Admin')
        ]
    }
    
    # Override the edit view to use our custom implementation
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        id = request.args.get('id')
        if id is None:
            return redirect(url_for('.index_view'))
            
        model = self.get_one(id)
        if model is None:
            flash(f'Record {id} not found', 'error')
            return redirect(url_for('.index_view'))
        
        if request.method == 'POST':
            # Manual form processing
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            
            if username:
                model.username = username
            if password:  # Only update password if provided
                model.password = password
            if role:
                model.role = role
            
            try:
                self.session.commit()
                flash('User successfully updated', 'success')
                return redirect(url_for('.index_view'))
            except Exception as ex:
                flash(f'Failed to update record: {str(ex)}', 'error')
                self.session.rollback()
        
        # For GET requests, render the form
        return self.render('admin/user_edit.html', model=model)


class CourseView(ModelView):
    column_list = ('id', 'name', 'capacity', 'timeslot', 'teacher')
    form_columns = ('name', 'capacity', 'timeslot', 'teacher_id')
    
    column_formatters = {
        'teacher': lambda v, c, m, p: m.teacher.username if m.teacher else 'Unknown'
    }
    
    # Customize the form field for teacher_id
    form_args = {
        'teacher_id': {
            'label': 'Teacher'
        }
    }
    
    # Override the edit view to use our custom implementation
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        id = request.args.get('id')
        if id is None:
            return redirect(url_for('.index_view'))
            
        model = self.get_one(id)
        if model is None:
            flash(f'Record {id} not found', 'error')
            return redirect(url_for('.index_view'))
        
        # Get teacher options for dropdown
        teachers = User.query.filter_by(role='teacher').all()
        
        if request.method == 'POST':
            # Manual form processing
            name = request.form.get('name')
            capacity = request.form.get('capacity')
            timeslot = request.form.get('timeslot')
            teacher_id = request.form.get('teacher_id')
            
            if name:
                model.name = name
            if capacity:
                model.capacity = int(capacity)
            if timeslot:
                model.timeslot = timeslot
            if teacher_id:
                model.teacher_id = int(teacher_id)
            
            try:
                self.session.commit()
                flash('Course successfully updated', 'success')
                return redirect(url_for('.index_view'))
            except Exception as ex:
                flash(f'Failed to update record: {str(ex)}', 'error')
                self.session.rollback()
        
        # For GET requests, render the form
        return self.render('admin/course_edit.html',
                          model=model,
                          teachers=teachers)


class EnhancedGradeView(ModelView):
    column_list = ('id', 'student', 'course', 'value')
    form_columns = ('student_id', 'course_id', 'value')
    
    column_formatters = {
        'student': lambda v, c, m, p: m.student.username if m.student else 'Unknown',
        'course': lambda v, c, m, p: m.course.name if m.course else 'Unknown'
    }
    
    def _student_query_factory(self):
        return User.query.filter_by(role='student')
    
    def _course_query_factory(self):
        return Course.query.all()
    
    # Override the edit view to use our custom implementation
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        id = request.args.get('id')
        if id is None:
            return redirect(url_for('.index_view'))
            
        model = self.get_one(id)
        if model is None:
            flash(f'Record {id} not found', 'error')
            return redirect(url_for('.index_view'))
        
        # Get options for dropdowns
        students = User.query.filter_by(role='student').all()
        courses = Course.query.all()
        
        if request.method == 'POST':
            # Manual form processing
            student_id = request.form.get('student_id')
            course_id = request.form.get('course_id')
            value = request.form.get('value')
            
            if student_id:
                model.student_id = int(student_id)
            if course_id:
                model.course_id = int(course_id)
            if value:
                model.value = float(value)
            
            try:
                self.session.commit()
                flash('Grade successfully updated', 'success')
                return redirect(url_for('.index_view'))
            except Exception as ex:
                flash(f'Failed to update record: {str(ex)}', 'error')
                self.session.rollback()
        
        # For GET requests, render the form
        return self.render('admin/grade_edit.html',
                          model=model,
                          students=students,
                          courses=courses)