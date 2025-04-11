# Student Enrollment System

A full-stack web application for managing student enrollments, courses, and grades. Built with Flask (backend) and React (frontend).

## Features

- User authentication (Admin, Teacher, Student roles)
- Course management
- Student enrollment
- Grade tracking
- Admin dashboard

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm (comes with Node.js)

## Installation

### Backend Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd CSE108_Lab8
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Initialize the database:
   ```
   python init_db.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install Node.js dependencies:
   ```
   npm install
   ```

## Running the Application

1. Start the backend server (from the root directory):
   ```
   python app.py
   ```
   The backend will run on http://localhost:5000

2. Start the frontend development server (from the frontend directory):
   ```
   cd frontend
   npm start
   ```
   The frontend will run on http://localhost:3000

## Usage

1. Access the application at http://localhost:3000
2. Log in with the following credentials:
   - Admin: username: admin, password: admin123
   - Teacher: username: teacher1, password: teacher123
   - Student: username: student1, password: student123

## Project Structure

- `app.py`: Main Flask application
- `models.py`: Database models
- `admin_views.py`: Flask-Admin views
- `init_db.py`: Database initialization script
- `frontend/`: React frontend application
- `templates/`: Flask templates for admin interface

## API Endpoints

- `/api/login`: User authentication
- `/api/logout`: User logout
- `/api/user`: Get current user information
- `/api/student/courses`: Get student courses
- `/api/teacher/courses`: Get teacher courses
- `/api/teacher/course/<id>/students`: Get students in a course
- `/api/teacher/update-grade`: Update student grade
- `/api/student/enroll`: Enroll in a course
- `/api/student/drop`: Drop a course
- `/api/courses`: Get all courses

## License

MIT