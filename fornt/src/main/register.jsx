import { useRef, useState, useEffect } from "react";
import axios from 'axios';
import { useNavigate } from "react-router-dom";
import pokeImg from '../images/poke.jpg';

// Constants
const USER_REGEX = /^[A-Za-z][A-Za-z0-9-_]{3,23}$/;
const PWD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,24}$/;
const REGISTER_URL = 'http://127.0.0.1:8000/register';

const Register = () => {
    const userRef = useRef();
    const errRef = useRef(); 
    const navigate = useNavigate();

    // State variables
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });
    const [validations, setValidations] = useState({
        username: false,
        password: false
    });
    const [focusStates, setFocusStates] = useState({
        username: false,
        password: false
    });
    const [status, setStatus] = useState({
        error: '',
        success: false,
        loading: false
    });

    // Focus on username input on mount
    useEffect(() => {
        userRef.current.focus();
    }, []);

    // Validate username
    useEffect(() => {
        const isValid = USER_REGEX.test(formData.username);
        setValidations(prev => ({ ...prev, username: isValid }));
    }, [formData.username]);

    // Validate password
    useEffect(() => {
        const isValid = PWD_REGEX.test(formData.password);
        setValidations(prev => ({ ...prev, password: isValid }));
    }, [formData.password]);

    // Clear error when inputs change
    useEffect(() => {
        if (status.error) {
            setStatus(prev => ({ ...prev, error: '' }));
        }
    }, [formData.username, formData.password]);

    // Handle input changes
    const handleChange = (e) => {
        const { id, value } = e.target;
        setFormData(prev => ({ ...prev, [id]: value }));
    };

    // Form submission
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Extra validation check
        const isUsernameValid = USER_REGEX.test(formData.username);
        const isPasswordValid = PWD_REGEX.test(formData.password);
        
        if (!isUsernameValid || !isPasswordValid) {
            setStatus(prev => ({ ...prev, error: 'Invalid credentials' }));
            return;
        }
        
        setStatus(prev => ({ ...prev, loading: true }));
        
        try {
            const response = await axios.post(
                REGISTER_URL,
                {
                    username: formData.username,
                    password: formData.password
                },
                {
                    headers: { 'Content-Type': 'application/json' }
                }
            );

            // Handle successful registration
            if (response.status === 200 || response.status === 201) {
                setStatus({ success: true, loading: false, error: '' });
                setFormData({ username: '', password: '' });
                
                // Redirect to login after 2 seconds
                setTimeout(() => navigate('/Auther'), 2000);
            } else {
                throw new Error('Registration failed');
            }
            
        } catch (err) {
            let errorMessage = 'Registration failed. Please try again.';
            
            if (err.response) {
                if (err.response.status === 409) {
                    errorMessage = 'Username is already taken';
                } else if (err.response.data?.detail) {
                    // Handle Django-style errors
                    errorMessage = err.response.data.detail;
                } else if (err.response.data?.message) {
                    errorMessage = err.response.data.message;
                } else if (err.response.status) {
                    errorMessage = `Server error: ${err.response.status}`;
                }
            } else if (err.message === 'Network Error') {
                errorMessage = 'Cannot connect to server';
            }
            
            setStatus(prev => ({ 
                ...prev, 
                error: errorMessage,
                loading: false 
            }));
            
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
        validInput: {
            borderColor: '#28a745',
        },
        invalidInput: {
            borderColor: '#dc3545',
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
        inputHint: {
            marginTop: '0.5rem',
            padding: '0.5rem',
            backgroundColor: '#f8f9fa',
            borderRadius: '4px',
            fontSize: '0.85rem',
            color: '#6c757d',
        },
        loginPrompt: {
            marginTop: '1.5rem',
            textAlign: 'center',
            color: '#6c757d',
        },
        loginLink: {
            color: '#007bff',
            textDecoration: 'none',
            fontWeight: '500',
        },
        successContainer: {
            textAlign: 'center',
            padding: '2rem',
            backgroundColor: 'rgba(255, 255, 255, 0.92)',
            borderRadius: '10px',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.3)',
            backdropFilter: 'blur(10px)',
            maxWidth: '500px',
            margin: '0 auto',
        },
        successHeader: {
            color: '#155724',
            marginBottom: '1rem',
        },
        successButton: {
            display: 'inline-block',
            marginTop: '1.5rem',
            padding: '0.75rem 1.5rem',
            backgroundColor: '#28a745',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px',
            fontWeight: '600',
            transition: 'background-color 0.3s',
        }
    };

    // Render success state
    if (status.success) {
        return (
            <div style={styles.pageContainer}>
                <div style={styles.successContainer}>
                    <h2 style={styles.successHeader}>Registration Successful!</h2>
                    <p>Your account has been created successfully</p>
                    <p>Redirecting to login page...</p>
                    <a 
                        href="/Auther" 
                        style={styles.successButton}
                        onClick={(e) => {
                            e.preventDefault();
                            navigate('/Auther');
                        }}
                    >
                        Go to Login
                    </a>
                </div>
            </div>
        );
    }

    // Render form
    return (
        <div style={styles.pageContainer}>
            <div style={styles.authContainer}>
                <div style={styles.buttonGroup}>
                    <button
                        onClick={() => navigate('/Auther')}
                        style={styles.button}
                    >
                        Login
                    </button>
                    <button
                        onClick={() => navigate('/register')}
                        style={{
                            ...styles.button,
                            ...styles.activeButton
                        }}
                    >
                        Register
                    </button>
                </div>

                <form onSubmit={handleSubmit} style={styles.authForm}>
                    <h2 style={styles.header}>Create Account</h2>
                    
                    {/* Error Message */}
                    {status.error && (
                        <div 
                            ref={errRef}
                            tabIndex={-1}
                            style={styles.errorMessage} 
                            aria-live="assertive"
                        >
                            {status.error}
                        </div>
                    )}
                    
                    {/* Username Field */}
                    <div style={styles.formGroup}>
                        <label htmlFor="username" style={styles.label}>
                            Username:
                        </label>
                        <input
                            type="text"
                            id="username"
                            ref={userRef}
                            autoComplete="off"
                            value={formData.username}
                            onChange={handleChange}
                            required
                            style={{
                                ...styles.input,
                                ...(formData.username && 
                                    (validations.username ? styles.validInput : styles.invalidInput))
                            }}
                            onFocus={() => setFocusStates(prev => ({ ...prev, username: true }))}
                            onBlur={() => setFocusStates(prev => ({ ...prev, username: false }))}
                            disabled={status.loading}
                        />
                        {focusStates.username && formData.username && !validations.username && (
                            <div style={styles.inputHint}>
                                4-24 characters. Must begin with a letter.<br />
                                Letters, numbers, underscores, hyphens allowed.
                            </div>
                        )}
                    </div>

                    {/* Password Field */}
                    <div style={styles.formGroup}>
                        <label htmlFor="password" style={styles.label}>
                            Password:
                        </label>
                        <input
                            type="password"
                            id="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            style={{
                                ...styles.input,
                                ...(formData.password && 
                                    (validations.password ? styles.validInput : styles.invalidInput))
                            }}
                            onFocus={() => setFocusStates(prev => ({ ...prev, password: true }))}
                            onBlur={() => setFocusStates(prev => ({ ...prev, password: false }))}
                            disabled={status.loading}
                        />
                        {focusStates.password && formData.password && !validations.password && (
                            <div style={styles.inputHint}>
                                8-24 characters. Must include:<br />
                                • Uppercase & lowercase letters<br />
                                • A number<br />
                                • Special character (!@#$%^&*)
                            </div>
                        )}
                    </div>

                    <button 
                        type="submit"
                        style={{
                            ...styles.submitButton,
                            ...(status.loading && styles.loadingButton)
                        }}
                        disabled={!validations.username || !validations.password || status.loading}
                    >
                        {status.loading ? 'Creating Account...' : 'Register'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Register;