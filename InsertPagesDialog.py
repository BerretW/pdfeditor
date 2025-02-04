# --- Dialog pro vkládání stránek ---
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QSpinBox, QComboBox, QHBoxLayout, QFileDialog
import os
class InsertPagesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vložit stránky")
        self.layout = QVBoxLayout()
        self.file_button = QPushButton("Vyberte PDF nebo obrázek", self)
        self.file_button.clicked.connect(self.select_file)
        self.file_path = None
        self.layout.addWidget(self.file_button)
        self.page_number_label = QLabel("Zadejte číslo stránky před kterou chcete vložit:", self)
        self.page_number_input = QSpinBox(self)
        self.page_number_input.setMinimum(1)
        self.page_number_input.setMaximum(9999)  # Nastavíme maximum na 9999
        self.layout.addWidget(self.page_number_label)
        self.layout.addWidget(self.page_number_input)
        self.insert_type_label = QLabel("Typ vkládaného souboru:", self)
        self.insert_type_combo = QComboBox(self)
        self.insert_type_combo.addItem("pdf")
        self.insert_type_combo.addItem("image")
        self.layout.addWidget(self.insert_type_label)
        self.layout.addWidget(self.insert_type_combo)
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("Zrušit", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Vyberte PDF nebo obrázek", "", "PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.file_path = os.path.abspath(file_path)

    def get_insert_params(self):
        return self.file_path, self.page_number_input.value(), self.insert_type_combo.currentText()

