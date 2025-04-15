import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './components/Login';
import StudentDashboard from './components/StudentDashboard';
import TeacherDashboard from './components/TeacherDashboard';
import CourseDetails from './components/CourseDetails';
import Navbar from './components/Navbar';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const checkAuth = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/user', {
          credentials: 'include'
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.authenticated) {
            setUser(data.user);
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogout = async () => {
    try {
      await fetch('http://localhost:5000/api/logout', {
        method: 'POST',
        credentials: 'include'
      });
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <Router>
      <div className="app">
        <Navbar user={user} onLogout={handleLogout} />
        <div className="container">
          <Routes>
            <Route path="/" element={
                user ? (
                  user.role === 'student' ? (
                    <Navigate to="/student" replace />
                  ) : user.role === 'teacher' ? (
                    <Navigate to="/teacher" replace />
                  ) : user.role === 'admin' ? (
                    <Navigate to="/admin" replace />
                  ) : (
                    <Navigate to="/login" replace />
                  )
                ) : (
                  <Navigate to="/login" replace />
                )
              } />
            <Route path="/login" element={
              user ? <Navigate to="/" replace /> : <Login setUser={setUser} />
            } />
            <Route path="/student" element={
              user && user.role === 'student' ? (
                <StudentDashboard user={user} />
              ) : (
                <Navigate to="/login" replace />
              )
            } />
            <Route path="/teacher" element={
              user && user.role === 'teacher' ? (
                <TeacherDashboard user={user} />
              ) : (
                <Navigate to="/login" replace />
              )
            } />
            
            <Route path="/teacher/course/:courseId" element={
              user && user.role === 'teacher' ? (
                <CourseDetails user={user} />
              ) : (
                <Navigate to="/login" replace />
              )
            } />
            
            <Route path="/admin" element={
              user && user.role === 'admin' ? (
                window.location.href = "http://localhost:5000/admin", null
              ) : (
                <Navigate to="/login" replace />
              )
            } />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;