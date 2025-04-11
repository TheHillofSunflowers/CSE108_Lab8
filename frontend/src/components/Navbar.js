import React from 'react';
import { Link } from 'react-router-dom';

function Navbar({ user, onLogout }) {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">School Enrollment System</Link>
      </div>
      {user ? (
        <div className="navbar-menu">
          <span className="navbar-item">Logged in as {user.username} ({user.role})</span>
          <button className="logout-btn" onClick={onLogout}>Logout</button>
        </div>
      ) : (
        <div className="navbar-menu">
          <Link to="/login" className="navbar-item">Login</Link>
        </div>
      )}
    </nav>
  );
}

export default Navbar;