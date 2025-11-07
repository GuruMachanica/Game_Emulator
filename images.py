"""
images.py
---------
Thread-safe asynchronous image downloader for game covers.
"""

# Import the os module for interacting with the operating system, e.g., for file path operations.
import os
# Import the threading module for creating and managing threads.
import threading
# Import the requests library for making HTTP requests.
import requests
# Import quote_plus from urllib.parse for URL encoding.
from urllib.parse import quote_plus
# Import QObject and pyqtSignal from PyQt5.QtCore for Qt-related object and signal/slot mechanisms.
from PyQt5.QtCore import QObject, pyqtSignal


# Define the ImageFetcher class, which inherits from QObject to utilize Qt's signal/slot system.
class ImageFetcher(QObject):
    """
    Downloads and caches cover images for games.

    Emits a signal `image_ready(game_key, local_path)` when an image is 
    successfully downloaded.
    """

    # Define a PyQt signal that will be emitted when an image is ready, carrying the game key and local path.
    image_ready = pyqtSignal(str, str)

    # Initialize the ImageFetcher instance.
    def __init__(self, cfg: dict):
        # Call the constructor of the parent class (QObject).
        super().__init__()
        # Store the configuration dictionary.
        self.cfg = cfg
        # Get the covers directory from the configuration, defaulting to "resources/covers".
        self.covers_dir = self.cfg.get("covers_dir", "resources/covers")
        # Create the covers directory if it doesn't already exist.
        os.makedirs(self.covers_dir, exist_ok=True)
        # Get and strip the RAWG API key from the configuration.
        self.api_key = self.cfg.get("rawg_api_key", "").strip()

    # Define the fetch method to start a background image download.
    def fetch(self, game_key: str, game_name: str, image_url: str = None) -> None:
        """Starts a background thread to fetch an image for a game."""
        # Determine the local path where the image should be saved.
        local_path = self._local_path_for(game_key)

        # If the image already exists locally, emit the signal immediately and return.
        if os.path.exists(local_path):
            self.image_ready.emit(game_key, local_path)
            return

        # Create a new background thread to perform the image fetching.
        thread = threading.Thread(
            target=self._worker,
            args=(game_key, game_name, image_url, local_path),
            daemon=True, # Set the thread as a daemon so it exits when the main program exits.
        )
        # Start the background thread.
        thread.start()

    # Define a private method to generate a safe local filename for a cover image.
    def _local_path_for(self, key: str) -> str:
        """Generates a safe local filename for the cover image."""
        # Sanitize the key to create a safe filename, replacing non-alphanumeric characters with underscores.
        safe_key = "".join(c if c.isalnum() or c in ("_", "-", ".") else "_" for c in key)
        # Join the covers directory with the safe key and a .png extension to form the full local path.
        return os.path.join(self.covers_dir, f"{safe_key}.png")

    # Define the worker method that runs in the background thread to download images.
    def _worker(self, key: str, name: str, url: str, local_path: str) -> None:
        """
        Worker thread that attempts to download an image from a URL or the RAWG API.
        """
        # Attempt to download the image from the provided URL if available.
        if url and self._try_download(url, local_path):
            # If successful, emit the image_ready signal.
            self.image_ready.emit(key, local_path)
            return

        # If a RAWG API key is available, attempt to fetch the image from the RAWG API.
        if self.api_key and self._try_fetch_from_rawg(name, local_path):
            # If successful, emit the image_ready signal.
            self.image_ready.emit(key, local_path)
            return

        # If neither method succeeds, emit the image_ready signal with an empty local path.
        self.image_ready.emit(key, "")

    # Define a private method to attempt downloading an image from a given URL.
    def _try_download(self, url: str, local_path: str) -> bool:
        """Downloads an image from a URL and saves it locally."""
        try:
            # Make an HTTP GET request to the URL with a timeout and stream enabled.
            response = requests.get(url, timeout=10, stream=True)
            # Raise an exception for bad HTTP status codes (4xx or 5xx).
            response.raise_for_status()

            # Create a temporary path for the download to ensure atomic file replacement.
            tmp_path = f"{local_path}.tmp"
            # Open the temporary file in binary write mode.
            with open(tmp_path, "wb") as f:
                # Iterate over the response content in chunks and write to the file.
                for chunk in response.iter_content(8192):
                    f.write(chunk)

            # Atomically replace the old file (if any) with the newly downloaded one.
            os.replace(tmp_path, local_path)
            # Return True indicating a successful download.
            return True
        # Catch any request-related exceptions.
        except requests.exceptions.RequestException as e:
            # Print a warning message if the image download fails.
            print(f"⚠️ Image download failed from {url}: {e}")
            # Return False indicating a failed download.
            return False

    # Define a private method to attempt fetching an image from the RAWG API.
    def _try_fetch_from_rawg(self, name: str, local_path: str) -> bool:
        """Fetches an image from the RAWG API and saves it locally."""
        try:
            # URL-encode the game name for the API query.
            query = quote_plus(name)
            # Construct the RAWG API URL for searching games.
            rawg_url = f"https://api.rawg.io/api/games?search={query}&page_size=1&key={self.api_key}"
            # Make an HTTP GET request to the RAWG API with a timeout.
            response = requests.get(rawg_url, timeout=8)
            # Raise an exception for bad HTTP status codes.
            response.raise_for_status()

            # Parse the JSON response and get the 'results' array.
            data = response.json().get("results")
            # Check if data exists and if the first result has a 'background_image'.
            if data and data[0].get("background_image"):
                # Extract the image URL from the API response.
                image_url = data[0]["background_image"]
                # Attempt to download the image using the extracted URL.
                return self._try_download(image_url, local_path)

        # Catch any request-related exceptions.
        except requests.exceptions.RequestException as e:
            # Print an error message if fetching from RAWG API fails.
            print(f"RAWG fetch error for {name}: {e}")

        # Return False if fetching from RAWG API fails or no image is found.
        return False