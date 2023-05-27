import random
import keyword
from PyQt5.QtGui import QPixmap, QPalette, QBrush
import os
from KlausSrc.Utilities.config import wallpaperDirectory
from KlausSrc.Utilities.HelperFunctions import makePath

def changeWallpaper(self):
    # Set the background image
    random_filePath = random.choice(wallpaperDirectory)
    background_image = QPixmap(random_filePath)
    # Create a QPalette and set the QPixmap as its brush.
    palette = QPalette()
    palette.setBrush(QPalette.Background, QBrush(background_image))

    # Apply the palette to the window.
    self.setPalette(palette)

