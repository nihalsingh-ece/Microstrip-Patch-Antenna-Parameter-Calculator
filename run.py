import sys
import os

# Add the current directory to Python path to find Antenna_Designer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Import from Antenna_Designer package
try:
    from antennacalculator.ui_main import antennacalculator
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Current sys.path: {sys.path}")
    print(f"Current directory: {os.path.dirname(os.path.abspath(__file__))}")
    sys.exit(1)

if __name__ == "__main__":
    # Set high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show main window
    window = antennacalculator()
    window.showMaximized()  # Show window maximized

    # Start application event loop
    sys.exit(app.exec())