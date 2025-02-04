from PyQt5.QtWidgets import QGraphicsView, QGraphicsRectItem, QDialog, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import Qt, QRectF

class CropGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._origin = None
        self._rubberRectItem = QGraphicsRectItem()
        self._rubberRectItem.setPen(QPen(Qt.red, 2, Qt.DashLine))
        self._rubberRectItem.setBrush(QBrush(Qt.transparent))
        self._rubberRectItem.setZValue(10)  # ať je nahoře
        self._rubberRectItem.hide()

    def setScene(self, scene):
        super().setScene(scene)
        # Po přidání scény přidáme i náš obdélník
        self.scene().addItem(self._rubberRectItem)

    def mousePressEvent(self, event):
        # Začínáme vybírat
        if event.button() == Qt.LeftButton:
            self._origin = self.mapToScene(event.pos())
            self._rubberRectItem.setRect(QRectF(self._origin, self._origin))
            self._rubberRectItem.show()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Dynamicky zvětšujeme obdélník
        if self._origin is not None:
            current_pos = self.mapToScene(event.pos())
            rect = QRectF(self._origin, current_pos).normalized()
            self._rubberRectItem.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Výběr dokončen
        if event.button() == Qt.LeftButton:
            self._origin = None
        super().mouseReleaseEvent(event)

    def getSelectionRect(self):
        """Vrátí vybraný obdélník v souřadnicích scény."""
        if self._rubberRectItem.isVisible():
            return self._rubberRectItem.rect()
        return QRectF()


class ImageCropDialog(QDialog):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editor obrázků - Oříznutí")
        self.original_pixmap = pixmap
        self.cropped_pixmap = None
        self.initUI()

    def initUI(self):
        self.view = CropGraphicsView(self)  # <= místo QGraphicsView
        self.scene = QGraphicsScene(self)
        self.pixmap_item = QGraphicsPixmapItem(self.original_pixmap)
        self.scene.addItem(self.pixmap_item)
        self.view.setScene(self.scene)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.crop)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Zrušit", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.resize(800, 600)

    def crop(self):
        # Přes náš cropView si zjistíme vybraný obdélník
        scene_selection_rect = self.view.getSelectionRect()
        if scene_selection_rect.isEmpty():
            # žádný obdélník => použijeme celý obrázek
            self.cropped_pixmap = self.original_pixmap
        else:
            # souřadnice pixmapu na scéně
            imageRect = self.pixmap_item.sceneBoundingRect()
            scaleX = self.original_pixmap.width() / imageRect.width()
            scaleY = self.original_pixmap.height() / imageRect.height()

            offsetX = scene_selection_rect.left() - imageRect.left()
            offsetY = scene_selection_rect.top() - imageRect.top()

            x = int(offsetX * scaleX)
            y = int(offsetY * scaleY)
            w = int(scene_selection_rect.width() * scaleX)
            h = int(scene_selection_rect.height() * scaleY)

            # ořízneme v pixmapě
            self.cropped_pixmap = self.original_pixmap.copy(x, y, w, h)

        self.accept()

    def getCroppedPixmap(self):
        return self.cropped_pixmap
