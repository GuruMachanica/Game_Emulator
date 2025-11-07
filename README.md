# 🚀 Retro Launcher Ultimate: Your Gateway to Classic Gaming!

> **Rediscover your favorite retro games with a modern, sleek, and highly customizable launcher.** Inspired by Steam Big Picture, Retro Launcher Ultimate transforms your game collection into an immersive, easy-to-navigate experience. Built with Python and PyQt5, it intelligently organizes your ROMs, fetches stunning cover art, and seamlessly launches your preferred emulators, all wrapped in a smooth, animated interface.

---

## ✨ Features That Elevate Your Retro Gaming

-   **Steam Big Picture–Style UI**: Dive into a visually stunning and intuitive interface designed for large screens and controller navigation.
-   **Asynchronous Image Downloading**: Enjoy a fluid experience as cover art and game metadata are fetched in the background, ensuring your UI remains responsive.
-   **Multi-Emulator Support**: Effortlessly configure and switch between various emulators for different consoles (e.g., NES, SNES, GBA, N64, PS1, etc.), providing unparalleled flexibility.
-   **Automatic Cover Art & Metadata**: Say goodbye to manual organization! The launcher automatically identifies your games and retrieves high-quality cover art and essential metadata from the RAWG.io API.
-   **Smooth & Responsive Animations**: Experience polished transitions and animations that make navigating your game library a joy.
-   **Highly Configurable**: Tailor your experience with extensive customization options for themes, layouts, emulator paths, and more via a simple `config.json` file.
-   **Intelligent Caching**: Game lists, cover images, and metadata are cached locally for lightning-fast startup times and offline access.
-   **Controller Ready**: Designed from the ground up with robust controller support in mind, offering a true console-like experience.

---

## 🖼️ Visual Showcase

![Launcher Preview](docs/preview.png)

---

## ⚙️ Requirements

To get Retro Launcher Ultimate up and running, you'll need:

-   **Python 3.x**: The core language for the launcher.
-   **PyQt5**: For building the rich graphical user interface.
-   **requests**: To handle API calls for fetching game data.
-   **Pillow (PIL Fork)**: For image processing and manipulation.
-   **pygame**: Utilized for robust controller input handling and future enhancements.

---

## 🚀 Setup & Installation: Get Started in Minutes!

Follow these simple steps to set up your ultimate retro gaming hub:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/retro-launcher-ultimate.git
    cd retro-launcher-ultimate
    ```

2.  **Create and activate a virtual environment (highly recommended):**
    ```bash
    # On Windows
    python -m venv .venv
    .venv\Scripts\activate

    # On Linux/Mac
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Integrate your emulators:**
    Place your preferred emulator executables (e.g., `snes9x.exe`, `nestopia.exe`, `visualboyadvance.exe`) into the `emulators/` folder. The launcher will automatically detect them.

5.  **Organize your ROMs:**
    Populate the `roms/` folder with your game ROMs. For optimal organization and detection, create subdirectories for each console (e.g., `roms/NES`, `roms/SNES`, `roms/GBA`).

6.  **Configure your RAWG API key:**
    -   Visit [RAWG.io API Docs](https://rawg.io/apidocs) and register for a free account to obtain your unique API key.
    -   Open the `config.json` file (it will be created on first run or you can create it manually from `config.py` defaults) and add your key:
        ```json
        {
            "rawg_api_key": "YOUR_RAWG_KEY_HERE",
            "emulator_paths": {
                "NES": "emulators/nestopia.exe",
                "SNES": "emulators/snes9x.exe",
                "GBA": "emulators/visualboyadvance.exe"
            },
            "rom_paths": {
                "NES": "roms/NES",
                "SNES": "roms/SNES",
                "GBA": "roms/GBA"
            }
            // ... other configuration settings
        }
        ```
        *Note: The `config.json` file allows you to customize emulator paths, ROM directories, themes, and other launcher behaviors. Refer to `config.py` for default values and available options.*

7.  **Launch the application:**
    ```bash
    python main.py
    ```
    Enjoy your newly organized retro gaming library!

---
## 🎮 Supported Emulators

| Console | Emulator(s) |
|---|---|
| NES | Nestopia |
| SNES | Snes9x |
| GBA | Visual Boy Advance |

---

## 📂 Project Architecture: A Glimpse Under the Hood

The Retro Launcher Ultimate is built with a modular design, ensuring maintainability and extensibility:

-   **`main.py`**: The primary entry point of the application. It initializes the PyQt5 application, loads the main UI, and orchestrates the initial setup.
-   **`config.py`**: Manages all application settings. It's responsible for loading configurations from `config.json` (or creating it with defaults if it doesn't exist) and saving any changes made by the user.
-   **`games.py`**: This module is the brain behind your game library. It scans the designated `roms` directories, identifies game files, extracts relevant information, and can optionally load pre-defined game metadata from `data/games.json`.
-   **`images.py`**: Handles all aspects of image management. It asynchronously downloads cover art from RAWG.io, resizes and optimizes images for display, and caches them locally in `resources/covers/` to ensure fast loading times.
-   **`launcher.py`**: The core logic for launching games. Given a selected game and its associated emulator, this module constructs the correct command-line arguments and executes the emulator process.
-   **`ui_bigpicture.py`**: Defines the entire graphical user interface. This module implements the Steam Big Picture-style layout, handles user interactions, manages animated transitions, and displays game information and cover art.

---

## 💡 Future Enhancements: What's Next?

We're constantly working to improve Retro Launcher Ultimate. Here are some features planned for future releases:

-   **Advanced Controller/Joystick Support**: Full, seamless navigation and game launching using a wide range of gamepads.
-   **Comprehensive Search and Filter**: Quickly locate any game in your vast library using powerful search and filtering options (by console, genre, year, etc.).
-   **Playtime Tracking & Statistics**: Keep a detailed log of how long you've played each game, with statistics and achievements.
-   **Favorites System**: Mark and easily access your most cherished games.
-   **Dynamic Theming Engine**: More built-in themes (CRT, neon, dark mode, custom color palettes) and easier ways for users to create and share their own.
-   **Multi-Language Support**: Localize the launcher into various languages.
-   **Game Details View**: A dedicated screen for each game showing descriptions, screenshots, and more.

---

## 🛠️ Troubleshooting

-   **Images not loading?** Ensure your `rawg_api_key` in `config.json` is correct and that you have an active internet connection.
-   **Emulator not launching?** Double-check the emulator paths in your `config.json` file and make sure the emulator executables are in the correct location.
-   **Controller not working?** Make sure your controller is properly connected and configured in your operating system.

---

## 💻 Supported Platforms

This launcher has been tested on **Windows 10/11**. While it may work on other operating systems, it is not officially supported at this time.

---

## 🧑‍💻 Contributing to the Project

We welcome contributions from the community! If you'd like to help make Retro Launcher Ultimate even better, please follow these guidelines:

1.  **Fork the repository** on GitHub.
2.  **Create a new branch** for your feature or bug fix: (`git checkout -b feature/your-new-feature` or `git checkout -b bugfix/issue-description`).
3.  **Make your changes**, ensuring they adhere to the existing code style and conventions.
4.  **Write clear, concise commit messages** (`git commit -m 'feat: Add new feature X'` or `fix: Resolve bug Y`).
-   **Push your changes** to your forked repository: (`git push origin feature/your-new-feature`).
-   **Open a Pull Request** to the `main` branch of the original repository, describing your changes in detail.

---

## 📜 License

This project is proudly licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full details.

---

## 💖 Credits & Acknowledgements

-   Developed with passion by [Mohammad Huzaifa](https://github.com/GuruMachanica)
-   Inspired by the elegant design of Steam Big Picture and the versatility of RetroArch.
-   Game covers and metadata generously provided by [RAWG.io](https://rawg.io/) and [IGDB](https://www.igdb.com/).
-   Special thanks to the Python and PyQt5 communities for their invaluable resources and support.
