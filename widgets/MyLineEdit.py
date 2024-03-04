from PyQt5.QtCore import pyqtSignal, QEvent, Qt
from PyQt5.QtWidgets import QLineEdit


class MyLineEdit(QLineEdit):
    tabPressed = pyqtSignal()

    def __init__(self, parent=None, completer=None):
        super().__init__(parent)
        self._compl = completer
        self.tabPressed.connect(self.next_completion)

    def next_completion(self):
        index = self._compl.currentIndex()
        self._compl.popup().setCurrentIndex(index)
        start = self._compl.currentRow()
        if not self._compl.setCurrentRow(start + 1):
            self._compl.setCurrentRow(0)

    def event(self, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            self.tabPressed.emit()
            return True
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            exit(0)
        return super().event(event)