import os
import sys
import ctypes
import importlib.util
from .gesture_control import start_gesture_control

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

from aqt import mw
from aqt.qt import QAction
def add_gesture_control_action():
    # Create the menu action
    action = QAction("Start Gesture Control", mw)
    action.triggered.connect(start_gesture_control)
    mw.form.menuTools.addAction(action)

# Add the menu action when Anki starts
add_gesture_control_action()
