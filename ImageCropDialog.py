from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QPushButton, QDialog,

    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)


class ImageCropDialog(QDialog):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editor obrázků - Oříznutí")
        self.original_pixmap = pixmap
        self.cropped_pixmap = None
        self.initUI()

    def initUI(self):
        # Použijeme QGraphicsView a QGraphicsScene
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.pixmap_item = QGraphicsPixmapItem(self.original_pixmap)
        self.scene.addItem(self.pixmap_item)
        self.view.setScene(self.scene)
        # Umožníme výběr pomocí rubber band (nativně podporováno)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
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
        # Získáme obdélník výběru (rubber band) v souřadnicích QGraphicsView
        rubberBandRect = self.view.rubberBandRect()
        if rubberBandRect.isNull():
            # Pokud není výběr, použijeme celý obrázek
            self.cropped_pixmap = self.original_pixmap
        else:
            scene_rect = self.view.mapToScene(rubberBandRect).boundingRect()
            self.cropped_pixmap = self.original_pixmap.copy(
                scene_rect.toRect())
        self.accept()

    def getCroppedPixmap(self):
        return self.cropped_pixmap
