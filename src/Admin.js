import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Admin.css';

const API_BASE = process.env.REACT_APP_API_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:5000');

function Admin() {
  const [employees, setEmployees] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const token = localStorage.getItem('token');

  const fetchEmployees = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/employees`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setEmployees(response.data);
    } catch (err) {
      setError('Failed to fetch employees');
    }
  }, [token]);

  useEffect(() => {
    if (!token) {
      navigate('/');
      return;
    }
    fetchEmployees();
  }, [token, navigate, fetchEmployees]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    console.log('Form Data:', formData);
    
    try {
      const response = await axios.post(
        `${API_BASE}/api/add-employee`,
        formData,
        { 
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          } 
        }
      );

      console.log('Success Response:', response.data);
      setSuccess('Employee added successfully!');
      setFormData({ name: '', email: '', password: '' });
      fetchEmployees();
    } catch (err) {
      console.log('Error Response:', err.response);
      setError(err.response?.data?.error || 'Failed to add employee');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteEmployee = async (empId) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        await axios.delete(`${API_BASE}/api/delete-employee/${empId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setSuccess('Employee deleted successfully!');
        fetchEmployees();
      } catch (err) {
        setError('Failed to delete employee');
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  return (
    <div>
      <header className="navbar">
        <h2 className="brand">Forbes Marshall - Admin Panel</h2>
        <button className="logout-btn" onClick={handleLogout}>Logout</button>
      </header>

      <div className="admin-container">
        <div className="admin-content">
          <div className="add-employee-section">
            <h2>Add New Employee</h2>
            <form onSubmit={handleAddEmployee}>
              <div className="form-group">
                <label>Employee Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Enter employee name"
                  required
                />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Enter email"
                  required
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Enter password"
                  required
                />
              </div>

              {error && <div className="error-message">{error}</div>}
              {success && <div className="success-message">{success}</div>}

              <button type="submit" className="btn-add" disabled={loading}>
                {loading ? 'Adding...' : 'Add Employee'}
              </button>
            </form>
          </div>

          <div className="employees-list-section">
            <h2>Employees List</h2>
            {employees.length === 0 ? (
              <p className="no-employees">No employees added yet</p>
            ) : (
              <div className="employees-table">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {employees.map((emp) => (
                      <tr key={emp.id}>
                        <td>{emp.id}</td>
                        <td>{emp.name}</td>
                        <td>{emp.email}</td>
                        <td>
                          <button
                            className="btn-delete"
                            onClick={() => handleDeleteEmployee(emp.id)}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Admin;
