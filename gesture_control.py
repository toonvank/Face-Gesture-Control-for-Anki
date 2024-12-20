import os
import sys
import ctypes
import importlib.util

# Set up paths
addon_dir = os.path.dirname(os.path.realpath(__file__))
vendor_dir = os.path.join(addon_dir, "vendor")
resources_dir = os.path.join(addon_dir, "resources")

# Add vendor directory to Python path
if vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

# Load DLLs from resources directory
opencv_world = os.path.join(resources_dir, "opencv_world490.dll")
if os.path.exists(opencv_world):
    ctypes.CDLL(opencv_world)

# Manually load specific modules if needed
def load_module_from_vendor(module_name, file_name):
    module_path = os.path.join(vendor_dir, file_name)
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    return None

# Load numpy manually if necessary
numpy_pyd = os.path.join(vendor_dir, "numpy", "core", "_multiarray_umath.cp311-win_amd64.pyd")
if os.path.exists(numpy_pyd):
    load_module_from_vendor("numpy", numpy_pyd)

# Import third-party libraries from vendor
import cv2
import dlib
import pyautogui
import time

from aqt import mw
from aqt.qt import QAction

def start_gesture_control():
    # Initialize Dlib's face detector and the facial landmark predictor
    face_detector = dlib.get_frontal_face_detector()
    predictor_path = os.path.join(resources_dir, "shape_predictor_68_face_landmarks.dat")
    shape_predictor = dlib.shape_predictor(predictor_path)

    # Start video capture
    cap = cv2.VideoCapture(0)

    # Reference point for nose position
    reference_nose_position = None

    # Movement states to ensure single action per movement
    moved_right = False
    moved_left = False
    moved_far_left = False

    # Timestamp for horizontal movement cooldown
    last_horizontal_action_time = 0
    horizontal_cooldown = 1  # Cooldown time in seconds

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_detector(gray)

        for face in faces:
            # Predict facial landmarks
            landmarks = shape_predictor(gray, face)

            # Get the nose tip coordinates (landmark index 30)
            nose_tip = (landmarks.part(30).x, landmarks.part(30).y)

            # Set the reference position only once
            if reference_nose_position is None:
                reference_nose_position = nose_tip

            # Calculate movement deltas
            delta_x = nose_tip[0] - reference_nose_position[0]
            delta_y = nose_tip[1] - reference_nose_position[1]

            # Movement thresholds
            threshold_x = 20
            threshold_y = 10

            # Current time
            current_time = time.time()

            # Check for horizontal movements
            if current_time - last_horizontal_action_time > horizontal_cooldown:
                if delta_x > threshold_x and not moved_right:
                    pyautogui.press("space")  # Move right
                    moved_right = True
                    moved_left = False
                    moved_far_left = False
                    last_horizontal_action_time = current_time
                elif delta_x < -threshold_x and not moved_left:
                    pyautogui.press("1")  # Press '1' for grading a card as again
                    moved_left = True
                    moved_right = False
                    moved_far_left = False
                    last_horizontal_action_time = current_time
                elif delta_x < -2 * threshold_x and not moved_far_left:
                    pyautogui.hotkey("ctrl", "z")  # Undo
                    moved_far_left = True
                    moved_left = False
                    moved_right = False
                    last_horizontal_action_time = current_time

            # Check for vertical movements
            if delta_y > threshold_y:
                pyautogui.scroll(-100)  # Scroll down continuously
            elif delta_y < -threshold_y:
                pyautogui.scroll(100)  # Scroll up continuously

            # Draw the nose tip on the frame
            cv2.circle(frame, nose_tip, 5, (0, 255, 0), -1)

        cv2.imshow("Face Gesture Control", frame)

        # Exit the loop when 'Esc' is pressed
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()