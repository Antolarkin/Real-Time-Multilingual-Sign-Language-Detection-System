import cv2
import time

def test_camera_index_1():
    print("Testing Camera Index 1 (Likely Mac Webcam)...")
    cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("Error: Could not open camera 1.")
        return False

    # Set common resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("Camera 1 opened successfully! Capturing 10 frames to verify stream...")
    
    success_frames = 0
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            success_frames += 1
            # cv2.imshow('Test Camera 1', frame) # Don't show window in automated test
            # cv2.waitKey(1)
        time.sleep(0.1)
        
    cap.release()
    cv2.destroyAllWindows()
    
    if success_frames > 5:
        print(f"Success! Captured {success_frames} frames from Camera 1.")
        return True
    else:
        print("Failed to capture frames from Camera 1.")
        return False

if __name__ == "__main__":
    test_camera_index_1()
