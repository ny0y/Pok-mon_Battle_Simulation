// src/AuthPage.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import pokeImg from '../images/poke.jpg';


const AuthPage = () => {
  const [showLogin, setShowLogin] = useState(true);
  const navigate = useNavigate();
  
  const handleLoginSubmit = (e) => {
    e.preventDefault();
    // In a real app, add authentication logic here
    console.log('Login successful');
    navigate('/main');
  };

  const handleRegisterSubmit = (e) => {
    e.preventDefault();
    // In a real app, add registration logic here
    console.log('Registration successful');
    navigate('/main');
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
    }
  };

  return (
    <div style={styles.pageContainer}>
      <div style={styles.authContainer}>
        <div style={styles.buttonGroup}>
          <button 
            onClick={() => setShowLogin(true)}
            style={{
              ...styles.button,
              ...(showLogin ? styles.activeButton : {})
            }}
          >
            Login
          </button>
          <button 
            onClick={() => setShowLogin(false)}
            style={{
              ...styles.button,
              ...(!showLogin ? styles.activeButton : {})
            }}
          >
            Register
          </button>
        </div>

        {showLogin ? (
          <form onSubmit={handleLoginSubmit} style={styles.authForm}>
            <h2 style={styles.header}>Login</h2>
            <div style={styles.formGroup}>
              <label style={styles.label}>Email:</label>
              <input 
                type="email" 
                required 
                style={styles.input}
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Password:</label>
              <input 
                type="password" 
                required 
                style={styles.input}
              />
            </div>
            <button type="submit" style={styles.submitButton}>Login</button>
          </form>
        ) : (
          <form onSubmit={handleRegisterSubmit} style={styles.authForm}>
            <h2 style={styles.header}>Register</h2>
            <div style={styles.formGroup}>
              <label style={styles.label}>Name:</label>
              <input 
                type="text" 
                required 
                style={styles.input}
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Email:</label>
              <input 
                type="email" 
                required 
                style={styles.input}
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Password:</label>
              <input 
                type="password" 
                required 
                style={styles.input}
              />
            </div>
            <button type="submit" style={styles.submitButton}>Register</button>
          </form>
        )}
      </div>
    </div>
  );
};

export default AuthPage;