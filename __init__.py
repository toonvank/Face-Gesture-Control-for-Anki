import subprocess
import sys
import os

def install_requirements():
    try:
        # Path to the requirements.txt file
        requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")

        # Check if the requirements.txt file exists
        if not os.path.exists(requirements_path):
            print("Error: requirements.txt file not found.")
            return

        # Path to Anki's Python executable
        python_executable = sys.executable

        # Install dependencies from requirements.txt
        print("Installing dependencies from requirements.txt...")
        subprocess.check_call(
            [python_executable, "-m", "pip", "install", "-r", requirements_path, "--user"]
        )
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Install required libraries
install_requirements()

# Import and set up the gesture control functionality
from aqt import mw
from aqt.qt import QAction
from .gesture_control import start_gesture_control

def add_gesture_control_action():
    # Create the menu action
    action = QAction("Start Gesture Control", mw)
    action.triggered.connect(start_gesture_control)
    mw.form.menuTools.addAction(action)

# Add the menu action when Anki starts
add_gesture_control_action()
