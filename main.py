"""
main.py - Entry point for Big Picture Retro Launcher.

This module initializes the application, loads the configuration,
and starts the main window with a Big Picture style interface.
"""

# Import the sys module to access system-specific parameters and functions.
import sys
# Import QApplication for managing the GUI application's control flow and main settings.
from PyQt5.QtWidgets import QApplication
# Import the load_config function from the config module to load the application's configuration.
from config import load_config
# Import the BigPictureWindow class from the ui_bigpicture module, which defines the main window.
from ui_bigpicture import BigPictureWindow


# Define the main function that serves as the entry point of the application.
def main():
    """
    Main entry point for the Retro Launcher application.

    Initializes the QApplication, loads configuration, creates and displays
    the main window, and starts the event loop.
    """
    # Load the application's configuration by calling the load_config function.
    cfg = load_config()
    # Create an instance of QApplication, which is required for any GUI application with Qt.
    app = QApplication(sys.argv)
    # Create an instance of the BigPictureWindow, passing the configuration to it.
    win = BigPictureWindow(cfg)
    # Show the main window.
    win.show()
    # Start the application's event loop and exit the script when the application closes.
    sys.exit(app.exec_())


# Check if the script is being run directly (not imported as a module).
if __name__ == "__main__":
    # Call the main function to start the application.
    main()
