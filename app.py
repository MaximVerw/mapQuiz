import sys

from PIL import Image
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QCompleter, QPushButton, QProgressBar, QApplication
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QImage, QMouseEvent
from PyQt5.QtCore import Qt, QSize, QTimer

from controller.quizmaster import QuizMaster
from osm.slippyTileUtil import coordToPixel, tile_to_latlon, latlon_to_tile


class App(QMainWindow):
    def __init__(self, waysByName, defaults, area_in_scope):
        super().__init__()
        self.setWindowTitle("JPG Background with Text Box")
        self.width = 1280
        self.height = 720
        self.scale = 2.
        self.setGeometry(100, 100, self.width, self.height+70)  # Set the window size to 512 by 512 pixels
        self.defaults = defaults
        self.zoom_levels = [13,14,15, 16, 17, 18, 19]
        self.zoom = 19
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.quizmaster = QuizMaster(waysByName, area_in_scope, self.zoom_levels)

        # Load the image from the local file system
        self.loadBackgroundImages()

        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width, self.height) # Set QLabel geometry
        self.background_label.setAlignment(Qt.AlignCenter)

        self.getNewStreet()

        try:
            self.create_text_box()

            # Button to refresh the background image
            self.refresh_button = QPushButton("Zoom out", self)
            self.refresh_button.setGeometry(self.width/2-150, self.height + 40, 100, 25)
            self.refresh_button.clicked.connect(self.plus_one)
            self.refresh_button_2 = QPushButton("Zoom in", self)
            self.refresh_button_2.setGeometry(self.width/2+50, self.height + 40, 100, 25)
            self.refresh_button_2.clicked.connect(self.minus_one)

        except FileNotFoundError:
            print("Error: File not found.")
        except Exception as e:
            print("Error loading image:", e)

    def getNewStreet(self):
        newStreet = self.quizmaster.pollNewStreet()
        self.scale = 1.
        if newStreet is None:
            exit(0)
        streetGeometry = self.quizmaster.getGeometry()
        self.drawGeometry(streetGeometry)

    def plus_one(self):
        self.plus(2.)
    def plus(self, amount = 2.):
        self.offset_x = round(self.offset_x/amount)
        self.offset_y = round(self.offset_y/amount)
        self.scale *= amount
        streetGeometry = self.quizmaster.getGeometry()
        self.drawGeometry(streetGeometry)

    def minus_one(self):
        self.minus(2.)

    def minus(self, amount = 2.):
        self.offset_x = round(amount*self.offset_x)
        self.offset_y = round(amount*self.offset_y)
        self.scale /= amount
        streetGeometry = self.quizmaster.getGeometry()
        self.drawGeometry(streetGeometry)

    def print_text(self):
        text = self.text_box.text()
        if (self.quizmaster.guess(text)):
            self.clear_text_box() # Clear the text box after printing the text
            self.getNewStreet()

    def create_text_box(self):
        # Create a text box
        self.text_box = QLineEdit(self)
        self.text_box.setGeometry(self.width / 2 - 100, self.height + 10, 200, 25)

        # Fixed options for autocomplete
        completer = QCompleter(self.defaults)  # Use custom completer
        self.text_box.setCompleter(completer)

        # Connect activated signal to clear the text box
        completer.activated.connect(self.clear_text_box)

        # Connect returnPressed signal to print_text method
        self.text_box.returnPressed.connect(self.print_text)

    def clear_text_box(self):
        QTimer.singleShot(0, self.text_box.clear)
        #self.text_box.clear()

    def drawGeometry(self, streetGeometry):
        rescaled_bbox = self.getRescaledBbox(streetGeometry)

        # Convert coordinates to pixel coordinates
        pixels = []
        for geom in streetGeometry.geoms:
            pixel_coords = []
            for coord in geom.coords[:]:
                pixel_coords.append(coordToPixel(coord[1], coord[0], rescaled_bbox, self.width, self.height, self.offset_x, self.offset_y))
            pixels.append(pixel_coords)

        # Create a white QImage
        image = QImage(self.width, self.height, QImage.Format_RGB32)
        image.fill(Qt.white)

        zoom_level = self.determine_zoom(rescaled_bbox, streetGeometry.centroid)

        pixmap = QPixmap.fromImage(image)

        topLeft = coordToPixel(self.backgroundTopLeft[zoom_level][1], self.backgroundTopLeft[zoom_level][0],
                               rescaled_bbox, self.width, self.height, self.offset_x, self.offset_y)
        bottomRight = coordToPixel(self.backgroundBottomRight[zoom_level][1],
                                   self.backgroundBottomRight[zoom_level][0], rescaled_bbox, self.width, self.height, self.offset_x, self.offset_y)

        painter = QPainter(pixmap)
        painter.drawPixmap(topLeft[0], topLeft[1], bottomRight[0]-topLeft[0], bottomRight[1]-topLeft[1],
                           self.background_images[zoom_level])

        # Draw lines on the QLabel
        pen = QPen(QColor(255, 0, 0))  # Red color for the lines
        pen.setWidth(3)  # Set pen width
        painter.setPen(pen)
        for line in pixels:
            if len(line) > 1:
                for i in range(len(line) - 1):
                    x1, y1 = line[i]
                    x2, y2 = line[i + 1]
                    painter.drawLine(x1, y1, x2, y2)
        painter.end()
        self.background_label.setPixmap(pixmap)

    def getRescaledBbox(self, geometry):
        minx, miny, maxx, maxy = geometry.bounds
        height = (maxy - miny)*self.scale
        width = (maxx - minx)*self.scale
        centroid = geometry.centroid


        # Calculate the scale factors for width and height
        target_aspect = self.width / self.height
        current_aspect = width / height

        if target_aspect > current_aspect:
            width_increase = height / self.height * self.width - width
            new_width = width + width_increase
            new_height = height
        else:
            height_increase = width / self.width * self.height - height
            new_width = width
            new_height = height + height_increase

        # Recalculate the new max and min coordinates based on the scaled dimensions
        new_minx = centroid.x - new_width / 2
        new_miny = centroid.y - new_height / 2
        new_maxx = centroid.x + new_width / 2
        new_maxy = centroid.y + new_height / 2

        # Update the bbox with the new coordinates
        return new_minx, new_miny, new_maxx, new_maxy

    def loadBackgroundImages(self):
        self.background_images = {}
        self.backgroundTopLeft = {}
        self.backgroundBottomRight = {}

        # Create progress bar
        progress_bar = QProgressBar(self)
        progress_bar.setGeometry(self.width/2-100, self.height/2, 200, 25)  # Adjust position and size as needed
        total_tiles = len(self.quizmaster.relevant_tiles)
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
                tile_path = f"/Users/verwilst/PycharmProjects/mapQuiz/resources/images/{zoom}/{x}-{y}-blurred.jpg"
                tile_image = Image.open(tile_path)
                image.paste(tile_image, ((x - start_x) * 256, (y - start_y) * 256))
                processed_tiles += 1
                progress_bar.setValue((processed_tiles / total_tiles) * 100)  # Update progress bar value

                print('trigger')
                QApplication.processEvents()

            # Convert the PIL image to a QImage
            q_image = QImage(image.tobytes(), total_width, total_height, QImage.Format_RGB888)
            self.background_images[zoom_level] = QPixmap.fromImage(q_image)

        progress_bar.deleteLater()  # Remove progress bar after loading is complete
        return self.background_images

    def getTopLeftCorner(self, x, y, zoom):
        lat, lon = tile_to_latlon(x, y, zoom)
        lat1, lon1 = tile_to_latlon(x, y, zoom)
        return (lon1+lon)/2,(lat+lat1)/2
    def getBottomRightCorner(self, x, y, zoom):
        lat, lon = tile_to_latlon(x, y, zoom)
        lat1, lon1 = tile_to_latlon(x, y, zoom)
        return (lon1+lon)/2,(lat+lat1)/2

    def determine_zoom(self, rescaled_bbox, centroid):
        lonPerPix = ((rescaled_bbox[2] - rescaled_bbox[0])/self.width)
        for zoom in self.zoom_levels:
            self.zoom = zoom
            x,y = latlon_to_tile(centroid.y, centroid.x, zoom)
            _, lon1 = tile_to_latlon(x, y, zoom)
            _, lon2 = tile_to_latlon(x+1, y, zoom)
            if lonPerPix*256 >= (lon2 - lon1):
                return self.zoom
        return self.zoom

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton or  event.button() == Qt.RightButton:
            self.dragging = True
            self.start_pos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            delta = event.pos() - self.start_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.start_pos = event.pos()
            streetGeometry = self.quizmaster.getGeometry()
            self.drawGeometry(streetGeometry)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton or  event.button() == Qt.RightButton:
            self.dragging = False

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120.  # Get the scroll value
        if(delta>0.):
            self.minus(1+delta)
        elif(delta<0.):
            self.plus(1-delta)

