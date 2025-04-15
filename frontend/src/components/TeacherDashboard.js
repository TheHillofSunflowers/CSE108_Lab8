import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function TeacherDashboard({ user }) {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/teacher/courses', {
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch courses');
        }
        
        const data = await response.json();
        setCourses(data);
      } catch (error) {
        setError('Error fetching courses');
        console.error('Error fetching courses:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCourses();
  }, []);

  if (loading) {
    return <div className="loading">Loading courses...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="teacher-dashboard">
      <h2>Teacher Dashboard</h2>
      
      <h3>My Courses</h3>
      {courses.length === 0 ? (
        <p>You are not teaching any courses.</p>
      ) : (
        <table className="courses-table">
          <thead>
            <tr>
              <th>Course Name</th>
              <th>Teacher</th>
              <th>Time</th>
              <th>Enrollment</th>
            </tr>
          </thead>
          <tbody>
            {courses.map(course => (
              <tr key={course.id}>
                <td>
                  <Link to={`/teacher/course/${course.id}`}>
                    {course.name}
                  </Link>
                </td>
                <td>{course.teacher_name}</td>
                <td>{course.timeslot}</td>
                <td>{course.enrolled_count}/{course.capacity}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default TeacherDashboard;