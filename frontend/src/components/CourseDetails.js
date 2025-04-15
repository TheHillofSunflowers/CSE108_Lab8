import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function CourseDetails({ user }) {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [courseInfo, setCourseInfo] = useState(null);

  useEffect(() => {
    const fetchCourseDetails = async () => {
      try {
        // Fetch course information
        const courseResponse = await fetch(`http://localhost:5000/api/courses`, {
          credentials: 'include'
        });
        
        if (!courseResponse.ok) {
          throw new Error('Failed to fetch course information');
        }
        
        const coursesData = await courseResponse.ok ? await courseResponse.json() : [];
        const currentCourse = coursesData.find(c => c.id === parseInt(courseId));
        setCourseInfo(currentCourse);
        
        // Fetch students enrolled in the course
        const studentsResponse = await fetch(`http://localhost:5000/api/teacher/course/${courseId}/students`, {
          credentials: 'include'
        });
        
        if (!studentsResponse.ok) {
          throw new Error('Failed to fetch students');
        }
        
        const studentsData = await studentsResponse.json();
        setStudents(studentsData);
      } catch (error) {
        setError('Error fetching course details');
        console.error('Error fetching course details:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCourseDetails();
  }, [courseId]);

  const handleGradeChange = async (studentId, newGrade) => {
    try {
      const response = await fetch('http://localhost:5000/api/teacher/update-grade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          student_id: studentId,
          course_id: parseInt(courseId),
          value: parseFloat(newGrade)
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Update local state
        setStudents(students.map(student => {
          if (student.id === studentId) {
            return { ...student, grade: parseFloat(newGrade) };
          }
          return student;
        }));
      } else {
        alert(data.error || 'Failed to update grade');
      }
    } catch (error) {
      console.error('Error updating grade:', error);
      alert('Error updating grade');
    }
  };

  const goBack = () => {
    navigate('/teacher');
  };

  if (loading) {
    return <div className="loading">Loading course details...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="course-details">
      <button className="back-btn" onClick={goBack}>← Back to Courses</button>
      
      <h2>{courseInfo ? courseInfo.name : 'Course Details'}</h2>
      {courseInfo && (
        <div className="course-info">
          <p><strong>Enrollment:</strong> {courseInfo.enrolled_count} / {courseInfo.capacity}</p>
        </div>
      )}
      
      <h3>Enrolled Students</h3>
      
      {students.length === 0 ? (
        <p>No students enrolled in this course.</p>
      ) : (
        <table className="students-table">
          <thead>
            <tr>
              <th>Student Name</th>
              <th>Grade</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {students.map(student => (
              <tr key={student.id}>
                <td>{student.username}</td>
                <td>{student.grade}</td>
                <td>
                  <div className="grade-edit">
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      defaultValue={student.grade}
                      onBlur={(e) => handleGradeChange(student.id, e.target.value)}
                    />
                    <button 
                      onClick={(e) => handleGradeChange(
                        student.id, 
                        e.target.previousSibling.value
                      )}
                    >
                      Update
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default CourseDetails;