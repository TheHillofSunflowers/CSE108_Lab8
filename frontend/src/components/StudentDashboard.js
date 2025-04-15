import React, { useState, useEffect } from 'react';

function StudentDashboard({ user }) {
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [availableCourses, setAvailableCourses] = useState([]);
  const [allCourses, setAllCourses] = useState([]);
  const [activeTab, setActiveTab] = useState('enrolled');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchCourses = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/student/courses', {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch courses');
      }
      
      const data = await response.json();
      
      setEnrolledCourses(data.enrolled_courses);
      setAvailableCourses(data.available_courses);
      
      // Combine all courses for the Add Courses tab
      setAllCourses([...data.enrolled_courses, ...data.available_courses]);
    } catch (error) {
      setError('Error fetching courses');
      console.error('Error fetching courses:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const handleEnroll = async (courseId) => {
    try {
      const response = await fetch('http://localhost:5000/api/student/enroll', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ course_id: courseId })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Update the course enrollment count in all lists
        const updatedAllCourses = allCourses.map(course => {
          if (course.id === courseId) {
            // Update enrollment count and enrolled status
            return {
              ...course,
              enrolled: true,
              enrolled_count: course.enrolled_count + 1
            };
          }
          return course;
        });
        setAllCourses(updatedAllCourses);
        
        // Move course from available to enrolled
        const course = availableCourses.find(c => c.id === courseId);
        if (course) {
          const updatedCourse = {
            ...course,
            enrolled: true,
            enrolled_count: course.enrolled_count + 1
          };
          
          setEnrolledCourses([...enrolledCourses, updatedCourse]);
          setAvailableCourses(availableCourses.filter(c => c.id !== courseId));
        }
      } else {
        alert(data.error || 'Failed to enroll in course');
      }
    } catch (error) {
      console.error('Error enrolling in course:', error);
      alert('Error enrolling in course');
    }
  };

  const handleDrop = async (courseId) => {
    try {
      const response = await fetch('http://localhost:5000/api/student/drop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ course_id: courseId })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Update the course enrollment count in all lists
        const updatedAllCourses = allCourses.map(course => {
          if (course.id === courseId) {
            // Update enrollment count and enrolled status
            return {
              ...course,
              enrolled: false,
              enrolled_count: Math.max(0, course.enrolled_count - 1) // Prevent negative count
            };
          }
          return course;
        });
        setAllCourses(updatedAllCourses);
        
        // Move course from enrolled to available
        const course = enrolledCourses.find(c => c.id === courseId);
        if (course) {
          const updatedCourse = {
            ...course,
            enrolled: false,
            enrolled_count: Math.max(0, course.enrolled_count - 1) // Prevent negative count
          };
          
          setAvailableCourses([...availableCourses, updatedCourse]);
          setEnrolledCourses(enrolledCourses.filter(c => c.id !== courseId));
        }
      } else {
        alert(data.error || 'Failed to drop course');
      }
    } catch (error) {
      console.error('Error dropping course:', error);
      alert('Error dropping course');
    }
  };

  if (loading) {
    return <div className="loading">Loading courses...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="student-dashboard">
      <h2>Student Dashboard</h2>
      <div className="tabs">
        <button 
          className={activeTab === 'enrolled' ? 'active' : ''} 
          onClick={() => setActiveTab('enrolled')}
        >
          My Courses
        </button>
        <button 
          className={activeTab === 'available' ? 'active' : ''} 
          onClick={() => setActiveTab('available')}
        >
          Add Courses
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'enrolled' ? (
          <>
            <h3>My Enrolled Courses</h3>
            {enrolledCourses.length === 0 ? (
              <p>You are not enrolled in any courses yet.</p>
            ) : (
              <table className="courses-table">
                <thead>
                  <tr>
                    <th>Course Name</th>
                    <th>Teacher</th>
                    <th>Time</th>
                    <th>Enrollment</th>
                    <th>Grade</th>
                  </tr>
                </thead>
                <tbody>
                  {enrolledCourses.map(course => (
                    <tr key={course.id}>
                      <td>{course.name}</td>
                      <td>{course.teacher_name}</td>
                      <td>{course.timeslot}</td>
                      <td>{course.enrolled_count}/{course.capacity}</td>
                      <td>{course.grade !== undefined ? course.grade : 'Not graded'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        ) : (
          <>
            <h3>All Courses</h3>
            {allCourses.length === 0 ? (
              <p>No courses available.</p>
            ) : (
              <table className="courses-table">
                <thead>
                  <tr>
                    <th>Course Name</th>
                    <th>Teacher</th>
                    <th>Time</th>
                    <th>Enrollment</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {allCourses.map(course => {
                    const isEnrolled = course.enrolled;
                    
                    return (
                      <tr key={course.id}>
                        <td>{course.name}</td>
                        <td>{course.teacher_name}</td>
                        <td>{course.timeslot}</td>
                        <td>{course.enrolled_count}/{course.capacity}</td>
                        <td>
                          {isEnrolled ? (
                            <button 
                              className="drop-btn"
                              onClick={() => handleDrop(course.id)}
                            >
                              Drop
                            </button>
                          ) : (
                            <button 
                              className="enroll-btn"
                              onClick={() => handleEnroll(course.id)}
                              disabled={course.enrolled_count >= course.capacity}
                            >
                              {course.enrolled_count >= course.capacity ? 'Full' : 'Enroll'}
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default StudentDashboard;