import React, { useState, useEffect, useRef } from "react";
import Webcam from "react-webcam";

const SignLanguageDetector = () => {
  const [language, setLanguage] = useState("ASL");
  const [isDetecting, setIsDetecting] = useState(false);
  const [status, setStatus] = useState(null);
  const [detectedText, setDetectedText] = useState("");
  const [languages, setLanguages] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [facingMode, setFacingMode] = useState("user"); // 'user' for front camera, 'environment' for rear
  const webcamRef = useRef(null);
  const detectionIntervalRef = useRef(null);
  const frameCaptureIntervalRef = useRef(null);

  // Fetch supported languages on component mount
  useEffect(() => {
    const fetchSupportedLanguages = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/supported_languages"
        );
        const data = await response.json();
        setLanguages(data.supported_languages);
      } catch (error) {
        console.error("Error fetching supported languages:", error);
      }
    };

    fetchSupportedLanguages();
    return () => {
      clearIntervals();
    };
  }, []);

  // Fetch model info when language changes
  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/model_info/${language}`
        );
        const data = await response.json();
        setModelInfo(data);
      } catch (error) {
        console.error("Error fetching model info:", error);
      }
    };

    fetchInfo();
  }, [language]);

  const clearIntervals = () => {
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
      detectionIntervalRef.current = null;
    }
    if (frameCaptureIntervalRef.current) {
      clearInterval(frameCaptureIntervalRef.current);
      frameCaptureIntervalRef.current = null;
    }
  };

  const toggleCamera = () => {
    setIsCameraActive(!isCameraActive);
    if (isCameraActive) {
      clearIntervals();
    }
  };

  const switchCamera = () => {
    setFacingMode(facingMode === "user" ? "environment" : "user");
  };

  const captureFrame = async () => {
    if (!webcamRef.current || !isDetecting) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    try {
      const response = await fetch("http://127.0.0.1:8000/process_frame", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image: imageSrc.split(",")[1], // Remove data URL prefix
          language: language,
        }),
      });
      const data = await response.json();
      setStatus(data);

      if (data.completed) {
        setIsDetecting(false);
        fetchDetectedText();
      }
    } catch (error) {
      console.error("Error processing frame:", error);
    }
  };

  const startDetection = async () => {
    if (!isCameraActive) {
      alert("Please activate the camera first");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/start_detection", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ language }),
      });
      const data = await response.json();
      setIsDetecting(true);

      // Start sending frames to the server
      frameCaptureIntervalRef.current = setInterval(captureFrame, 200); // 5 FPS

      // Start polling for status updates
      detectionIntervalRef.current = setInterval(async () => {
        try {
          const statusResponse = await fetch(
            "http://127.0.0.1:8000/detection_status"
          );
          const statusData = await statusResponse.json();
          setStatus(statusData);

          if (statusData.completed) {
            setIsDetecting(false);
            fetchDetectedText();
            clearIntervals();
          }
        } catch (error) {
          console.error("Error fetching status:", error);
        }
      }, 1000);

      console.log("Detection started:", data);
    } catch (error) {
      console.error("Error starting detection:", error);
    }
  };

  const stopDetection = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/stop_detection", {
        method: "POST",
      });
      const data = await response.json();
      setIsDetecting(false);
      clearIntervals();
      fetchDetectedText();
      console.log("Detection stopped:", data);
    } catch (error) {
      console.error("Error stopping detection:", error);
    }
  };

  const fetchDetectedText = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/get_detected_text");
      const data = await response.json();
      if (data.available) {
        setDetectedText(data.text);
      }
    } catch (error) {
      console.error("Error fetching detected text:", error);
    }
  };

  const clearSession = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/clear_session", {
        method: "DELETE",
      });
      const data = await response.json();
      setDetectedText("");
      setStatus(null);
      console.log("Session cleared:", data);
    } catch (error) {
      console.error("Error clearing session:", error);
    }
  };

  const videoConstraints = {
    facingMode: facingMode,
    width: 640,
    height: 480,
  };

  return (
    <div className="sign-language-detector">
      <h1>Sign Language Detection</h1>

      <div className="camera-section">
        <div className="camera-container">
          {isCameraActive ? (
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              style={{ width: "100%", maxWidth: "640px" }}
            />
          ) : (
            <div className="camera-placeholder">Camera is off</div>
          )}
        </div>
        <div className="camera-controls">
          <button onClick={toggleCamera}>
            {isCameraActive ? "Turn Off Camera" : "Turn On Camera"}
          </button>
          {isCameraActive && (
            <button onClick={switchCamera}>
              Switch Camera ({facingMode === "user" ? "Front" : "Rear"})
            </button>
          )}
        </div>
      </div>

      <div className="language-selector">
        <label>Select Language:</label>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          disabled={isDetecting}
        >
          {languages.map((lang) => (
            <option key={lang} value={lang}>
              {lang}
            </option>
          ))}
        </select>
      </div>

      {modelInfo && (
        <div className="model-info">
          <h3>Model Information</h3>
          <p>Name: {modelInfo.name}</p>
          <p>Type: {modelInfo.model_type}</p>
          <p>Description: {modelInfo.description}</p>
        </div>
      )}

      <div className="controls">
        <button
          onClick={startDetection}
          disabled={isDetecting || !isCameraActive}
        >
          Start Detection
        </button>
        <button onClick={stopDetection} disabled={!isDetecting}>
          Stop Detection
        </button>
        <button onClick={clearSession}>Clear Session</button>
      </div>

      {status && (
        <div className="status">
          <h3>Detection Status</h3>
          <p>Active: {status.active ? "Yes" : "No"}</p>
          <p>Last Detected: {status.last_detected_char || "None"}</p>
          <p>Confidence: {status.confidence?.toFixed(1) || "0"}%</p>
          <p>Current Word: {status.word_buffer || ""}</p>
          <p>Current Sentence: {status.sentence_buffer || ""}</p>
          {status.detection_progress > 0 && (
            <div className="progress-container">
              <div
                className="progress-bar"
                style={{ width: `${status.detection_progress * 100}%` }}
              ></div>
            </div>
          )}
        </div>
      )}

      <div className="results">
        <h3>Detected Text</h3>
        <div className="detected-text-box">
          {detectedText || "No text detected yet"}
        </div>
      </div>

      <style jsx>{`
        .sign-language-detector {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          font-family: Arial, sans-serif;
        }
        .camera-section {
          margin-bottom: 20px;
        }
        .camera-container {
          border: 2px solid #ddd;
          margin-bottom: 10px;
          min-height: 360px;
          display: flex;
          justify-content: center;
          align-items: center;
          background-color: #f0f0f0;
        }
        .camera-placeholder {
          padding: 20px;
          color: #666;
        }
        .camera-controls {
          display: flex;
          gap: 10px;
          margin-bottom: 20px;
        }
        .language-selector {
          margin-bottom: 20px;
        }
        select {
          padding: 8px;
          margin-left: 10px;
        }
        .model-info {
          background-color: #f8f8f8;
          padding: 15px;
          border-radius: 5px;
          margin-bottom: 20px;
        }
        .controls {
          display: flex;
          gap: 10px;
          margin-bottom: 20px;
        }
        button {
          padding: 10px 15px;
          background-color: #4caf50;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        button:disabled {
          background-color: #cccccc;
          cursor: not-allowed;
        }
        .status {
          background-color: #e9f7ef;
          padding: 15px;
          border-radius: 5px;
          margin-bottom: 20px;
        }
        .progress-container {
          width: 100%;
          background-color: #e0e0e0;
          border-radius: 4px;
          margin-top: 10px;
        }
        .progress-bar {
          height: 10px;
          background-color: #4caf50;
          border-radius: 4px;
          transition: width 0.3s;
        }
        .results {
          background-color: #f0f7ff;
          padding: 15px;
          border-radius: 5px;
        }
        .detected-text-box {
          min-height: 100px;
          border: 1px solid #ddd;
          padding: 10px;
          background-color: white;
          white-space: pre-wrap;
        }
      `}</style>
    </div>
  );
};

export default SignLanguageDetector;
