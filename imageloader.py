import sys

from PIL import Image
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap

from osm.slippyTileUtil import tile_to_latlon


class ImageLoader(QThread):
    progress_updated = pyqtSignal(int)
    images_loaded = pyqtSignal(dict)
    bottom_right_loaded = pyqtSignal(dict)
    top_left_loaded = pyqtSignal(dict)

    def __init__(self, quizmaster, zoom_levels):
        super().__init__()
        self.quizmaster = quizmaster
        self.zoom_levels = zoom_levels
        self.background_images = {}
        self.backgroundTopLeft = {}
        self.backgroundBottomRight = {}

    def run(self):
        # Create progress bar
        processed_tiles = 0

        for zoom_level in self.zoom_levels:
            start_x = sys.maxsize
            start_y = sys.maxsize
            end_x = 0
            end_y = 0

            for x, y, zoom in self.quizmaster.relevant_tiles:
                if zoom == zoom_level:
                    if x < start_x:
                        start_x = x
                    if y < start_y:
                        start_y = y
                    if x > end_x:
                        end_x = x
                    if y > end_y:
                        end_y = y

            self.backgroundTopLeft[zoom_level] = self.getTopLeftCorner(start_x, start_y, zoom_level)
            self.backgroundBottomRight[zoom_level] = self.getBottomRightCorner(end_x, end_y, zoom_level)

            total_width = (end_x - start_x) * 256
            total_height = (end_y - start_y) * 256

            image = Image.new('RGB', (total_width, total_height))

            for x, y, zoom in self.quizmaster.relevant_tiles:
                if zoom != zoom_level:
                    continue
                tile_path = f"/Users/verwilst/PycharmProjects/mapQuiz/resources/images/{zoom}/{x}-{y}-blurred.jpg"
                tile_image = Image.open(tile_path)
                image.paste(tile_image, ((x - start_x) * 256, (y - start_y) * 256))
                processed_tiles += 1

                progress_percentage = int((processed_tiles / len(self.quizmaster.relevant_tiles)) * 100)
                self.progress_updated.emit(progress_percentage)

            # Convert the PIL image to a QImage
            q_image = QImage(image.tobytes(), total_width, total_height, QImage.Format_RGB888)
            self.background_images[zoom_level] = QPixmap.fromImage(q_image)

        self.bottom_right_loaded.emit(self.backgroundBottomRight)
        self.top_left_loaded.emit(self.backgroundTopLeft)
        self.images_loaded.emit(self.background_images)

    def getTopLeftCorner(self, x, y, zoom):
        lat, lon = tile_to_latlon(x, y, zoom)
        lat1, lon1 = tile_to_latlon(x, y, zoom)
        return (lon1 + lon) / 2, (lat + lat1) / 2

    def getBottomRightCorner(self, x, y, zoom):
        lat, lon = tile_to_latlon(x, y, zoom)
        lat1, lon1 = tile_to_latlon(x, y, zoom)
        return (lon1 + lon) / 2, (lat + lat1) / 2
