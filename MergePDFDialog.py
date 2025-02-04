from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QSpinBox, QComboBox, QHBoxLayout, QFileDialog, QListWidget, QAbstractItemView, QLineEdit, QListWidgetItem
from PyQt5.QtCore import Qt

class MergePDFDialog(QDialog):
    def __init__(self, parent=None, file_names=None):
        super().__init__(parent)
        self.setWindowTitle("Sloučit PDF - Pořadí souborů")
        self.file_names = file_names
        self.layout = QVBoxLayout()

        self.file_list = QListWidget()
        self.file_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.file_list.setSelectionMode(QAbstractItemView.SingleSelection)  # only one item selected
        for name in file_names:
            item = QListWidgetItem(name)
            self.file_list.addItem(item)
        self.layout.addWidget(self.file_list)

        self.path_layout = QHBoxLayout()
        self.path_label = QLabel("Výstupní cesta:", self)
        self.path_input = QLineEdit(self)
        self.path_button = QPushButton("Procházet", self)
        self.path_button.clicked.connect(self.select_output_path)

        self.path_layout.addWidget(self.path_label)
        self.path_layout.addWidget(self.path_input)
        self.path_layout.addWidget(self.path_button)
        self.layout.addLayout(self.path_layout)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("Zrušit", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)
        self.output_path = None

    def select_output_path(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Uložit sloučené PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.output_path = file_path
            self.path_input.setText(file_path)

    def get_file_order(self):
        return [self.file_list.item(i).text() for i in range(self.file_list.count())]

    def get_output_path(self):
        return self.output_path