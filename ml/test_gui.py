import cv2
import numpy as np

def test_gui():
    print("Attempting to create a window...")
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    img[:] = (0, 255, 0) # Green
    
    cv2.putText(img, "GUI Test", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.imshow("Test Window", img)
    print("Window created. Press any key to close.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("Window closed.")

if __name__ == "__main__":
    test_gui()
