import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const SignupPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeTerms: false,
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Basic validation
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    if (!formData.agreeTerms) {
      setError("You must agree to the terms and conditions");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:3001/user/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.firstName,
          email: formData.email,
          password: formData.password,
        }),
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

        navigate("/");
      } else {
        setError(data.message || "Signup failed. Please try again.");
      }
    } catch (error) {
      setError(
        "An error occurred. Please check your connection and try again."
      );
      console.error("Signup error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-card">
        <div className="signup-header">
          <h2>
            Create your <span className="logo-text">SignLingua</span> account
          </h2>
          <p>Get started with our Indian Sign Language toolkit</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="signup-form">
          <div className="name-fields">
            <div className="form-group">
              <label htmlFor="firstName">First Name</label>
              <input
                type="text"
                id="firstName"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                placeholder="Enter your first name"
                required
                disabled={isLoading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="lastName">Last Name</label>
              <input
                type="text"
                id="lastName"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                placeholder="Enter your last name"
                required
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
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
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Create a password"
              required
              disabled={isLoading}
            />
            <div className="password-hint">Must be at least 8 characters</div>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm your password"
              required
              disabled={isLoading}
            />
          </div>

          <div className="checkbox-group">
            <input
              type="checkbox"
              id="agreeTerms"
              name="agreeTerms"
              checked={formData.agreeTerms}
              onChange={handleChange}
              disabled={isLoading}
            />
            <label htmlFor="agreeTerms">
              I agree to the <a href="/terms">Terms of Service</a> and{" "}
              <a href="/privacy">Privacy Policy</a>
            </label>
          </div>

          <button type="submit" className="signup-button" disabled={isLoading}>
            {isLoading ? "Creating Account..." : "Create Account"}
          </button>
        </form>

        <div className="login-link">
          Already have an account? <Link to="/">Sign in</Link>
        </div>
      </div>

      <style jsx>{`
        .signup-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          background-color: #f8f9fa;
          font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
          padding: 1rem;
        }

        .signup-card {
          width: 100%;
          max-width: 480px;
          padding: 2.5rem;
          background: white;
          border-radius: 12px;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .signup-card:hover {
          box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
        }

        .signup-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .signup-header h2 {
          color: #2d3748;
          font-weight: 600;
          margin-bottom: 0.5rem;
          font-size: 1.8rem;
        }

        .signup-header p {
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

        .name-fields {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
          margin-bottom: 1.5rem;
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

        .password-hint {
          font-size: 0.8rem;
          color: #718096;
          margin-top: 0.25rem;
        }

        .checkbox-group {
          display: flex;
          align-items: center;
          margin: 1.5rem 0;
        }

        .checkbox-group input {
          width: auto;
          margin-right: 0.75rem;
          accent-color: #4e9af1;
        }

        .checkbox-group input:disabled {
          accent-color: #a0aec0;
        }

        .checkbox-group label {
          margin-bottom: 0;
          font-size: 0.9rem;
          color: #4a5568;
        }

        .checkbox-group a {
          color: #4e9af1;
          text-decoration: none;
          transition: color 0.2s ease;
        }

        .checkbox-group a:hover {
          color: #3b82f6;
          text-decoration: underline;
        }

        .signup-button {
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

        .signup-button:hover:not(:disabled) {
          background-color: #3b82f6;
          transform: translateY(-2px);
        }

        .signup-button:active:not(:disabled) {
          transform: translateY(0);
        }

        .signup-button:disabled {
          background-color: #a0aec0;
          cursor: not-allowed;
          transform: none;
        }

        .login-link {
          text-align: center;
          color: #718096;
          font-size: 0.95rem;
        }

        .login-link a {
          color: #4e9af1;
          text-decoration: none;
          font-weight: 500;
          transition: color 0.2s ease;
        }

        .login-link a:hover {
          color: #3b82f6;
          text-decoration: underline;
        }

        @media (max-width: 600px) {
          .name-fields {
            grid-template-columns: 1fr;
          }

          .signup-card {
            padding: 1.75rem;
          }
        }

        @media (max-width: 480px) {
          .signup-card {
            padding: 1.5rem;
          }
        }
      `}</style>
    </div>
  );
};

export default SignupPage;
