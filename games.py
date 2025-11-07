"""
games.py
---------
Handles discovering available games for the Retro Launcher.
It first tries to load `data/games.json` (for metadata and cover URLs).
If that file doesn't exist, it scans the `roms/` directory automatically.
"""

# Import the os module for interacting with the operating system, e.g., for file path operations.
import os
# Import the json module for working with JSON data.
import json

# Define a tuple of supported ROM file extensions that the launcher recognizes.
SUPPORTED_EXTS = (".nes", ".smc", ".sfc", ".gba", ".gbc", ".gb")


# Define a function to scan for ROMs, taking the configuration as an argument.
def scan_roms(cfg):
    """
    Loads the game list either from data/games.json or by scanning rom folders.

    Args:
        cfg (dict): The configuration dictionary (from config.json)
    Returns:
        list of dict: Each game has keys like name, console, rom_path, image_url...
    """

    # Construct the absolute path to the games.json file within the 'data' directory.
    data_file = os.path.join("data", "games.json")
    # Initialize an empty list to store game information.
    games = []

    # ----- CASE 1: Attempt to load game data from games.json -----
    # Check if the games.json file exists at the specified path.
    if os.path.exists(data_file):
        try:
            # Open the games.json file for reading with UTF-8 encoding.
            with open(data_file, "r", encoding="utf-8") as f:
                # Load the JSON data from the file into the 'loaded' variable.
                loaded = json.load(f)

                # Iterate over each game entry in the loaded data.
                for g in loaded:
                    # Get the console type (e.g., NES, SNES, GBA) for the current game.
                    console = g.get("console")
                    # Get the full path to the ROM file for the current game.
                    path = g.get("rom_path")

                    # Skip invalid entries that do not have sufficient information (missing console or path).
                    if not console or not path:
                        # Print a warning message for invalid entries.
                        print(f"⚠️  Skipping invalid entry (missing console/path): {g}")
                        # Move to the next iteration of the loop.
                        continue

                    # Convert relative ROM paths to absolute paths for consistent handling.
                    if not os.path.isabs(path):
                        # Convert the relative path to an absolute path.
                        path = os.path.abspath(path)

                    # Ensure a unique "key" exists for internal use, generating one if missing.
                    g["rom_path"] = path
                    g["key"] = g.get("key", f"{console}::{g.get('name', 'Unknown')}")
                    # Add the processed game dictionary to the 'games' list.
                    games.append(g)

        # Catch exceptions related to JSON decoding errors or I/O operations.
        except (json.JSONDecodeError, IOError) as e:
            # Print an error message if loading from games.json fails.
            print(f"❌ Error loading data/games.json: {e}")

    # ----- CASE 2: If no games were loaded from JSON, scan ROM folders -----
    # Check if the 'games' list is still empty, indicating games.json was not loaded or was empty/corrupt.
    if not games:
        # Get the ROMs directory from the configuration, defaulting to "roms" if not specified.
        roms_dir = cfg.get("roms_dir", "roms")

        # Check if the specified ROMs directory exists and is a directory.
        if not os.path.isdir(roms_dir):
            # Print a warning if the ROMs directory is not found.
            print("⚠️  No ROMs directory found:", roms_dir)
            # Return an empty list as no ROMs could be scanned.
            return []

        # Iterate over each console subdirectory within the ROMs directory, sorted alphabetically.
        for console in sorted(os.listdir(roms_dir)):
            # Construct the full path to the current console directory.
            cpath = os.path.join(roms_dir, console)
            # Skip if the current path is not a directory.
            if not os.path.isdir(cpath):
                continue

            # Iterate over each file within the current console directory, sorted alphabetically.
            for file in sorted(os.listdir(cpath)):
                # Check if the file's extension is among the supported ROM extensions (case-insensitive).
                if file.lower().endswith(SUPPORTED_EXTS):
                    # Extract the game name from the filename (without the extension).
                    name = os.path.splitext(file)[0]
                    # Construct the absolute path to the ROM file.
                    rom_path = os.path.abspath(os.path.join(cpath, file))

                    # Append a new dictionary representing the discovered game to the 'games' list.
                    games.append({
                        # Create a unique key for the game using console and name.
                        "key": f"{console}::{name}",
                        # Store the extracted game name.
                        "name": name,
                        # Store the console type.
                        "console": console,
                        # Store the original filename.
                        "file": file,
                        # Store the absolute path to the ROM file.
                        "rom_path": rom_path
                    })

    # Print a confirmation message indicating the total number of games loaded.
    print(f"✅ Loaded {len(games)} games.")
    # Return the final list of discovered games.
    return games
