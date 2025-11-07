"""
launcher.py
------------
Handles launching emulators and tracking play sessions.
Ensures safe emulator lookup and process handling.
"""

# Import the subprocess module to spawn new processes, connect to their input/output/error pipes, and obtain their return codes.
import subprocess
# Import the os module for interacting with the operating system, e.g., for file path operations.
import os
# Import the threading module for creating and managing threads.
import threading
# Import Optional, Callable, Dict, and Any from the typing module for type hinting.
from typing import Optional, Callable, Dict, Any
# Import QMessageBox and QWidget from PyQt5.QtWidgets for GUI elements.
from PyQt5.QtWidgets import QMessageBox, QWidget


# Define a function to find the correct emulator executable for a given console.
def find_emulator(cfg: Dict[str, Any], console: str) -> Optional[str]:
    """
    Finds the correct emulator executable for the given console.

    It first checks config.json, then scans the `emulators/` folder.
    If multiple emulators are found, it returns the first one.
    If no emulator is found, it returns None.

    Args:
        cfg (Dict[str, Any]): The configuration dictionary.
        console (str): The name of the console to find the emulator for.

    Returns:
        Optional[str]: The path to the emulator executable, or None if not found.
    """
    # Attempt to get the emulator path directly from the configuration for the specified console.
    em = cfg.get("emulators", {}).get(console)

    # ----- Direct match in config.json -----
    # If an emulator path is found in the config and it exists on the filesystem, return it.
    if em and os.path.exists(em):
        return em

    # ----- Try to find a matching file in the emulators/ folder -----
    # Define the directory where emulators are expected to be located.
    em_dir = "emulators"
    # Check if the emulators directory exists.
    if os.path.isdir(em_dir):
        # Iterate through each file in the emulators directory.
        for file in os.listdir(em_dir):
            # Check if the console name is part of the filename (case-insensitive).
            if console.lower() in file.lower():
                # Construct the full path to the potential emulator executable.
                candidate = os.path.join(em_dir, file)
                # If the candidate path points to an existing file, return it.
                if os.path.isfile(candidate):
                    return candidate

    # ----- Fallback: if only one .exe is present, assume it -----
    try:
        # Get a list of all files in the emulators directory.
        files = [os.path.join(em_dir, f) for f in os.listdir(em_dir)]
        # Filter the list to include only executable files (ending with .exe).
        exes = [f for f in files if f.lower().endswith(".exe")]
        # If exactly one executable is found, assume it's the correct emulator and return its path.
        if len(exes) == 1:
            return exes[0]
    # Catch FileNotFoundError if the emulators directory does not exist.
    except FileNotFoundError:
        # Pass, as this is a fallback mechanism.
        pass

    # If no emulator is found through any of the above methods, return None.
    return None


# Define a function to launch an emulator and monitor its process.
def launch_and_watch(
    emulator: str,
    rom_path: str,
    on_exit: Optional[Callable[[int], None]] = None,
    parent: Optional[QWidget] = None,
) -> Optional[subprocess.Popen]:
    """
    Launches an emulator with a ROM file.
    Runs it in a separate thread and optionally triggers on_exit() when closed.

    Args:
        emulator (str): The path to the emulator executable.
        rom_path (str): The path to the ROM file.
        on_exit (Optional[Callable[[int], None]]): A callback function to execute when the emulator process exits.
        parent (Optional[QWidget]): The parent widget for displaying message boxes.

    Returns:
        Optional[subprocess.Popen]: The process object for the launched emulator, or None if launch fails.
    """

    # ----- VALIDATION -----
    # Check if the emulator executable exists.
    if not os.path.exists(emulator):
        # Display a critical error message box to the user.
        QMessageBox.critical(parent, "Emulator Missing", f"Emulator not found:\n{emulator}")
        # Print an error message to the console.
        print(f"❌ Emulator missing: {emulator}")
        # Return None as the launch failed.
        return None

    # Check if the ROM file exists.
    if not os.path.exists(rom_path):
        # Display a critical error message box to the user.
        QMessageBox.critical(parent, "ROM Missing", f"ROM file not found:\n{rom_path}")
        # Print an error message to the console.
        print(f"❌ ROM missing: {rom_path}")
        # Return None as the launch failed.
        return None

    # ----- LAUNCH -----
    try:
        # Print a message indicating the emulator and ROM being launched.
        print(f"""🎮 Launching emulator: {emulator}
   ROM: {rom_path}""")
        # Launch the emulator as a subprocess with the ROM path as an argument.
        proc = subprocess.Popen([emulator, rom_path])
    # Catch OSError if the subprocess creation fails.
    except OSError as e:
        # Display a critical error message box to the user.
        QMessageBox.critical(parent, "Launch Failed", str(e))
        # Print an error message to the console.
        print(f"❌ Launch error: {e}")
        # Return None as the launch failed.
        return None

    # ----- WATCH THREAD -----
    # Define a nested function to watch the launched process.
    def watcher(p: subprocess.Popen):
        # Wait for the process to terminate and get its exit code.
        code = p.wait()
        # If an on_exit callback function is provided, call it with the exit code.
        if callable(on_exit):
            on_exit(code)

    # Create and start a new daemon thread to run the watcher function.
    threading.Thread(target=watcher, args=(proc,), daemon=True).start()
    # Return the subprocess.Popen object.
    return proc
