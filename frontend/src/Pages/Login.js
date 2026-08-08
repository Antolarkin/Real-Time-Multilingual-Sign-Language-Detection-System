import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:3001/user/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password, rememberMe }),
      });

      const data = await response.json();

      if (data.success) {
        // Store authentication token if provided
        if (data.token) {
          localStorage.setItem("authToken", data.token);
        }

        // Store user data if provided
        if (data.user) {
          localStorage.setItem("userData", JSON.stringify(data.user));
        }

        navigate("/sign-kit/home");
      } else {
        setError(data.message || "Login failed. Please try again.");
      }
    } catch (error) {
      setError(
        "An error occurred. Please check your connection and try again."
      );
      console.error("Login error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h2>
            Welcome to <span className="logo-text">SignLingua</span>
          </h2>
          <p>Sign in to access your dashboard</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              disabled={isLoading}
            />
          </div>

          <div className="form-options">
            <div className="remember-me">
              <input
                type="checkbox"
                id="rememberMe"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={isLoading}
              />
              <label htmlFor="rememberMe">Remember me</label>
            </div>
          </div>

          <button type="submit" className="login-button" disabled={isLoading}>
            {isLoading ? "Signing In..." : "Sign In"}
          </button>
        </form>

        <div className="signup-link">
          Don't have an account? <Link to="/signup">Create one</Link>
        </div>
      </div>

      <style jsx>{`
        .login-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          background-color: #f8f9fa;
          font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        }

        .login-card {
          width: 100%;
          max-width: 420px;
          padding: 2.5rem;
          background: white;
          border-radius: 12px;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .login-card:hover {
          box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
        }

        .login-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .login-header h2 {
          color: #2d3748;
          font-weight: 600;
          margin-bottom: 0.5rem;
          font-size: 1.8rem;
        }

        .login-header p {
          color: #718096;
          font-size: 0.95rem;
        }

        .logo-text {
          color: #4e9af1;
          font-weight: 700;
        }

        .error-message {
          background-color: #fee;
          color: #c33;
          padding: 0.75rem;
          border-radius: 6px;
          margin-bottom: 1.5rem;
          border: 1px solid #fcc;
          text-align: center;
        }

        .form-group {
          margin-bottom: 1.5rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          color: #4a5568;
          font-size: 0.95rem;
          font-weight: 500;
        }

        .form-group input {
          width: 100%;
          padding: 0.75rem 1rem;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          font-size: 0.95rem;
          transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }

        .form-group input:focus {
          outline: none;
          border-color: #4e9af1;
          box-shadow: 0 0 0 3px rgba(78, 154, 241, 0.1);
        }

        .form-group input:disabled {
          background-color: #f8f9fa;
          cursor: not-allowed;
        }

        .form-options {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
          font-size: 0.9rem;
        }

        .remember-me {
          display: flex;
          align-items: center;
        }

        .remember-me input {
          margin-right: 0.5rem;
          accent-color: #4e9af1;
        }

        .remember-me input:disabled {
          accent-color: #a0aec0;
        }

        .forgot-password {
          color: #4e9af1;
          text-decoration: none;
          transition: color 0.2s ease;
        }

        .forgot-password:hover {
          color: #3b82f6;
          text-decoration: underline;
        }

        .login-button {
          width: 100%;
          padding: 0.85rem;
          background-color: #4e9af1;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.3s ease, transform 0.2s ease;
          margin-bottom: 1.5rem;
        }

        .login-button:hover:not(:disabled) {
          background-color: #3b82f6;
          transform: translateY(-2px);
        }

        .login-button:active:not(:disabled) {
          transform: translateY(0);
        }

        .login-button:disabled {
          background-color: #a0aec0;
          cursor: not-allowed;
          transform: none;
        }

        .signup-link {
          text-align: center;
          color: #718096;
          font-size: 0.95rem;
        }

        .signup-link a {
          color: #4e9af1;
          text-decoration: none;
          font-weight: 500;
          transition: color 0.2s ease;
        }

        .signup-link a:hover {
          color: #3b82f6;
          text-decoration: underline;
        }

        @media (max-width: 480px) {
          .login-card {
            padding: 1.5rem;
            margin: 0 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default LoginPage;
