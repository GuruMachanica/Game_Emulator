"""
config.py - Handles loading and saving configuration for paths, emulators, and API keys.

This module provides functionality to manage the application's configuration,
including default settings, loading from file, and saving to file.
"""

# Import the json module for working with JSON data.
import json
# Import the os module for interacting with the operating system, e.g., for file path operations.
import os

# Define the path to the configuration file.
CONFIG_PATH = "config.json"

# Define the default configuration values for the application.
DEFAULT = {
    # Default directory for ROMs.
    "roms_dir": "roms",
    # Default directory for game covers.
    "covers_dir": "resources/covers",
    # Default file for storing recently played games.
    "recent_file": "recent.json",
    # Default file for storing game playtime.
    "playtime_file": "playtime.json",
    # Default API key for the RAWG.io service (initially empty).
    "rawg_api_key": "",
    # Default emulators for different consoles.
    "emulators": {
        "NES": "emulators/nestopia.exe",
        "SNES": "emulators/snes9x.exe",
        "GBA": "emulators/visualboyadvance.exe"
    }
}


# Define a function to load the configuration from a file.
def load_config():
    """
    Load configuration from file.
    
    Returns:
        dict: The loaded configuration. If the config file doesn't exist,
              creates it with default values first.
    """
    # Check if the configuration file exists.
    if not os.path.exists(CONFIG_PATH):
        # If the config file doesn't exist, create it with default values.
        save_config(DEFAULT)
    
    try:
        # Open the configuration file for reading.
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            # Load the JSON data from the file and return it.
            return json.load(f)
    # Handle exceptions that may occur during file reading or JSON decoding.
    except (json.JSONDecodeError, IOError) as e:
        # Print an error message if loading fails.
        print(f"Error loading config: {e}. Using default configuration.")
        # Return a copy of the default configuration as a fallback.
        return DEFAULT.copy()


# Define a function to save the configuration to a file.
def save_config(cfg):
    """
    Save configuration to file.
    
    Args:
        cfg (dict): Configuration dictionary to save.
    """
    try:
        # Create the directory for the configuration file if it doesn't exist.
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        
        # Open the configuration file for writing.
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            # Write the configuration dictionary to the file in JSON format.
            json.dump(cfg, f, indent=2)
    # Handle exceptions that may occur during file writing.
    except (IOError, OSError) as e:
        # Print an error message if saving fails.
        print(f"Error saving config: {e}")