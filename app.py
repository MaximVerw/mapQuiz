import platform
import random

from PyQt5.QtWidgets import QMainWindow, QLabel, QCompleter, QProgressBar, QApplication, QPushButton
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QImage, QMouseEvent, QIcon, QCloseEvent
from PyQt5.QtCore import Qt, QTimer

from quizmaster.quizmaster import QuizMaster
from widgets.MyLineEdit import MyLineEdit
from widgets.imageloader import ImageLoader
from osm.slippyTileUtil import coordToPixel, tile_to_latlon, latlon_to_tile

class App(QMainWindow):
    def __init__(self, waysByName, area_in_scope, easy_mode=False):
        super().__init__()
        self.easy_mode = easy_mode
        self.setWindowTitle("MapQuiz")
        desktop = QApplication.desktop()
        screen_rect = desktop.screenGeometry(desktop.screenNumber(self))
        self.width = screen_rect.width()
        self.height = screen_rect.height()-55
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint)
        self.scale = 4.
        self.setGeometry(0, 0, self.width, self.height+55)
        self.defaults = list(waysByName.keys())
        self.zoom_levels = [13, 14, 15, 16, 17, 18, 19]
        self.zoom = 19
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.quizmaster = QuizMaster(waysByName, area_in_scope, self.zoom_levels)
        self.hint = ""
        self.background_images = {}
        self.backgroundTopLeft = {}
        self.backgroundBottomRight = {}
        self.oldGeometry = None

        # Set application icon
        icon = None
        if platform.system() == 'Darwin':
            icon = QIcon("resources/logo/osm_logo.icns")
        elif platform.system() == 'Windows':
            icon = QIcon("resources/logo/osm_logo.png")
        self.setWindowIcon(icon)

        # Create progress bars
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(int(self.width/2 - self.width*9/20), self.height - 50, int(self.width*9/10), 20)

        self.progress_bar_quiz = QProgressBar(self)
        self.progress_bar_quiz.setGeometry(int(self.width/2 - self.width*9/20), self.height+40, int(self.width*9/10), 10)
        self.progress_bar_quiz.hide()

        # Start image loading process in a separate thread
        self.image_loader = ImageLoader(self.quizmaster, self.zoom_levels)
        self.image_loader.progress_updated.connect(self.update_progress)
        self.image_loader.images_loaded.connect(self.handle_images_loaded)
        self.image_loader.bottom_right_loaded.connect(self.handle_bottom_right_loaded)
        self.image_loader.top_left_loaded.connect(self.handle_top_left_loaded)
        self.image_loader.start()

        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width, self.height - (50 if self.easy_mode else 0))
        self.background_label.setAlignment(Qt.AlignCenter)

        # Create QLabel for displaying the image
        self.logo = QLabel(self)
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setGeometry(0, 0, self.width, self.height)

        # Load the image
        image_path = "resources/logo/osm_logo.png"  # Replace with the actual path to your image
        pixmap = QPixmap(image_path)
        self.logo.setPixmap(pixmap.scaledToWidth(self.width//2))


    def getNewStreet(self):
        self.hint = ""
        self.progress_bar_quiz.setValue(int(len(self.quizmaster.guessed_streets)/len(self.quizmaster.waysByName)*100.))
        self.quizmaster.pollNewStreet()
        self.drawGeometry()
        if self.easy_mode:
            current_street = self.quizmaster.current_street
            used = set()
            used.add(current_street)
            def_len = len(self.defaults)
            random_street = current_street
            for i in range(4):
                while random_street in used:
                    random_street = self.defaults[random.randint(0, def_len-1)]
                used.add(random_street)
                self.mcButtons[i].setText(random_street)
            j = random.randint(0, 3)
            self.mcButtons[j].setText(current_street)
            for button in self.mcButtons:
                button.setFocusPolicy(Qt.TabFocus)

    def plus_one(self):
        self.plus(2.)
    def plus(self, amount = 2.):
        self.offset_x = round(self.offset_x/amount)
        self.offset_y = round(self.offset_y/amount)
        self.scale *= amount
        self.drawGeometry()

    def minus_one(self):
        self.minus(2.)

    def minus(self, amount = 2.):
        self.offset_x = round(amount*self.offset_x)
        self.offset_y = round(amount*self.offset_y)
        self.scale /= amount
        self.drawGeometry()

    def print_text(self):
        text = self.text_box.text()
        if (self.quizmaster.guess(text, self.hint)):
            self.clear_text_box() # Clear the text box after printing the text
            self.getNewStreet()
        else:
            length = len(self.hint)
            currentStreet = self.quizmaster.current_street
            if (length<len(currentStreet)):
                self.hint += currentStreet[length]
                self.text_box.setText(self.hint)

    def create_text_box(self):
        completer = QCompleter(self.defaults)
        completer.activated.connect(self.clear_text_box)
        completer.setCompletionMode(QCompleter.PopupCompletion)

        # Create a text box
        self.text_box = MyLineEdit(self, completer)
        self.text_box.setGeometry(int(self.width / 20), self.height + 10, int(self.width * 9 / 10), 25)
        self.text_box.setCompleter(completer)

        # Connect returnPressed signal to print_text method
        self.text_box.returnPressed.connect(self.print_text)
        self.text_box.show()

    def create_multiple_choice(self):

        mcButton1 = QPushButton(self)
        font = mcButton1.font()
        font.setPixelSize(self.width / 80 )
        mcButton1.setFont(font)
        mcButton1.setGeometry(int(self.width * 1/32), self.height - 50, int(self.width * 3 / 16), 90)
        mcButton1.clicked.connect(self.click_1)

        mcButton2 = QPushButton(self)
        mcButton2.setFont(font)
        mcButton2.setGeometry(int(self.width * 9/32), self.height  - 50, int(self.width * 3 / 16), 90)
        mcButton2.clicked.connect(self.click_2)

        mcButton3 = QPushButton(self)
        mcButton3.setFont(font)
        mcButton3.setGeometry(int(self.width * 17/32), self.height  - 50 , int(self.width * 3 / 16), 90)
        mcButton3.clicked.connect(self.click_3)

        mcButton4 = QPushButton(self)
        mcButton4.setFont(font)
        mcButton4.setGeometry(int(self.width * 25/32), self.height  - 50 , int(self.width * 3 / 16), 90)
        mcButton4.clicked.connect(self.click_4)
        self.mcButtons = [mcButton1, mcButton2, mcButton3, mcButton4]
        for button in self.mcButtons:
            button.show()

        #self.mc_layout.setGeometry(int(self.width / 20), self.height - 65, int(self.width * 9 / 10), 100)
        #self.mc_layout.show()

    def click_1(self):
        self.handle_mc_click(0)
    def click_2(self):
        self.handle_mc_click(1)
    def click_3(self):
        self.handle_mc_click(2)
    def click_4(self):
        self.handle_mc_click(3)

    def handle_mc_click(self, index):
        text = self.mcButtons[index].text()
        if (self.quizmaster.guess(text, self.hint)):
            self.getNewStreet()
            for button in self.mcButtons:
                print(button.styleSheet())
                button.setEnabled(True)
        else:
            self.mcButtons[index].setEnabled(False)
            length = len(self.hint)
            currentStreet = self.quizmaster.current_street
            if (length<len(currentStreet)):
                self.hint += currentStreet[length]


    def clear_text_box(self):
        QTimer.singleShot(0, self.text_box.clear)

    def drawGeometry(self):
        streetGeometry = self.quizmaster.getGeometry()
        if streetGeometry == None:
            streetGeometry = self.oldGeometry
        else:
            self.oldGeometry = streetGeometry
        guessedGeometriesWithHints, guessedGeometriesWithHint, guessedGeometries = self.quizmaster.getGuessedGeometries()
        rescaled_bbox = self.getRescaledBbox(streetGeometry)

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

        self.drawGeometryCollection(painter, rescaled_bbox, streetGeometry,  QColor(255, 0, 0))
        self.drawGeometryCollection(painter, rescaled_bbox, guessedGeometries, QColor(0, 150, 0))
        self.drawGeometryCollection(painter, rescaled_bbox, guessedGeometriesWithHint, QColor(194, 245, 66))
        self.drawGeometryCollection(painter, rescaled_bbox, guessedGeometriesWithHints, QColor(245, 230, 66))
        painter.end()
        self.background_label.setPixmap(pixmap)

    def drawGeometryCollection(self, painter, rescaled_bbox, geometry, qColor):
        # Convert coordinates to pixel coordinates
        pixels = []
        for geom in geometry.geoms:
            pixel_coords = []
            for coord in geom.coords[:]:
                pixel_coords.append(
                    coordToPixel(coord[1], coord[0], rescaled_bbox, self.width, self.height, self.offset_x,
                                 self.offset_y))
            pixels.append(pixel_coords)
        # Draw lines on the QLabel
        pen = QPen(qColor)  # Red color for the lines
        pen.setWidth(3)  # Set pen width
        painter.setPen(pen)
        for line in pixels:
            if len(line) > 1:
                for i in range(len(line) - 1):
                    x1, y1 = line[i]
                    x2, y2 = line[i + 1]
                    painter.drawLine(x1, y1, x2, y2)

    def getRescaledBbox(self, geometry):
        height = 0.001 * self.scale
        width = 0.001 * self.scale
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
        try:
            self.progress_bar.isHidden()
            return
        except:
            pass
        if event.button() == Qt.LeftButton or  event.button() == Qt.RightButton:
            self.dragging = True
            self.start_pos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        try:
            self.progress_bar.isHidden()
            return
        except:
            pass
        if self.dragging:
            delta = event.pos() - self.start_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.start_pos = event.pos()
            self.drawGeometry()

    def mouseReleaseEvent(self, event: QMouseEvent):
        try:
            self.progress_bar.isHidden()
            return
        except:
            pass
        if event.button() == Qt.LeftButton or  event.button() == Qt.RightButton:
            self.dragging = False

    def wheelEvent(self, event):
        try:
            self.progress_bar.isHidden()
            return
        except:
            pass

        delta = event.angleDelta().y() / 120.  # Get the scroll value
        if(delta>0.):
            self.minus(1+delta)
        elif(delta<0.):
            self.plus(1-delta)

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def handle_top_left_loaded(self, backgroundTopLeft):
        self.backgroundTopLeft = backgroundTopLeft
        # Handle the loaded images

    def handle_bottom_right_loaded(self, backgroundBottomRight):
        self.backgroundBottomRight = backgroundBottomRight
        # Handle the loaded images

    def handle_images_loaded(self, background_images):
        self.background_images = background_images
        # Handle the loaded images
        self.progress_bar.deleteLater()   # Remove progress bar after loading is complete
        self.logo.deleteLater()
        if self.easy_mode:
            self.create_multiple_choice()
        else:
            self.create_text_box()
        self.getNewStreet()
        self.progress_bar_quiz.show()

    def keyPressEvent(self, event, **kwargs):
        if event.key() == Qt.Key_Escape:
            exit(0)


