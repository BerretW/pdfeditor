# --- Dialog pro hromadné přejmenování ---
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton

class BulkRenameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hromadné přejmenování")
        self.layout = QVBoxLayout()
        self.label_pattern = QLabel("Vzor:", self)
        self.input_pattern = QLineEdit(self)
        self.layout.addWidget(self.label_pattern)
        self.layout.addWidget(self.input_pattern)
        self.label_new_pattern = QLabel("Nový vzor:", self)
        self.input_new_pattern = QLineEdit(self)
        self.layout.addWidget(self.label_new_pattern)
        self.layout.addWidget(self.input_new_pattern)
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("Zrušit", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def get_rename_params(self):
        return self.input_pattern.text(), self.input_new_pattern.text()