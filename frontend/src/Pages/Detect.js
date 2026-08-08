import React, { useState, useEffect } from "react";

const Detect = () => {
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectedChars, setDetectedChars] = useState([]);
  const [currentChar, setCurrentChar] = useState("");
  const [language, setLanguage] = useState("ASL");
  const [confidence, setConfidence] = useState(0);
  const [sessionId, setSessionId] = useState("");
  const [isAutoDetection, setIsAutoDetection] = useState(true);
  const [inputText, setInputText] = useState("");
  const [isFinalized, setIsFinalized] = useState(false);

  // Polling interval for detection status
  useEffect(() => {
    let intervalId;

    if (isDetecting) {
      intervalId = setInterval(async () => {
        try {
          const response = await fetch(
            "http://127.0.0.1:8000/detection_status",
            {
              method: "GET",
              headers: {
                accept: "application/json",
              },
            }
          );

          if (!response.ok) {
            throw new Error("Network response was not ok");
          }

          const data = await response.json();

          // Update current character display
          if (data.last_detected_char && data.last_detected_char !== "?") {
            setCurrentChar(data.last_detected_char);
            setConfidence(data.confidence);
          }

          // Use word_buffer from backend as single source of truth
          if (data.word_buffer !== undefined) {
            setInputText(data.word_buffer);
          }

          if (data.session_id) setSessionId(data.session_id);
          if (data.auto_detection_enabled !== undefined)
            setIsAutoDetection(data.auto_detection_enabled);

          if (data.final_sentence) {
            setDetectedChars((prev) => [...prev, data.final_sentence]);
            setIsFinalized(true);
          }
        } catch (error) {
          console.error("Error fetching detection status:", error);
        }
      }, 500);
    }

    return () => clearInterval(intervalId);
  }, [isDetecting, isFinalized]);

  const startDetection = async () => {
    try {
      setIsDetecting(true);
      setDetectedChars([]);
      setCurrentChar("");
      setInputText("");
      setIsFinalized(false);

      const response = await fetch("http://127.0.0.1:8000/start_detection", {
        method: "POST",
        headers: {
          accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          language: language,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start detection");
      }
    } catch (error) {
      console.error("Error:", error);
      setIsDetecting(false);
    }
  };

const stopDetection = async () => {
  try {
    // First: Stop detection
    await fetch("http://127.0.0.1:8000/stop_detection", {
      method: "POST",
      headers: {
        accept: "application/json",
      },
    });

    // Second: Clear session
    await fetch("http://127.0.0.1:8000/clear_session", {
      method: "DELETE",
      headers: {
        accept: "application/json",
      },
    });
  } catch (error) {
    console.error("Error stopping detection or clearing session:", error);
  } finally {
    setIsDetecting(false);
    setCurrentChar("");
  }
};

  const handleBackspace = async () => {
    try {
      await fetch("http://127.0.0.1:8000/backspace", {
        method: "POST",
        headers: {
          accept: "application/json",
        },
      });
      setInputText((prev) => prev.slice(0, -1));
    } catch (error) {
      console.error("Error handling backspace:", error);
    }
  };

  const handleEnter = async () => {
    try {
      await fetch("http://127.0.0.1:8000/enter", {
        method: "POST",
        headers: {
          accept: "application/json",
        },
      });
      if (inputText) {
        setDetectedChars((prev) => [...prev, inputText]);
        setInputText("");
        setIsFinalized(true);
      }
    } catch (error) {
      console.error("Error handling enter:", error);
    }
  };

  const handleInputChange = (e) => {
    setInputText(e.target.value);
  };

  return (
    <div className="detect-container">
      <div className="detect-header">
        <h1>Sign Language Detection System</h1>
        <p className="subtitle">Real-time character recognition</p>
      </div>

      <div className="detect-content">
        <div className="status-panel">
          <div className="status-card">
            <h3>Detection Status</h3>
            <div className="status-indicator">
              <span
                className={`status-dot ${isDetecting ? "active" : ""}`}
              ></span>
              <span>{isDetecting ? "ACTIVE" : "INACTIVE"}</span>
            </div>
            <div className="status-details">
              <p>
                <strong>Language:</strong> {language}
              </p>
              <p>
                <strong>Session ID:</strong> {sessionId || "Not started"}
              </p>
              <p>
                <strong>Auto Detection:</strong>{" "}
                {isAutoDetection ? "ON" : "OFF"}
              </p>
            </div>
          </div>

          <div className="current-character">
            <h3>Current Character</h3>
            <div className="character-display">
              {currentChar || (
                <span className="placeholder-char">Waiting for input...</span>
              )}
            </div>
            <div className="confidence-meter">
              <div className="confidence-label">Confidence: {confidence}%</div>
              <div className="confidence-bar">
                <div
                  className="confidence-fill"
                  style={{ width: `${confidence}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div className="input-section">
          <h3>Current Input</h3>
          <div className="input-control-group">
            <div className="input-container">
              <input
                type="text"
                value={inputText}
                onChange={handleInputChange}
                placeholder="Characters will appear here as detected..."
                className="text-input"
                disabled={isFinalized}
              />
              {isFinalized && (
                <button
                  className="edit-button"
                  onClick={() => setIsFinalized(false)}
                >
                  <i className="fas fa-edit"></i> Detect Again
                </button>
              )}
            </div>
            {isDetecting && (
              <div className="input-action-buttons">
                <button
                  className="input-action-button backspace-button"
                  onClick={handleBackspace}
                >
                  <i className="fas fa-backspace"></i> Backspace
                </button>
                <button
                  className="input-action-button enter-button"
                  onClick={handleEnter}
                >
                  <i className="fas fa-arrow-right"></i> Enter
                </button>
              </div>
            )}
          </div>
          <div className="input-instructions">
            <p>
              <i className="fas fa-info-circle"></i> Characters appear
              automatically as detected
            </p>
          </div>
        </div>

        <div className="text-output">
          <h3>Detected Text</h3>
          <div className="text-display">
            {detectedChars.length > 0 ? (
              <div className="detected-words">
                {detectedChars.map((word, index) => (
                  <span key={index} className="detected-word">
                    {word}
                  </span>
                ))}
              </div>
            ) : (
              <p className="placeholder-text">
                Your finalized text will appear here
              </p>
            )}
          </div>
        </div>

        <div className="control-panel">
          <div className="language-selector">
            <label htmlFor="language">Detection Language:</label>
            <select
              id="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              disabled={isDetecting}
            >
              <option value="ASL">American Sign Language (ASL)</option>
              <option value="ISL">Indian Sign Language (ISL)</option>
              <option value="TSL">Tamil Sign Language (TSL)</option>
            </select>
          </div>

          <div className="action-buttons">
            {!isDetecting ? (
              <button
                className="action-button start-button"
                onClick={startDetection}
              >
                <i className="fas fa-play"></i> Start Detection
              </button>
            ) : (
              <button
                className="action-button stop-button"
                onClick={stopDetection}
              >
                <i className="fas fa-stop"></i> Stop Detection
              </button>
            )}
          </div>
        </div>
      </div>


    </div>
  );
};

export default Detect;
