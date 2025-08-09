import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import pokeImg from '../images/poke.jpg';

const AuthPage = () => {
  const userRef = useRef();
  const errRef = useRef();
  const navigate = useNavigate();
  
  // State management
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [status, setStatus] = useState({
    error: '',
    loading: false,
    success: false
  });

  // Focus on username input on mount
  useEffect(() => {
    userRef.current.focus();
  }, []);

  // Clear error when inputs change
  useEffect(() => {
    if (status.error) {
      setStatus(prev => ({ ...prev, error: '' }));
    }
  }, [credentials.username, credentials.password]);

  // Handle input changes
  const handleChange = (e) => {
    const { id, value } = e.target;
    setCredentials(prev => ({ ...prev, [id]: value }));
  };

  // Handle login submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus(prev => ({ ...prev, loading: true, error: '' }));
    
    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/login',
        {
          username: credentials.username,
          password: credentials.password
        },
        {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true
        }
      );
      
      // Handle successful login
      setStatus({ error: '', loading: false, success: true });
      
      // Store tokens and roles (if needed)
      const accessToken = response?.data?.accessToken;
      const roles = response?.data?.roles;
      
      // Navigate to main page after successful login
      setTimeout(() => navigate('/mainMenu'), 1000);
      
    } catch (error) {
      let errorMessage = 'Login failed';
      
      if (error.response) {
        if (error.response.status === 401) {
          errorMessage = 'Invalid username or password';
        } else if (error.response.status === 400) {
          errorMessage = 'Missing credentials';
        } else if (error.response.data?.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data?.message) {
          errorMessage = error.response.data.message;
        }
      } else if (error.message === 'Network Error') {
        errorMessage = 'Cannot connect to server';
      }
      
      setStatus(prev => ({ 
        ...prev, 
        error: errorMessage,
        loading: false 
      }));
      
      // Safely handle focus
      if (errRef.current) {
        errRef.current.focus();
      }
    }
  };

  // Styles defined as JavaScript object
  const styles = {
    pageContainer: {
      minHeight: '100vh',
      backgroundImage: `url(${pokeImg})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
    },
    authContainer: {
      maxWidth: '400px',
      width: '100%',
      padding: '30px',
      backgroundColor: 'rgba(255, 255, 255, 0.92)',
      borderRadius: '10px',
      boxShadow: '0 8px 30px rgba(0, 0, 0, 0.3)',
      backdropFilter: 'blur(10px)',
    },
    buttonGroup: {
      display: 'flex',
      marginBottom: '25px',
      gap: '10px',
    },
    button: {
      flex: 1,
      padding: '12px',
      border: 'none',
      background: '#e0e0e0',
      cursor: 'pointer',
      fontSize: '16px',
      fontWeight: '600',
      transition: 'all 0.3s ease',
      borderRadius: '6px',
    },
    activeButton: {
      background: '#1a73e8',
      color: 'white',
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
    },
    authForm: {
      display: 'flex',
      flexDirection: 'column',
    },
    header: {
      marginTop: '0',
      marginBottom: '20px',
      textAlign: 'center',
      color: '#202124',
    },
    formGroup: {
      marginBottom: '18px',
      position: 'relative',
    },
    label: {
      display: 'block',
      marginBottom: '8px',
      fontWeight: '500',
      color: '#444',
    },
    input: {
      width: '100%',
      padding: '12px',
      border: '1px solid #ddd',
      borderRadius: '8px',
      fontSize: '16px',
      transition: 'border 0.3s',
      boxSizing: 'border-box',
    },
    submitButton: {
      padding: '14px',
      background: '#1a73e8',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      cursor: 'pointer',
      fontSize: '16px',
      fontWeight: '600',
      marginTop: '10px',
      transition: 'background 0.3s',
      boxShadow: '0 4px 6px rgba(26, 115, 232, 0.3)',
      position: 'relative',
    },
    loadingButton: {
      backgroundColor: '#6c757d',
    },
    errorMessage: {
      padding: '10px',
      marginBottom: '15px',
      backgroundColor: '#f8d7da',
      color: '#721c24',
      borderRadius: '4px',
      border: '1px solid #f5c6cb',
      textAlign: 'center',
      // Make focusable
      outline: 'none',
    },
    successMessage: {
      padding: '10px',
      marginBottom: '15px',
      backgroundColor: '#d4edda',
      color: '#155724',
      borderRadius: '4px',
      border: '1px solid #c3e6cb',
      textAlign: 'center',
    },
  };

  return (
    <div style={styles.pageContainer}>
      <div style={styles.authContainer}>
        <div style={styles.buttonGroup}>
          <button
            onClick={() => navigate('/login')}
            style={{
              ...styles.button,
              ...styles.activeButton
            }}
          >
            Login
          </button>
          <button
            onClick={() => navigate('/register')}
            style={styles.button}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} style={styles.authForm}>
          <h2 style={styles.header}>Login</h2>
          
          {/* Error Message - Now focusable */}
          {status.error && (
            <div 
              ref={errRef}
              tabIndex={-1} // Make focusable
              style={styles.errorMessage} 
              aria-live="assertive"
            >
              {status.error}
            </div>
          )}
          
          {/* Success Message */}
          {status.success && (
            <div style={styles.successMessage}>
              Login successful! Redirecting...
            </div>
          )}
          
          <div style={styles.formGroup}>
            <label htmlFor="username" style={styles.label}>
              Username:
            </label>
            <input
              type="text"
              required
              id="username"
              ref={userRef}
              onChange={handleChange}
              value={credentials.username}
              style={styles.input}
              autoComplete="username"
              disabled={status.loading || status.success}
            />
          </div>
          
          <div style={styles.formGroup}>
            <label htmlFor="password" style={styles.label}>
              Password:
            </label>
            <input
              type="password"
              required
              id="password"
              onChange={handleChange}
              value={credentials.password}
              style={styles.input}
              autoComplete="current-password"
              disabled={status.loading || status.success}
            />
          </div>
          
          <button 
            type="submit"
            style={{
              ...styles.submitButton,
              ...(status.loading ? styles.loadingButton : {})
            }}
            disabled={status.loading || status.success}
          >
            {status.loading ? 'Authenticating...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AuthPage;