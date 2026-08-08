from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import numpy as np
import multiprocessing
import threading
import os
import time
import json
from datetime import datetime
import asyncio
import uvicorn
from models import UnifiedSignLanguageDetector
from semantic_corrector import SemanticCorrector
try:
    from PIL import Image, ImageDraw, ImageFont
    _TAMIL_FONT_PATH = "/System/Library/Fonts/Supplemental/Tamil Sangam MN.ttc"
    _TAMIL_FONT_SM = ImageFont.truetype(_TAMIL_FONT_PATH, 36)
    _TAMIL_FONT_LG = ImageFont.truetype(_TAMIL_FONT_PATH, 52)
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

def draw_unicode_text(frame, text, pos, font=None, color=(255, 255, 0)):
    """Draw a Unicode (Tamil) string on an OpenCV frame using Pillow."""
    if not PIL_AVAILABLE or font is None:
        # Graceful fallback: skip non-ASCII characters
        safe = ''.join(c if ord(c) < 128 else '?' for c in text)
        cv2.putText(frame, safe, pos, cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2)
        return
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    draw.text(pos, text, font=font, fill=(color[2], color[1], color[0]))
    frame[:] = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

app = FastAPI(title="Unified Sign Language Detection API", version="3.0.0")

# Add CORS middleware for React app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DETECTED_TEXT_FILE = "detected_text.txt"
DETECTION_LOG_FILE = "sign_language_detections.txt"
STATUS_FILE = "status.json"
CAMERA_INDEX = 1  # 0 is usually iPhone (Continuity), 1 is Built-in Mac Webcam

# Global variables
detection_active = False
detection_thread = None
detector = UnifiedSignLanguageDetector()
detection_status = {
    "active": False,
    "language": "ASL",
    "word_buffer": "",
    "sentence_buffer": "",
    "last_detected_char": "?",
    "confidence": 0.0,
    "session_id": "",
    "completed": False,
    "final_sentence": "",
    "detection_progress": 0.0,
    "auto_detection_enabled": True
}

class DetectionRequest(BaseModel):
    language: str = "ASL"  # ASL, ISL

# Reset status file on startup to clear stale state
def reset_status_on_startup():
    with open(STATUS_FILE, 'w') as f:
        json.dump(detection_status, f)

reset_status_on_startup()

def log_detection(detection_data):
    """Log detection to text file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log to text file
    with open(DETECTION_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {detection_data}\n")

def process_camera_opencv(language="ASL"):
    """Unified camera processing for ASL, ISL, and Tamil"""
    global detection_status, detector
    
    # Initialize detector for specified language
    print(f"DEBUG: Initializing detector for {language}...", flush=True)
    if not detector.initialize(language):
        print(f"DEBUG: Failed to load {language} model", flush=True)
        return False
    
    detector.cap = cv2.VideoCapture(CAMERA_INDEX)
    if not detector.cap.isOpened():
        print(f"DEBUG: Cannot access camera {CAMERA_INDEX}. Trying index 0...", flush=True)
        detector.cap = cv2.VideoCapture(0)
    
    if not detector.cap.isOpened():
        print("DEBUG: Cannot access any camera", flush=True)
        return False
    
    # Set frame dimensions based on language
    frame_width = 1280 if language in ["ISL", "TSL", "TAMIL"] else 1920
    frame_height = 720 if language in ["ISL", "TSL", "TAMIL"] else 1080
    detector.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    detector.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    
    print(f"DEBUG: Camera opened. Resolution: {frame_width}x{frame_height}", flush=True)
    
    window_name = f'{language} Character Detection - Unified API'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, frame_width, frame_height)
    
    # Get language-specific instructions
    instructions = detector.get_instructions()
    
    # Initialize Semantic Corrector
    semantic_corrector = SemanticCorrector(language)
    
    word_buffer = ""
    sentence_buffer = ""
    detector.session_start_time = datetime.now().isoformat()
    print("DEBUG: Starting detection loop...", flush=True)
    
    # Initialize log file
    with open(DETECTION_LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== {language} Character Detection Session Started: {detector.session_start_time} ===\n")
    
    # Reset detection status
    detection_status.update({
        "active": True,
        "language": language,
        "word_buffer": "",
        "sentence_buffer": "",
        "last_detected_char": "?",
        "confidence": 0.0,
        "session_id": detector.session_start_time,
        "completed": False,
        "final_sentence": "",
        "detection_progress": 0.0,
        "auto_detection_enabled": True  # All languages now use auto-detection
    })
    
    # Write initial status to file so frontend sees it immediately
    with open(STATUS_FILE, 'w') as f:
        json.dump(detection_status, f)
    
    # Camera Warm-up (Important for Mac/Slow cameras)
    print("DEBUG: Waiting for camera to warm up...", flush=True)
    for _ in range(10):  # Try 10 times to get a valid frame
        ret, frame = detector.cap.read()
        if ret:
            break
        time.sleep(0.1)
    
    while True:
        # Check status file to see if we've been told to stop
        try:
            with open(STATUS_FILE, 'r') as sf:
                file_status = json.load(sf)
                if not file_status.get("active", True):
                    print("DEBUG: Stop signal received via status file", flush=True)
                    break
        except Exception:
            pass

        ret, frame_raw = detector.cap.read()
        if not ret:
            print("Warning: Failed to read from camera, retrying...", flush=True)
            time.sleep(0.5)
            ret, frame_raw = detector.cap.read()
            if not ret:
                print("Error: Permanent camera read failure", flush=True)
                with open(STATUS_FILE, 'w') as f:
                    json.dump({**detection_status, "active": False}, f)
                break
        
        # 1. Prepare frame
        frame_display = frame_raw.copy()
        
        # Get frame dimensions
        height, width = frame_display.shape[:2]
        
        # 2. Add guidance box and overlays to DISPLAY frame
        box_size = int(min(width, height) * 0.7)
        center_x = width // 2
        center_y = height // 2
        cv2.rectangle(frame_display, 
                      (center_x - box_size//2, center_y - box_size//2),
                      (center_x + box_size//2, center_y + box_size//2), 
                      (0, 255, 0), 3)
        
        # Add overlay for status info based on language
        if language in ["ISL", "TSL", "TAMIL"]:
            overlay = frame_display.copy()
            cv2.rectangle(overlay, (0, 0), (width, 140), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame_display, 0.4, 0, frame_display)
            font_scale = 0.6
            line_spacing = 25
            start_y = 30
        else:
            # ASL style overlay
            overlay = np.zeros((200, width, 3), dtype=np.uint8)
            frame_display[0:200, 0:width] = cv2.addWeighted(overlay, 0.5, frame_display[0:200, 0:width], 0.5, 0)
            font_scale = 0.8
            line_spacing = 40
            start_y = 40
        
        # Instructions overlay
        for idx, instruction in enumerate(instructions):
            cv2.putText(frame_display, instruction, (10, start_y + idx * line_spacing), 
                        cv2.FONT_HERSHEY_DUPLEX, font_scale, (255, 255, 255), 2)
        
        # Process frame for hand detection (USING RAW FRAME)
        frame_rgb = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False  # Required by MediaPipe Holistic
        results = detector.initialize_hands_if_needed().process(frame_rgb)
        frame_rgb.flags.writeable = True
        
        # Get detection results
        detected_char, confidence, extra_info = detector.process_frame(frame_raw, results=results)
        
        # MONITORING LOG (Every 10 frames)
        if int(time.time() * 10) % 10 == 0:
            print(f">>> [REAL-TIME] Lang: {language} | Char: {detected_char} | Conf: {confidence:.2f}% | Prog: {extra_info.get('detection_progress', 0):.2f}", flush=True)

        # Draw hand landmarks (Always draw on display frame)
        if language in ("TSL", "TAMIL"):
            # TSL uses holistic — always call draw_landmarks, it handles the structure internally
            detector.draw_landmarks(frame_display, results)
        elif results and results.multi_hand_landmarks:
            detector.draw_landmarks(frame_display, results)
            cv2.putText(frame_display, "HAND TRACKING ACTIVE", (width - 250, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(frame_display, "NO HAND DETECTED", (width - 250, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Display detected character and confidence
        if language in ["ISL", "TSL", "TAMIL"]:
            color = (0, 255, 0) if detected_char != '?' else (100, 100, 100)
            if language in ["TSL", "TAMIL"] and PIL_AVAILABLE:
                draw_unicode_text(frame_display,
                                  f"Detected: {detected_char} ({confidence:.1f}%)",
                                  (10, height - 80),
                                  font=_TAMIL_FONT_SM,
                                  color=color)
            else:
                cv2.putText(frame_display, f"Detected: {detected_char} ({confidence:.1f}%)",
                            (10, height - 80),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, color, 2)
        else:
            if detected_char != '?':
                cv2.putText(frame_display, f"Detected: {detected_char} ({confidence:.1f}%)", (10, 250), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
            else:
                 cv2.putText(frame_display, "Waiting for sign...", (10, 250), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, (100, 100, 100), 2)
        
        # Handle auto-detection progress bar for all languages
        if extra_info and extra_info.get("detection_progress", 0) > 0:
            progress = extra_info["detection_progress"]
            bar_width = 200
            bar_height = 20
            bar_x = width - 220
            bar_y = height - 100
            
            # Draw progress bar
            cv2.rectangle(frame_display, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
            cv2.rectangle(frame_display, (bar_x, bar_y), (bar_x + int(bar_width * progress), bar_y + bar_height), (0, 255, 0), -1)
            
            # Show progress text
            progress_text = f"Detecting '{detected_char}': {int(progress * 100)}%"
            cv2.putText(frame_display, progress_text, (bar_x - 50, bar_y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Display current word and sentence
        word_y = height - 50 if language in ["ISL", "TSL", "TAMIL"] else 300
        sentence_y = height - 20 if language in ["ISL", "TSL", "TAMIL"] else 350
        font_size = 0.7 if language in ["ISL", "TSL", "TAMIL"] else 1
        
        if language in ["TSL", "TAMIL"] and PIL_AVAILABLE:
            draw_unicode_text(frame_display, f"Word: {word_buffer}",
                              (10, word_y), font=_TAMIL_FONT_SM, color=(255, 255, 0))
            draw_unicode_text(frame_display, f"Sentence: {sentence_buffer}",
                              (10, sentence_y), font=_TAMIL_FONT_SM, color=(0, 255, 255))
        else:
            cv2.putText(frame_display, f"Word: {word_buffer}", (10, word_y),
                        cv2.FONT_HERSHEY_DUPLEX, font_size, (255, 255, 0), 2)
            cv2.putText(frame_display, f"Sentence: {sentence_buffer}", (10, sentence_y),
                        cv2.FONT_HERSHEY_DUPLEX, font_size, (0, 255, 255), 2)
        
        # Handle automatic detection for all languages
        if extra_info and extra_info.get("should_auto_detect", False):
            word_buffer += detected_char
            print(f"Auto-added '{detected_char}' to word. Current word: '{word_buffer}'", flush=True)
        
        # Update status file
        current_status = {
            "active": True,
            "language": language,
            "word_buffer": word_buffer,
            "sentence_buffer": sentence_buffer,
            "last_detected_char": detected_char,
            "confidence": confidence,
            "session_id": detector.session_start_time,
            "completed": False,
            "final_sentence": "",
            "detection_progress": extra_info.get("detection_progress", 0.0) if extra_info else 0.0,
            "auto_detection_enabled": True
        }
        
        with open(STATUS_FILE, 'w') as f:
            json.dump(current_status, f)
        
        cv2.imshow(window_name, frame_display)

        # Handle keyboard input (INSIDE THE LOOP)
        key = cv2.waitKey(1) & 0xFF
        
        if key == 13:  # ENTER - Add word to sentence
            if word_buffer.strip():
                if sentence_buffer:
                    sentence_buffer += ' ' + word_buffer.strip()
                else:
                    sentence_buffer = word_buffer.strip()
                
                print(f"Added word '{word_buffer}' to sentence. Current sentence: '{sentence_buffer}'", flush=True)
                word_buffer = ""
                
        elif key == ord('q'):  # Q - Finish sentence detection
            # Add the last word if any
            if word_buffer.strip():
                if sentence_buffer:
                    sentence_buffer += ' ' + word_buffer.strip()
                else:
                    sentence_buffer = word_buffer.strip()
                word_buffer = ""
            
            # Apply Semantic Error Correction
            original_sentence = sentence_buffer
            sentence_buffer = semantic_corrector.correct_sentence(sentence_buffer)
            
            if original_sentence != sentence_buffer:
                print(f"Semantic Correction Applied: '{original_sentence}' -> '{sentence_buffer}'", flush=True)
            
            # Save sentence to text file
            with open(DETECTED_TEXT_FILE, 'w', encoding='utf-8') as f:
                f.write(sentence_buffer)
            
            print(f"Session completed. Final sentence: '{sentence_buffer}'", flush=True)
            
            # Update final status
            detection_status.update({
                "active": False,
                "language": language,
                "word_buffer": word_buffer,
                "sentence_buffer": sentence_buffer,
                "last_detected_char": detected_char,
                "confidence": confidence,
                "completed": True,
                "final_sentence": sentence_buffer,
                "detection_progress": 0.0
            })
            
            detection_active = False
            detection_status["active"] = False
            break
    
    # Cleanup
    detector.cleanup()
    
    # Log session end
    with open(DETECTION_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"=== Session Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
    
    return True

@app.post("/start_detection")
async def start_detection(request: DetectionRequest, background_tasks: BackgroundTasks):
    """Start sign language character detection with OpenCV popup window"""
    global detection_thread, detection_active
    
    # Validate language
    language = request.language.upper()
    if language not in ["ASL", "ISL", "TSL", "TAMIL"]:
        raise HTTPException(status_code=400, detail="Language must be 'ASL', 'ISL', 'TSL', or 'TAMIL'")
    
    if detection_active:
        return JSONResponse(
            status_code=400,
            content={"message": f"{language} detection is already running"}
        )
    
    # Set the flag immediately
    detection_active = True
    # Reset status
    detection_status["active"] = True
    detection_status["language"] = language
    
    # Update status file IMMEDIATELY
    with open(STATUS_FILE, 'w') as f:
        json.dump(detection_status, f)
    
    # Set session start time in parent so it's available in the response
    detector.session_start_time = datetime.now().isoformat()

    # Start detection in background process (Fix for Mac GUI)
    detection_thread = multiprocessing.Process(
        target=process_camera_opencv,
        args=(language,),
        daemon=True
    )
    detection_thread.start()
    
    # Wait a moment for detection to start
    await asyncio.sleep(1.0)
    
    return {
        "message": f"{language} character detection started successfully",
        "language": language,
        "session_id": detector.session_start_time,
        "status_url": "/detection_status",
    }

@app.get("/detection_status")
async def get_detection_status():
    """Get the current detection status"""
    global detection_active, detection_status
    
    # Check status file if available
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
            
    return detection_status

@app.post("/stop_detection")
async def stop_detection():
    """Stop the current detection session"""
    global detection_active, detection_thread
    
    if not detection_active:
        return {"message": "No detection session is currently active"}
    
    detection_active = False
    
    # Signal the child process to stop by updating the status file
    detection_status["active"] = False
    with open(STATUS_FILE, 'w') as f:
        json.dump(detection_status, f)
    
    # Give process time to stop cleanly, then terminate if still running
    if detection_thread and detection_thread.is_alive():
        detection_thread.join(timeout=2.0)
        if detection_thread.is_alive():
            detection_thread.terminate()
        
    return {"message": "Detection session stopped"}

@app.get("/get_detected_text")
async def get_detected_text():
    """Retrieve the final detected text"""
    if os.path.exists(DETECTED_TEXT_FILE):
        with open(DETECTED_TEXT_FILE, "r", encoding="utf-8") as f:
            return {"text": f.read()}
    return {"text": ""}

@app.get("/detection_log")
async def get_detection_log():
    """Retrieve the detailed detection log"""
    if os.path.exists(DETECTION_LOG_FILE):
        with open(DETECTION_LOG_FILE, "r", encoding="utf-8") as f:
            return {"log": f.read()}
    return {"log": ""}

@app.get("/model_info/{language}")
async def get_model_info(language: str):
    """Get information about a specific model"""
    lang = language.upper()
    if lang == "ASL":
        return {
            "model_type": "Random Forest (sklearn)",
            "features": "42 Landmarks (X, Y)",
            "classes": 26,
            "file": "model.p"
        }
    elif lang == "ISL":
        return {
            "model_type": "LSTM (Keras)",
            "features": "84 Landmarks (2 hands x 42)",
            "classes": 36,
            "file": "final_lstm_hand_model.keras"
        }
    return {"error": "Model info not available for this language"}

@app.get("/supported_languages")
async def get_supported_languages():
    """Get list of supported languages and their details"""
    return {
        "languages": [
            {"code": "ASL", "name": "American Sign Language", "hands": 1},
            {"code": "ISL", "name": "Indian Sign Language", "hands": 2},
            {"code": "TSL", "name": "Tamil Sign Language", "hands": 2}
        ]
    }

@app.post("/set_camera/{index}")
async def set_camera(index: int):
    """Change the camera index"""
    global CAMERA_INDEX
    CAMERA_INDEX = index
    return {"message": f"Camera index set to {index}. Restart detection to apply."}

@app.delete("/clear_session")
async def clear_session():
    """Clear output files for a fresh session"""
    for file_path in [DETECTED_TEXT_FILE, DETECTION_LOG_FILE, STATUS_FILE]:
        if os.path.exists(file_path):
            os.remove(file_path)
    return {"message": "Session files cleared"}

@app.get("/word_formation/{language}")
async def get_word_formation(language: str):
    """Get word formation progress for ISL/Tamil"""
    global detection_status
    return {
        "current_word": detection_status["word_buffer"],
        "sentence": detection_status["sentence_buffer"]
    }

@app.get("/statistics")
async def get_statistics():
    """Get overall detection session statistics"""
    return {
        "uptime": "100%",
        "status": "Healthy",
        "available_models": {
            "ASL": "Loaded",
            "ISL": "Loaded",
            "TSL": "Loaded"
        },
        "auto_detection_info": {
            "ASL": "Hold sign for 1.5-2 seconds for automatic detection",
            "ISL": "Hold sign for 2-3 seconds for automatic detection", 
            "TSL/TAMIL": "Hold sign for 2-3 seconds for automatic detection"
        }
    }

if __name__ == "__main__":
    # Ensure we are in the script's directory for relative paths to work
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(os.path.abspath(DETECTION_LOG_FILE)), exist_ok=True)
    
    print("Starting Unified Sign Language Detection API...", flush=True)
    print("Supported Languages: ASL (American), ISL (Indian), and TSL/Tamil", flush=True)
    print("All languages now use automatic detection - no manual key presses needed!", flush=True)
    print("The API will open OpenCV popup windows for camera detection", flush=True)
    print("Text output will be available via /get_detected_text endpoint", flush=True)
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )