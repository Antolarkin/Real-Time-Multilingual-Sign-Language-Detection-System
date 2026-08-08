import os
import cv2
import mediapipe as mp
import numpy as np
import pickle
import time
import json
from datetime import datetime
import tensorflow as tf
import keras
from features import GestureFeatureExtractor
# Legacy model utilities
from collections import deque, Counter

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_abs_path(relative_path):
    """Convert a path relative to the ml directory to an absolute path"""
    if relative_path.startswith('./ml/'):
        return os.path.join(os.path.dirname(BASE_DIR), relative_path[5:])
    if relative_path.startswith('./'):
        return os.path.join(BASE_DIR, relative_path[2:])
    return os.path.join(BASE_DIR, relative_path)


# ─────────────────────────────────────────────────────────────────────────────
# Advanced Frame Preprocessing
# ─────────────────────────────────────────────────────────────────────────────

# Frame Preprocessor (Disabled for simplicity)
class FramePreprocessor:
    def preprocess(self, frame):
        return frame


# ─────────────────────────────────────────────────────────────────────────────
# Hand Disambiguation Utility
# ─────────────────────────────────────────────────────────────────────────────

def get_hand_by_label(multi_hand_landmarks, multi_handedness):
    """
    Correctly assign Left/Right hands using MediaPipe handedness labels.
    MediaPipe reports from the camera's perspective (mirrored), so:
      - 'Right' in handedness = user's LEFT hand
      - 'Left'  in handedness = user's RIGHT hand
    We return (left_hand_lm, right_hand_lm) from the USER's perspective.
    """
    left_hand  = None
    right_hand = None

    if multi_hand_landmarks is None or multi_handedness is None:
        return left_hand, right_hand

    for hand_lm, handedness in zip(multi_hand_landmarks, multi_handedness):
        label = handedness.classification[0].label  # 'Left' or 'Right'
        # MediaPipe is mirrored: 'Right' → user's left
        if label == 'Right':
            left_hand = hand_lm
        else:
            right_hand = hand_lm

    return left_hand, right_hand


def normalize_landmarks(keypoints_42):
    """Normalize 42 features (21 landmarks × x,y) relative to wrist"""
    if np.all(keypoints_42 == 0):
        return keypoints_42  # empty hand, leave as zeros
    
    wrist_x = keypoints_42[0]
    wrist_y = keypoints_42[1]
    
    normalized = keypoints_42.copy()
    for i in range(0, 42, 2):
        normalized[i] -= wrist_x      # subtract wrist x
        normalized[i+1] -= wrist_y    # subtract wrist y
    
    # Scale by hand size so distance from camera doesn't matter
    distances = np.sqrt(normalized[0::2]**2 + normalized[1::2]**2)
    max_dist = np.max(distances)
    if max_dist > 0:
        normalized /= max_dist
    
    return normalized


# ─────────────────────────────────────────────────────────────────────────────
# Gesture Stability Index (shared logic)
# ─────────────────────────────────────────────────────────────────────────────

class GestureStabilityIndex:
    """
    Tracks prediction stability over a sliding window.
    Only fires when the same prediction appears consistently (GSI ≥ threshold).
    Prevents jitter / false triggers from overlapping hands.
    """

    def __init__(self, window_size=20, gsi_threshold=0.70, cooldown_frames=15):
        self.window_size     = window_size
        self.gsi_threshold   = gsi_threshold
        self.cooldown_frames = cooldown_frames
        self.prediction_window = deque(maxlen=window_size)
        self.last_added_char   = None
        self.cooldown_counter  = 0

    def update(self, detected_char, confidence, confidence_threshold):
        """
        Returns (should_fire: bool, progress: float 0-1).
        """
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1
            return False, 0.0

        valid = (detected_char not in ['?', ' ', 'Background']
                 and confidence >= confidence_threshold)
        self.prediction_window.append(detected_char if valid else '?')

        if not self.prediction_window:
            return False, 0.0

        counts = Counter(self.prediction_window)
        top_char, count = counts.most_common(1)[0]

        if len(self.prediction_window) < self.window_size:
            progress = (count / (self.window_size * self.gsi_threshold)
                        if top_char != '?' else 0.0)
            return False, min(progress, 1.0)

        gsi = count / self.window_size
        progress = min(gsi / self.gsi_threshold, 1.0) if top_char != '?' else 0.0

        if top_char != '?' and gsi >= self.gsi_threshold:
            if top_char != self.last_added_char:
                self.last_added_char = top_char
                self.prediction_window.clear()
                self.cooldown_counter = self.cooldown_frames
                return True, 1.0

        return False, progress

    def reset(self):
        self.prediction_window.clear()
        self.cooldown_counter = 0
        self.last_added_char  = None


# ─────────────────────────────────────────────────────────────────────────────
# ASL Detector
# ─────────────────────────────────────────────────────────────────────────────

class ASLDetector:
    def __init__(self):
        self.model = None
        self.mp_hands = None
        self.mp_drawing = None
        self.hands = None
        self.labels_dict = {
            0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H',
            8: 'I', 9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O',
            15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V',
            22: 'W', 23: 'X', 24: 'Y', 25: 'Z'
        }
        self.model_path = get_abs_path('model.p')
        self.gsi = GestureStabilityIndex(window_size=20, gsi_threshold=0.70, cooldown_frames=15)
        self.confidence_threshold = 30
        self.feature_extractor = None
        self.use_hybrid = False

    def load_model(self):
        try:
            if not os.path.exists(self.model_path):
                print(f"ASL model file not found at {self.model_path}")
                return False
            model_dict = pickle.load(open(self.model_path, 'rb'))
            self.model = model_dict['model']
            self.use_hybrid = False
            print("ASL Legacy model loaded successfully")

            self._init_mediapipe(max_hands=1)
            return True
        except Exception as e:
            print(f"Error loading ASL model: {e}")
            return False

    def _init_mediapipe(self, max_hands=1):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=max_hands
        )

    def _process_legacy_landmarks(self, hand_landmarks):
        """Original feature extraction for the .p Random Forest model with Normalization."""
        kp = []
        for lm in hand_landmarks.landmark:
            kp.extend([lm.x, lm.y])
        
        arr = np.array(kp[:42], dtype=np.float32)
        # Weak normalization
        arr = arr - np.min(arr)
        return arr

    def predict(self, hand_landmarks):
        try:
            features = self._process_legacy_landmarks(hand_landmarks)
            prediction = self.model.predict([np.asarray(features)])
            predicted_index = int(prediction[0])
            detected_char = self.labels_dict.get(predicted_index, '?')
            try:
                proba = self.model.predict_proba([np.asarray(features)])
                confidence = float(np.max(proba)) * 100
            except Exception:
                confidence = 85.0
            return detected_char, confidence
        except Exception as e:
            print(f"ASL prediction error: {e}")
            return '?', 0.0

    def should_auto_detect(self, detected_char, confidence):
        return self.gsi.update(detected_char, confidence, self.confidence_threshold)

    def get_instructions(self):
        return [
            "ASL Detection — Place hand in green box",
            "Hold the same sign for ~1.5 seconds for auto-detection",
            "Press ENTER to add the captured word to the sentence",
            "Press Q when the sentence is complete"
        ]

    def is_manual_capture(self):
        return False

    # Legacy compatibility
    @property
    def window_size(self): return self.gsi.window_size
    @property
    def gsi_threshold(self): return self.gsi.gsi_threshold
    @property
    def cooldown_frames(self): return self.gsi.cooldown_frames
    @property
    def cooldown_counter(self): return self.gsi.cooldown_counter
    @property
    def prediction_window(self): return self.gsi.prediction_window


# ─────────────────────────────────────────────────────────────────────────────
# ISL Detector
# ─────────────────────────────────────────────────────────────────────────────

class ISLDetector:
    def __init__(self):
        self.model = None
        self.mp_hands = None
        self.mp_drawing = None
        self.hands = None
        self.isl_labels_dict = {
            0: '1', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '7', 7: '8', 8: '9',
            9: 'A', 10: 'B', 11: 'C', 12: 'D', 13: 'E', 14: 'F', 15: 'G', 16: 'H',
            17: 'I', 18: 'J', 19: 'K', 20: 'L', 21: 'M', 22: 'N', 23: 'O', 24: 'P',
            25: 'Q', 26: 'R', 27: 'S', 28: 'T', 29: 'U', 30: 'V', 31: 'W', 32: 'X',
            33: 'Y', 34: 'Z', 35: ' '
        }
        self.model_path = get_abs_path('final_lstm_hand_model.keras')
        self.gsi = GestureStabilityIndex(window_size=20, gsi_threshold=0.60, cooldown_frames=15)
        self.confidence_threshold = 30
        self.feature_extractor = None
        self.use_hybrid = False

    def load_model(self):
        try:
            if not os.path.exists(self.model_path):
                print(f"ISL model file not found at {self.model_path}")
                return False
            self.model = keras.models.load_model(self.model_path)
            self.use_hybrid = False
            print("ISL standard model loaded successfully")

            self._init_mediapipe(max_hands=2)
            return True
        except Exception as e:
            print(f"Error loading ISL model: {e}")
            return False

    def _init_mediapipe(self, max_hands=2):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=max_hands
        )

    def _process_landmarks_for_legacy(self, multi_hand_landmarks, multi_handedness):
        """Original absolute-coordinate extraction for the standard ISL model."""
        # Note: Original logic used simple index access, but we'll use our safer helper
        # to avoid crashes, but WITHOUT the new normalization.
        left_lm, right_lm = get_hand_by_label(multi_hand_landmarks, multi_handedness)

        def extract_xy(hand_lm):
            if hand_lm is None:
                return np.zeros(42, dtype=np.float32)
            kp = []
            for lm in hand_lm.landmark:
                kp.extend([lm.x, lm.y])
            return np.array(kp[:42], dtype=np.float32)

        left_feat  = extract_xy(left_lm)
        right_feat = extract_xy(right_lm)
        # Stack as expected by the (None, 1, 84) LSTM input
        features = np.concatenate([left_feat, right_feat]).reshape(1, 1, 84)
        return features

    def predict(self, multi_hand_landmarks, multi_handedness=None):
        try:
            features = self._process_landmarks_for_legacy(multi_hand_landmarks, multi_handedness)
            prediction = self.model.predict(features, verbose=0)
            predicted_index = int(np.argmax(prediction[0]))
            confidence = float(prediction[0][predicted_index]) * 100

            detected_char = self.isl_labels_dict.get(predicted_index, '?')
            return detected_char, confidence
        except Exception as e:
            print(f"ISL prediction error: {e}")
            return '?', 0.0
        except Exception as e:
            print(f"ISL prediction error: {e}")
            return '?', 0.0

    def should_auto_detect(self, detected_char, confidence):
        return self.gsi.update(detected_char, confidence, self.confidence_threshold)

    def get_instructions(self):
        return [
            "ISL Detection — Place hands in green box",
            "Hold the same sign for ~2 seconds for auto-detection",
            "Press ENTER to add the captured word to the sentence",
            "Press Q when the sentence is complete"
        ]

    def is_manual_capture(self):
        return False

    # Legacy compatibility
    @property
    def window_size(self): return self.gsi.window_size
    @property
    def gsi_threshold(self): return self.gsi.gsi_threshold
    @property
    def cooldown_frames(self): return self.gsi.cooldown_frames
    @property
    def cooldown_counter(self): return self.gsi.cooldown_counter
    @property
    def prediction_window(self): return self.gsi.prediction_window


# ─────────────────────────────────────────────────────────────────────────────
# TSL Detector
# ─────────────────────────────────────────────────────────────────────────────

class TSLDetector:
    def __init__(self):
        self.model = None
        self.mp_holistic = None
        self.mp_drawing = None
        self.hands = None          # kept for draw_landmarks compatibility
        self.mp_hands = None       # kept for draw_landmarks compatibility
        self.holistic = None
        self.tamil_labels = None
        self.model_path = get_abs_path('best_lstm_model.keras')
        self.labels_path = get_abs_path('tamil_labels.json')
        self.gsi = GestureStabilityIndex(window_size=15, gsi_threshold=0.55, cooldown_frames=20)
        self.confidence_threshold = 10  # TSL LSTM has 26 classes, softmax is spread thin
        self.use_hybrid = False

    def load_model(self):
        try:
            if not os.path.exists(self.model_path):
                print(f"Tamil model file not found at {self.model_path}")
                return False
            self.model = keras.models.load_model(self.model_path)
            if not os.path.exists(self.labels_path):
                print(f"Tamil labels file not found at {self.labels_path}")
                return False
            with open(self.labels_path, 'r', encoding='utf-8') as f:
                self.tamil_labels = json.load(f)
            self.tamil_labels = {str(k): v for k, v in self.tamil_labels.items()}
            self.use_hybrid = False
            print(f"Tamil standard model loaded. Labels: {len(self.tamil_labels)} characters")
            self._init_mediapipe()
            return True
        except Exception as e:
            print(f"Error loading Tamil model: {e}")
            return False

    def _init_mediapipe(self):
        self.mp_holistic = mp.solutions.holistic
        self.mp_hands = mp.solutions.hands      # kept for compatibility
        self.mp_drawing = mp.solutions.drawing_utils
        # Use Holistic — same as training notebook
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        # Point self.hands to holistic so UnifiedDetector draw_landmarks still works
        self.hands = self.holistic

    def _extract_hand_xy(self, hand_landmarks):
        """Extract 42 (x,y) features, wrist-relative + scale-normalized."""
        if hand_landmarks is None:
            return np.zeros(42, dtype=np.float32)
        lms = hand_landmarks.landmark
        wx, wy = lms[0].x, lms[0].y  # wrist as origin
        coords = np.array([[lm.x - wx, lm.y - wy] for lm in lms], dtype=np.float32).flatten()
        scale = np.max(np.abs(coords)) + 1e-6
        return coords / scale

    def predict_from_holistic(self, results):
        """Predict Tamil sign from Holistic results."""
        try:
            lh = self._extract_hand_xy(results.left_hand_landmarks)
            rh = self._extract_hand_xy(results.right_hand_landmarks)
            feat = np.concatenate([lh, rh]).reshape(1, 1, 84)
            prediction = self.model.predict(feat, verbose=0)
            predicted_index = int(np.argmax(prediction[0]))
            confidence = float(prediction[0][predicted_index]) * 100

            label_key = str(predicted_index + 1)
            if label_key in self.tamil_labels:
                info = self.tamil_labels[label_key]
                if isinstance(info, dict):
                    char = info.get('tamil', info.get('pronunciation', '?'))
                    return char, confidence
                return str(info), confidence
            return '?', confidence
        except Exception as e:
            print(f"Tamil prediction error: {e}")
            return '?', 0.0

    def predict(self, multi_hand_landmarks, multi_handedness=None):
        """Legacy predict path (called from UnifiedDetector.process_frame)."""
        # This path is not reached for TSL — TSL uses predict_from_holistic via process_frame override
        return '?', 0.0

    def should_auto_detect(self, detected_char, confidence):
        return self.gsi.update(detected_char, confidence, self.confidence_threshold)

    def get_instructions(self):
        return [
            "Tamil Sign Language Detection — Place hands in green box",
            "Hold the same sign for ~2 seconds for auto-detection",
            "Press ENTER to add the captured word to the sentence",
            "Press Q when the sentence is complete"
        ]

    def is_manual_capture(self):
        return False

    # Legacy compatibility
    @property
    def window_size(self): return self.gsi.window_size
    @property
    def gsi_threshold(self): return self.gsi.gsi_threshold
    @property
    def cooldown_frames(self): return self.gsi.cooldown_frames
    @property
    def cooldown_counter(self): return self.gsi.cooldown_counter
    @property
    def prediction_window(self): return self.gsi.prediction_window


# ─────────────────────────────────────────────────────────────────────────────
# Unified Detector
# ─────────────────────────────────────────────────────────────────────────────

class UnifiedSignLanguageDetector:
    def __init__(self):
        self.asl_detector = ASLDetector()
        self.isl_detector = ISLDetector()
        self.tsl_detector = TSLDetector()
        self.current_detector = None
        self.language = None
        self.cap = None
        self.session_start_time = None
        self.preprocessor = FramePreprocessor()

    def initialize(self, language="ASL"):
        self.language = language.upper()
        if self.language == "ASL":
            self.current_detector = self.asl_detector
            return self.asl_detector.load_model()
        elif self.language == "ISL":
            self.current_detector = self.isl_detector
            return self.isl_detector.load_model()
        elif self.language in ("TSL", "TAMIL"):
            self.current_detector = self.tsl_detector
            return self.tsl_detector.load_model()
        else:
            print(f"Unsupported language: {language}")
            return False

    def get_detector_info(self):
        if not self.current_detector:
            return {}
        return {
            "language": self.language,
            "window_size": self.current_detector.window_size,
            "gsi_threshold": self.current_detector.gsi_threshold,
            "confidence_threshold": self.current_detector.confidence_threshold,
            "cooldown_frames": self.current_detector.cooldown_frames,
            "mediapipe_complexity": "model_complexity=1",
        }

    def apply_lighting_normalization(self, frame):
        """Full preprocessing pipeline (backward-compatible method name)."""
        return self.preprocessor.preprocess(frame)

    def initialize_hands_if_needed(self):
        if self.current_detector:
            if self.current_detector.hands is None:
                self.current_detector.load_model()
            return self.current_detector.hands
        return None

    def process_frame(self, frame, results=None):
        """
        Process a single frame and return detection results.
        If results are provided (from api.py), uses them directly.
        """
        if not self.current_detector:
            return '?', 0.0, {}

        # If results not provided, calculate them (legacy fallback)
        if results is None:
            preprocessed = self.preprocessor.preprocess(frame)
            frame_rgb = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2RGB)
            results = self.current_detector.hands.process(frame_rgb)

        detected_char = '?'
        confidence    = 0.0
        extra_info    = {}

        if self.language in ("TSL", "TAMIL"):
            # TSL uses Holistic model — different results structure
            tsl = self.current_detector
            has_hand = (results and
                        (results.left_hand_landmarks is not None or
                         results.right_hand_landmarks is not None))
            if has_hand:
                detected_char, confidence = tsl.predict_from_holistic(results)
                if int(time.time() * 30) % 30 == 0:
                    print(f"DEBUG TSL: Char='{detected_char}', Conf={confidence:.1f}%", flush=True)
                should_detect, progress = tsl.should_auto_detect(detected_char, confidence)
                extra_info = {
                    "should_auto_detect": should_detect,
                    "detection_progress": progress,
                    "cooldown_active": tsl.gsi.cooldown_counter > 0,
                }
        elif results and results.multi_hand_landmarks:
            mhl = results.multi_hand_landmarks
            mhd = results.multi_handedness

            if self.language == "ASL":
                detected_char, confidence = self.current_detector.predict(mhl[0])
            else:
                detected_char, confidence = self.current_detector.predict(mhl, mhd)

            # DEBUG: Print every 30th frame to avoid log spam
            if int(time.time() * 30) % 30 == 0:
                print(f"DEBUG: Language={self.language}, Char='{detected_char}', Conf={confidence:.1f}%", flush=True)

            # Auto-detection stability logic
            should_detect, progress = self.current_detector.should_auto_detect(
                detected_char, confidence
            )
            extra_info = {
                "should_auto_detect": should_detect,
                "detection_progress": progress,
                "cooldown_active": self.current_detector.gsi.cooldown_counter > 0,
            }

        return detected_char, confidence, extra_info

    def draw_landmarks(self, frame, results):
        """Draw hand landmarks with colour-coded handedness."""
        if not self.current_detector:
            return
        mp_draw = self.current_detector.mp_drawing

        if self.language in ("TSL", "TAMIL"):
            # Holistic results: left_hand_landmarks / right_hand_landmarks
            mp_h = mp.solutions.hands
            for hand_lm, colour in [
                (getattr(results, 'left_hand_landmarks', None),  (0, 255, 0)),
                (getattr(results, 'right_hand_landmarks', None), (255, 100, 0)),
            ]:
                if hand_lm:
                    mp_draw.draw_landmarks(
                        frame, hand_lm, mp_h.HAND_CONNECTIONS,
                        mp_draw.DrawingSpec(color=colour, thickness=2, circle_radius=4),
                        mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2))
        elif results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Colour-code: green = right hand (user's), blue = left hand
                if results.multi_handedness:
                    label = results.multi_handedness[i].classification[0].label
                    dot_colour = (0, 255, 0) if label == 'Left' else (255, 100, 0)
                else:
                    dot_colour = (0, 255, 0)

                self.current_detector.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.current_detector.mp_hands.HAND_CONNECTIONS,
                    self.current_detector.mp_drawing.DrawingSpec(
                        color=dot_colour, thickness=2, circle_radius=4),
                    self.current_detector.mp_drawing.DrawingSpec(
                        color=(255, 255, 255), thickness=2)
                )

    def get_instructions(self):
        if self.current_detector:
            return self.current_detector.get_instructions()
        return []

    def is_manual_capture(self):
        if self.current_detector:
            return self.current_detector.is_manual_capture()
        return False

    def cleanup(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()