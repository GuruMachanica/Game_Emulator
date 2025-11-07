"""
ui_bigpicture.py
----------------
Steam Big Picture-style user interface.
Displays game posters, handles smooth focus animations, and launches games.
"""

# Import necessary widgets from PyQt5.QtWidgets module.
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QGridLayout,
    QScrollArea, QSizePolicy, QGraphicsDropShadowEffect, QMessageBox
)
# Import necessary classes from PyQt5.QtGui module.
from PyQt5.QtGui import QPixmap, QFont
# Import necessary classes from PyQt5.QtCore module.
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSlot, pyqtSignal
# Import partial for creating partial functions, useful for connecting signals to slots with arguments.
from functools import partial
# Import the os module for interacting with the operating system, e.g., for file path operations.
import os

# Import the ImageFetcher class from the local images module for asynchronous image downloading.
from images import ImageFetcher
# Import the scan_roms function from the local games module for discovering available games.
from games import scan_roms
# Import the find_emulator and launch_and_watch functions from the local launcher module for game execution.
from launcher import find_emulator, launch_and_watch

# --- UI Constants ---
# Define the default width and height for a game poster card.
SMALL_W, SMALL_H = 220, 300
# Define the expanded width and height for a game poster card when it is focused.
LARGE_W, LARGE_H = 320, 430
# Define the duration of UI animations in milliseconds.
ANIM_MS = 200

# Define the PosterCard class, which represents a single game poster in the UI.
class PosterCard(QWidget):
    """
    Represents a single game poster card.
    Expands when focused, shrinks when unfocused, and is clickable.
    """
    # Define a custom signal that is emitted when the card is clicked.
    clicked = pyqtSignal()

    # Initialize the PosterCard instance.
    def __init__(self, game, placeholder, parent=None):
        # Call the constructor of the parent class (QWidget).
        super().__init__(parent)
        # Store the game data associated with this card.
        self.game = game

        # --- Layout Setup ---
        # Create a vertical box layout for arranging elements within the card.
        self.layout = QVBoxLayout()
        # Set the margins around the content within the layout.
        self.layout.setContentsMargins(6, 6, 6, 6)
        # Apply the created layout to this widget.
        self.setLayout(self.layout)

        # --- Game Cover ---
        # Create a QLabel to display the game cover image.
        self.cover = QLabel()
        # Set a fixed size for the cover image display area.
        self.cover.setFixedSize(SMALL_W, SMALL_H)
        # Enable scaling of the image to fit the label's size.
        self.cover.setScaledContents(True)
        # Set an initial placeholder image for the cover.
        self.cover.setPixmap(placeholder)
        # Set the size policy to fixed, preventing the cover from resizing with its parent.
        self.cover.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Add drop shadow for depth
        # Create a QGraphicsDropShadowEffect for visual depth.
        self.shadow = QGraphicsDropShadowEffect()
        # Set the blur radius for the shadow effect.
        self.shadow.setBlurRadius(8)
        # Apply the shadow effect to the cover QLabel.
        self.cover.setGraphicsEffect(self.shadow)

        # --- Title Label ---
        # Create a QLabel to display the game title, defaulting to "Unknown" if not found.
        self.title = QLabel(self.game.get("name", "Unknown"))
        # Align the title text to the center.
        self.title.setAlignment(Qt.AlignCenter)
        # Set the font for the title, making it bold.
        self.title.setFont(QFont("Consolas", 10, QFont.Bold))

        # --- Assemble ---
        # Add the cover QLabel to the layout, centered horizontally.
        self.layout.addWidget(self.cover, alignment=Qt.AlignCenter)
        # Add the title QLabel to the layout.
        self.layout.addWidget(self.title)

        # --- Animation Setup ---
        # Create a QPropertyAnimation to animate the 'geometry' property of the cover QLabel.
        self.anim = QPropertyAnimation(self.cover, b"geometry")
        # Set the easing curve for a smooth animation effect.
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        # Set the duration of the animation.
        self.anim.setDuration(ANIM_MS)

    # Override the mouseReleaseEvent to detect clicks on the card.
    def mouseReleaseEvent(self, event):
        # Emit the custom 'clicked' signal when the mouse button is released over the card.
        self.clicked.emit()

    # Define a method to set the cover image of the card.
    def set_cover(self, path):
        # Check if the provided image file path exists.
        if os.path.exists(path):
            # Create a QPixmap object from the image file.
            pix = QPixmap(path)
            # Check if the QPixmap was loaded successfully (not null).
            if not pix.isNull():
                # Set the pixmap for the cover QLabel, scaling it to fit while maintaining aspect ratio.
                self.cover.setPixmap(
                    pix.scaled(self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )

    # Define a method to smoothly expand the card's cover image.
    def expand(self):
        # Get the current geometry of the cover QLabel.
        start = self.cover.geometry()
        # Calculate the target geometry for the expanded state.
        end = QRect(
            start.x() - ((LARGE_W - SMALL_W) // 2),
            start.y() - ((LARGE_H - SMALL_H) // 2),
            LARGE_W, LARGE_H
        )
        # Stop any ongoing animation to prevent conflicts.
        self.anim.stop()
        # Set the starting value of the animation to the current geometry.
        self.anim.setStartValue(start)
        # Set the ending value of the animation to the calculated expanded geometry.
        self.anim.setEndValue(end)
        # Start the animation.
        self.anim.start()
        # Increase the blur radius of the shadow for a more pronounced effect when expanded.
        self.shadow.setBlurRadius(20)

    # Define a method to smoothly shrink the card's cover image.
    def shrink(self):
        # Get the current geometry of the cover QLabel.
        start = self.cover.geometry()
        # Calculate the target geometry for the shrunk state.
        end = QRect(
            start.x() + ((LARGE_W - SMALL_W) // 2),
            start.y() + ((LARGE_H - SMALL_H) // 2),
            SMALL_W, SMALL_H
        )
        # Stop any ongoing animation.
        self.anim.stop()
        # Set the starting value of the animation to the current geometry.
        self.anim.setStartValue(start)
        # Set the ending value of the animation to the calculated shrunk geometry.
        self.anim.setEndValue(end)
        # Start the animation.
        self.anim.start()
        # Reset the blur radius of the shadow to its default value.
        self.shadow.setBlurRadius(8)


# Define the BigPictureWindow class, which is the main application window.
class BigPictureWindow(QMainWindow):
    """Main UI window class."""

    # Initialize the BigPictureWindow instance.
    def __init__(self, cfg):
        # Call the constructor of the parent class (QMainWindow).
        super().__init__()
        # Store the application configuration.
        self.cfg = cfg
        # Set the title of the main window.
        self.setWindowTitle("Retro Launcher — Big Picture")
        # Set the initial position and size of the window.
        self.setGeometry(50, 50, 1280, 800)

        # Placeholder cover (grey)
        # Create a QPixmap to serve as a placeholder for game covers.
        placeholder = QPixmap(SMALL_W, SMALL_H)
        # Fill the placeholder pixmap with a dark gray color.
        placeholder.fill(Qt.darkGray)
        # Store the placeholder pixmap as an instance variable.
        self.placeholder = placeholder

        # Asynchronous image fetcher
        # Create an instance of the ImageFetcher to handle downloading game cover images.
        self.fetcher = ImageFetcher(cfg)
        # Connect the 'image_ready' signal from the fetcher to the 'on_image_ready' slot in this window.
        self.fetcher.image_ready.connect(self.on_image_ready)

        # --- Scrollable Grid Layout ---
        # Create a central widget to hold the main layout.
        root = QWidget()
        # Create a vertical box layout for the root widget.
        layout = QVBoxLayout(root)

        # Create a QScrollArea to allow scrolling if content exceeds visible area.
        self.scroll = QScrollArea()
        # Make the widget inside the scroll area resizable.
        self.scroll.setWidgetResizable(True)

        # Create a container widget that will hold the grid of game cards.
        self.container = QWidget()
        # Create a QGridLayout for arranging game cards in a grid.
        self.grid = QGridLayout(self.container)
        # Set the spacing between items in the grid.
        self.grid.setSpacing(18)

        # Set the container widget as the scroll area's widget.
        self.scroll.setWidget(self.container)
        # Add the scroll area to the main vertical layout.
        layout.addWidget(self.scroll)
        # Set the root widget as the central widget of the QMainWindow.
        self.setCentralWidget(root)

        # --- Load Game Data ---
        # Scan for available ROMs and load game data using the configuration.
        self.games = scan_roms(cfg)
        # Initialize an empty list to store PosterCard objects.
        self.cards = []
        # Initialize the index of the currently selected card to 0.
        self.selected = 0

        # Populate the grid with game poster cards.
        self._populate_grid()

        # Highlight the first card if any games were loaded.
        if self.cards:
            # Call the _focus method to highlight the first card.
            self._focus(0)

    # ----- UI Construction -----
    # Define a method to populate the grid layout with game poster cards.
    def _populate_grid(self):
        # Iterate through existing items in the grid in reverse order to remove them.
        for i in reversed(range(self.grid.count())):
            # Get the widget at the current grid index.
            w = self.grid.itemAt(i).widget()
            # If a widget exists, remove it from its parent (and thus from the layout).
            if w:
                w.setParent(None)

        # Initialize row and column counters for grid placement.
        r = c = 0
        # Define the number of cards to display per row.
        per_row = 4

        # Iterate through the list of games with their index.
        for idx, g in enumerate(self.games):
            # Create a PosterCard for each game, using the placeholder image.
            card = PosterCard(g, self.placeholder)
            # Connect the card's 'clicked' signal to the '_on_card_clicked' slot, passing the card's index.
            card.clicked.connect(partial(self._on_card_clicked, idx))
            # Add the card to the grid layout at the current row and column.
            self.grid.addWidget(card, r, c)
            # Add the created card to the list of cards.
            self.cards.append(card)

            # Start asynchronous image download for the game's cover if an image URL is available.
            self.fetcher.fetch(g["key"], g["name"], g.get("image_url"))

            # Increment the column counter.
            c += 1
            # If the current row is full, reset the column counter and move to the next row.
            if c >= per_row:
                c = 0
                r += 1

    # ----- Image Handler -----
    # Decorate the method as a PyQt slot that accepts two string arguments (key and path).
    @pyqtSlot(str, str)
    # Define the slot to handle the 'image_ready' signal from the ImageFetcher.
    def on_image_ready(self, key, path):
        # Iterate through all existing PosterCard objects.
        for card in self.cards:
            # If the game key of the card matches the key received from the signal.
            if card.game["key"] == key:
                # Set the downloaded image as the cover for this card.
                card.set_cover(path)
                # Exit the loop once the matching card is found and updated.
                break

    # ----- Keyboard Navigation -----
    # Override the keyPressEvent method to handle keyboard input for navigation.
    def keyPressEvent(self, ev):
        # If there are no cards, do nothing.
        if not self.cards:
            return

        # Define the number of columns in the grid for navigation calculations.
        cols = 4
        # Get the index of the currently selected card.
        idx = self.selected

        # Handle Right arrow key press.
        if ev.key() == Qt.Key_Right:
            # Move to the next card, wrapping around to the beginning if at the end.
            idx = (idx + 1) % len(self.cards)
        # Handle Left arrow key press.
        elif ev.key() == Qt.Key_Left:
            # Move to the previous card, wrapping around to the end if at the beginning.
            idx = (idx - 1) % len(self.cards)
        # Handle Down arrow key press.
        elif ev.key() == Qt.Key_Down:
            # Move down one row, wrapping around if at the bottom.
            idx = (idx + cols) % len(self.cards)
        # Handle Up arrow key press.
        elif ev.key() == Qt.Key_Up:
            # Move up one row, wrapping around if at the top.
            idx = (idx - cols) % len(self.cards)
        # Handle Enter or Return key press.
        elif ev.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Play the game associated with the currently selected card.
            self._play(self.cards[self.selected].game)
            # Return to prevent further processing of this key event.
            return

        # After handling navigation keys, focus on the newly calculated index.
        self._focus(idx)

    # ----- Focus Animation -----
    # Define a method to manage the focus state and animation of cards.
    def _focus(self, idx):
        # If there are no cards, do nothing.
        if not self.cards:
            return
        # Shrink previous
        # Check if the previously selected index is valid.
        if 0 <= self.selected < len(self.cards):
            # Shrink the card that was previously focused.
            self.cards[self.selected].shrink()

        # Expand new
        # Update the selected index to the new index.
        self.selected = idx
        # Expand the newly selected card.
        self.cards[self.selected].expand()
        # Ensure the newly selected card is visible within the scroll area, with some margin.
        self.scroll.ensureWidgetVisible(self.cards[self.selected], xMargin=40, yMargin=40)

    # ----- Click Action -----
    # Define a slot to handle clicks on individual PosterCard objects.
    def _on_card_clicked(self, idx):
        # Focus on the clicked card.
        self._focus(idx)
        # Play the game associated with the clicked card.
        self._play(self.cards[idx].game)

    # ----- Game Launch -----
    # Define a method to initiate playing a game.
    def _play(self, game):
        # Get the console type from the game data.
        console = game.get("console")
        # Get the ROM file path from the game data.
        rom_path = game.get("rom_path")

        # Validate data before launching
        # Check if essential game information (console or ROM path) is missing.
        if not console or not rom_path:
            # Display a critical error message to the user.
            QMessageBox.critical(self, "Invalid Game", "Game is missing required information (console or path).")
            # Print an error message to the console.
            print("❌ Invalid game:", game)
            # Stop the launch process.
            return

        # Find the appropriate emulator executable for the game's console.
        em = find_emulator(self.cfg, console)
        # Check if an emulator was found.
        if not em:
            # Display a warning message to the user if no emulator is configured.
            QMessageBox.warning(self, "No Emulator", f"No emulator configured for {console}.")
            # Print an error message to the console.
            print("❌ Emulator not found for:", console)
            # Stop the launch process.
            return

        # Check if the ROM file actually exists at the specified path.
        if not os.path.exists(rom_path):
            # Display a warning message to the user if the ROM file is not found.
            QMessageBox.warning(self, "ROM Not Found", f"ROM file not found:\n{rom_path}")
            # Print an error message to the console.
            print("❌ ROM not found:", rom_path)
            # Stop the launch process.
            return

        # Print a message to the console indicating the game being launched.
        print(f"🎮 Launching {game['name']} ({console}) with {em}")
        # Launch the emulator with the ROM and set up a callback for when the game exits.
        launch_and_watch(em, rom_path, on_exit=lambda rc: print(f"Game exited with code {rc}"), parent=self)
