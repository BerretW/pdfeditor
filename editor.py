import sys
import os
import json
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QLineEdit, QFileDialog,
    QMessageBox, QDialog, QSpinBox, QScrollArea,
    QGridLayout, QFrame, QCheckBox, QComboBox, QTextEdit, QAbstractItemView,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QPoint, QMimeData
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont, QDrag
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import fitz
from ImageCropDialog import ImageCropDialog

from BulkRenameDialog import BulkRenameDialog

from InsertPagesDialog import InsertPagesDialog

# --- Klikací label (pro náhledy) ---
class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)



# --- Widget pro zobrazení stránky (bez drag & drop) ---
class PageThumbnail(QFrame):
    def __init__(self, page_number, pixmap, parent_window, parent=None):
        super().__init__(parent)
        self.page_number = page_number  # 1-indexované číslo stránky
        self.parent_window = parent_window
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        layout = QVBoxLayout(self)
        self.checkbox = QCheckBox(f"Strana {page_number}", self)
        layout.addWidget(self.checkbox)
        self.label = ClickableLabel(self)
        self.label.setPixmap(pixmap)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.label.clicked.connect(lambda: self.parent_window.open_large_preview_with_edit(self.page_number))
    # Odstranili jsme drag & drop metody

# --- Dialog pro vytvoření nového PDF ---
class NewPDFDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vytvořit nové PDF")
        layout = QVBoxLayout(self)
        self.label = QLabel("Zadejte počet prázdných stránek:", self)
        layout.addWidget(self.label)
        self.spin_pages = QSpinBox(self)
        self.spin_pages.setMinimum(1)
        self.spin_pages.setValue(1)
        layout.addWidget(self.spin_pages)
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Vytvořit", self)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        cancel_button = QPushButton("Zrušit", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def getPageCount(self):
        return self.spin_pages.value()

# --- Hlavní okno ---
class PDFManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Editor")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon("icon.png"))
        self.database_file = os.path.abspath("pdf_data.json")
        self.database = {}
        self.load_database()
        self.selected_pdf = None
        self.floating_preview = None  # plovoucí okno s náhledem první stránky
        self.page_order = []  # aktuální pořadí stran (1-indexováno)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Horní lišta – přidáno tlačítko Nové PDF
        top_layout = QHBoxLayout()
        self.new_pdf_button = QPushButton("Nové PDF", self)
        self.new_pdf_button.clicked.connect(self.create_new_pdf)
        top_layout.addWidget(self.new_pdf_button)

        self.add_button = QPushButton("Přidat PDF", self)
        self.add_button.clicked.connect(self.add_pdf)
        top_layout.addWidget(self.add_button)

        self.add_bulk_button = QPushButton("Přidat více PDF", self)
        self.add_bulk_button.clicked.connect(self.add_bulk_pdfs)
        top_layout.addWidget(self.add_bulk_button)

        self.remove_button = QPushButton("Odebrat PDF", self)
        self.remove_button.clicked.connect(self.remove_selected_pdfs)
        top_layout.addWidget(self.remove_button)

        self.rename_button = QPushButton("Hromadné přejmenování", self)
        self.rename_button.clicked.connect(self.bulk_rename_dialog)
        top_layout.addWidget(self.rename_button)

        # Přidáno tlačítko pro sloučení PDF souborů
        self.merge_button = QPushButton("Sloučit PDF", self)
        self.merge_button.clicked.connect(self.merge_pdfs)
        top_layout.addWidget(self.merge_button)

        top_layout.addWidget(QLabel("Velikost náhledu:", self))
        self.size_combo = QComboBox(self)
        self.size_combo.addItem("Malý", 100)
        self.size_combo.addItem("Střední", 200)
        self.size_combo.addItem("Velký", 300)
        self.size_combo.currentIndexChanged.connect(self.reload_thumbnails)
        top_layout.addWidget(self.size_combo)
        main_layout.addLayout(top_layout)

        # Seznam PDF
        self.pdf_list = QListWidget(self)
        self.pdf_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.pdf_list.itemClicked.connect(self.show_pdf_details)
        self.pdf_list.viewport().setMouseTracking(True)
        self.pdf_list.viewport().installEventFilter(self)
        main_layout.addWidget(self.pdf_list)

        # Hlavní oblast
        main_area_layout = QHBoxLayout()
        self.pages_scroll_area = QScrollArea(self)
        self.pages_scroll_area.setWidgetResizable(True)
        self.pages_widget = QWidget()
        self.pages_layout = QGridLayout(self.pages_widget)
        self.pages_scroll_area.setWidget(self.pages_widget)
        main_area_layout.addWidget(self.pages_scroll_area, 3)

        # Panel akcí
        action_layout = QVBoxLayout()
        self.detail_label = QLabel("Vyberte PDF ze seznamu", self)
        action_layout.addWidget(self.detail_label)
        self.page_detail_label = QLabel("", self)
        action_layout.addWidget(self.page_detail_label)
        self.delete_pages_button = QPushButton("Odebrat vybrané stránky", self)
        self.delete_pages_button.clicked.connect(self.delete_selected_pages)
        action_layout.addWidget(self.delete_pages_button)
        self.apply_deletions_button = QPushButton("Aplikovat odstranění stran", self)
        self.apply_deletions_button.clicked.connect(self.apply_deleted_pages)
        action_layout.addWidget(self.apply_deletions_button)
        self.insert_pages_button = QPushButton("Vložit stránky", self)
        self.insert_pages_button.clicked.connect(self.insert_pages_dialog)
        action_layout.addWidget(self.insert_pages_button)
        # Uložit automaticky přepíše původní soubor
        self.save_button = QPushButton("Uložit (auto overwrite)", self)
        self.save_button.clicked.connect(self.auto_save_pdf)
        action_layout.addWidget(self.save_button)
        main_area_layout.addLayout(action_layout, 1)
        main_layout.addLayout(main_area_layout)
        central_widget.setLayout(main_layout)
        self.update_pdf_list()
    
    def merge_pdfs(self):
        selected_items = self.pdf_list.selectedItems()
        if len(selected_items) < 2:
            QMessageBox.warning(self, "Varování", "Vyberte alespoň dva PDF soubory pro sloučení.")
            return

        file_paths = [self.database[item.text()]["path"] for item in selected_items]
        output_path, _ = QFileDialog.getSaveFileName(self, "Uložit sloučené PDF", "", "PDF Files (*.pdf)")

        if output_path:
            try:
                pdf_writer = PyPDF2.PdfWriter()
                for file_path in file_paths:
                    with open(file_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page in pdf_reader.pages:
                            pdf_writer.add_page(page)

                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                
                # Add the merged PDF to the database
                file_name = os.path.basename(output_path)
                self.database[file_name] = {
                    "path": os.path.abspath(output_path),
                    "num_pages": len(pdf_writer.pages),
                    "deleted_pages": [],
                    "inserted_pages": []
                }
                self.save_database()
                self.update_pdf_list()

                QMessageBox.information(self, "Úspěch", f"Soubory byly sloučeny do:\n{output_path}")
            except Exception as e:
                QMessageBox.critical(self, "Chyba", f"Chyba při slučování PDF souborů: {e}")


    # --- Vytvoření nového PDF ---
    def create_new_pdf(self):
        dialog = NewPDFDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            page_count = dialog.getPageCount()
            tmp_path = os.path.join(tempfile.gettempdir(), "new_pdf.pdf")
            c = canvas.Canvas(tmp_path, pagesize=A4)
            for _ in range(page_count):
                c.showPage()
            c.save()
            save_path, _ = QFileDialog.getSaveFileName(self, "Uložit nové PDF", "", "PDF Files (*.pdf)")
            if save_path:
                os.rename(tmp_path, save_path)
                try:
                    with open(save_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        num_pages = len(pdf_reader.pages)
                    file_name = os.path.basename(save_path)
                    self.database[file_name] = {
                        "path": os.path.abspath(save_path),
                        "num_pages": num_pages,
                        "deleted_pages": [],
                        "inserted_pages": []
                    }
                    self.save_database()
                    self.update_pdf_list()
                    QMessageBox.information(self, "Nové PDF", f"Nové PDF {file_name} bylo vytvořeno a přidáno do databáze.")
                except Exception as e:
                    QMessageBox.critical(self, "Chyba", f"Chyba při přidávání nového PDF: {e}")
            else:
                os.unlink(tmp_path)

    # --- Funkce pro hromadné přidání PDF souborů ---
    def add_bulk_pdfs(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Vyberte PDF soubory", "", "PDF Files (*.pdf)")
        if not file_paths:
            return
        added = 0
        for file_path in file_paths:
            try:
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)
                file_name = os.path.basename(file_path)
                if file_name not in self.database:
                    self.database[file_name] = {
                        "path": os.path.abspath(file_path),
                        "num_pages": num_pages,
                        "deleted_pages": [],
                        "inserted_pages": []
                    }
                    added += 1
            except Exception as e:
                QMessageBox.critical(self, "Chyba", f"Chyba při přidávání {file_path}: {e}")
        self.save_database()
        self.update_pdf_list()
        QMessageBox.information(self, "PDF Přidáno", f"Přidáno bylo {added} souborů.")

    # --- Event filter pro plovoucí náhled ---
    def eventFilter(self, obj, event):
        if obj == self.pdf_list.viewport():
            if event.type() == QEvent.MouseMove:
                pos = event.pos()
                item = self.pdf_list.itemAt(pos)
                if item:
                    global_pos = self.pdf_list.viewport().mapToGlobal(pos)
                    self.show_floating_preview(item, global_pos)
                else:
                    if self.floating_preview:
                        self.floating_preview.hide()
            elif event.type() == QEvent.Leave:
                if self.floating_preview:
                    self.floating_preview.hide()
        return super().eventFilter(obj, event)

    def show_floating_preview(self, item, global_pos):
        file_name = item.text()
        if file_name not in self.database:
            return
        preview = self.get_first_page_preview(file_name)
        if preview is None:
            return
        if self.floating_preview is None:
            self.floating_preview = QDialog(self, Qt.ToolTip)
            self.floating_preview.setWindowFlags(Qt.ToolTip)
            layout = QVBoxLayout()
            self.floating_label = QLabel()
            layout.addWidget(self.floating_label)
            self.floating_preview.setLayout(layout)
        self.floating_label.setPixmap(preview)
        self.floating_preview.move(global_pos + QPoint(20, 20))
        self.floating_preview.show()

    def get_first_page_preview(self, file_name):
        try:
            pdf_path = self.database[file_name]["path"]
            ext = os.path.splitext(pdf_path)[1].lower()
            if ext == ".png":
                img = QImage()
                if img.load(pdf_path):
                    if img.hasAlphaChannel():
                        img = img.convertToFormat(QImage.Format_ARGB32)
                    return QPixmap.fromImage(img).scaled(300, 300, Qt.KeepAspectRatio)
                else:
                    return None
            else:
                doc = fitz.open(pdf_path)
                if len(doc) == 0:
                    doc.close()
                    return None
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
                fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
                image = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
                pixmap = QPixmap.fromImage(image).scaled(300, 300, Qt.KeepAspectRatio)
                doc.close()
                return pixmap
        except Exception as e:
            print(f"Chyba při načítání prvního náhledu: {e}")
            return None

    def load_database(self):
        try:
            with open(self.database_file, 'r') as f:
                self.database = json.load(f)
        except FileNotFoundError:
            self.database = {}

    def save_database(self):
        with open(self.database_file, 'w') as f:
            json.dump(self.database, f)

    def add_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Vyberte PDF soubor", "", "PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            try:
                ext = os.path.splitext(file_path)[1].lower()
                if ext == ".png":
                    # Pokud je PNG, nejprve otevřeme editor obrázků pro oříznutí
                    pixmap = QPixmap(file_path)
                    crop_dialog = ImageCropDialog(pixmap, self)
                    if crop_dialog.exec_() == QDialog.Accepted:
                        cropped = crop_dialog.getCroppedPixmap()
                        # Uložíme oříznutý obrázek do dočasného souboru
                        temp_img_path = os.path.join(tempfile.gettempdir(), "cropped.png")
                        cropped.save(temp_img_path, "PNG")
                        # Vytvoříme PDF stránku z oříznutého obrázku pomocí ReportLabu
                        new_pdf_path = os.path.join(tempfile.gettempdir(), "converted.png.pdf")
                        c = canvas.Canvas(new_pdf_path, pagesize=A4)
                        c.drawImage(temp_img_path, 0, 0, A4[0], A4[1], mask='auto')
                        c.save()
                        file_path = new_pdf_path
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)
                file_name = os.path.basename(file_path)
                self.database[file_name] = {
                    "path": os.path.abspath(file_path),
                    "num_pages": num_pages,
                    "deleted_pages": [],
                    "inserted_pages": []
                }
                self.save_database()
                self.update_pdf_list()
                QMessageBox.information(self, "PDF Přidáno", f"Soubor {file_name} byl přidán do databáze.")
            except Exception as e:
                QMessageBox.critical(self, "Chyba", f"Chyba při přidávání souboru: {e}")

    def remove_selected_pdfs(self):
        selected_items = self.pdf_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Varování", "Nevybrali jste žádné PDF k odebrání.")
            return
        reply = QMessageBox.question(self, "Potvrdit", f"Odebrat {len(selected_items)} vybraných souborů?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            for item in selected_items:
                file_name = item.text()
                if file_name in self.database:
                    del self.database[file_name]
            self.save_database()
            self.update_pdf_list()
            self.detail_label.setText("Vyberte PDF ze seznamu")
            self.page_detail_label.setText("")
            self.clear_page_thumbnails()

    def update_pdf_list(self):
        self.pdf_list.clear()
        for file_name in self.database:
            self.pdf_list.addItem(file_name)

    def show_pdf_details(self, item):
        self.clear_page_thumbnails()
        file_name = item.text()
        self.selected_pdf = file_name
        pdf_data = self.database[file_name]
        self.detail_label.setText(f"Název: {file_name}")
        self.page_detail_label.setText(f"Počet stran: {pdf_data['num_pages']}")
        self.page_order = list(range(1, pdf_data['num_pages'] + 1))
        self.load_pdf_thumbnails(file_name)

    def load_pdf_thumbnails(self, file_name):
        try:
            pdf_path = self.database[file_name]["path"]
            doc = fitz.open(pdf_path)
            preview_size = self.size_combo.currentData()
            for idx, page_num in enumerate(self.page_order):
                page = doc[page_num - 1]
                pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
                fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
                image = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
                full_pixmap = QPixmap.fromImage(image)
                thumb_pixmap = full_pixmap.scaled(preview_size, preview_size, Qt.KeepAspectRatio)
                thumbnail = PageThumbnail(page_num, thumb_pixmap, self, self)
                row = idx // 4
                col = idx % 4
                self.pages_layout.addWidget(thumbnail, row, col)
            doc.close()
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Chyba při načítání náhledů: {e}")

    def clear_page_thumbnails(self):
        while self.pages_layout.count():
            item = self.pages_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def reload_thumbnails(self):
        if self.selected_pdf:
            self.show_pdf_details(self.pdf_list.currentItem())

    def handle_page_reorder(self, source_page, target_page):
        try:
            src_index = self.page_order.index(source_page)
            tgt_index = self.page_order.index(target_page)
            self.page_order[src_index], self.page_order[tgt_index] = self.page_order[tgt_index], self.page_order[src_index]
            self.reload_thumbnails()
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Chyba při přesouvání stránek: {e}")

    def open_large_preview_with_edit(self, page_number):
        try:
            pdf_path = self.database[self.selected_pdf]["path"]
            doc = fitz.open(pdf_path)
            page = doc[page_number - 1]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            pixmap = QPixmap.fromImage(image)
            doc.close()
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Strana {page_number}")
            dlg_layout = QVBoxLayout()
            label = QLabel()
            label.setPixmap(pixmap)
            dlg_layout.addWidget(label)
            edit_button = QPushButton("Editovat stránku", dialog)
            edit_button.clicked.connect(lambda: self.edit_page_text(page_number, dialog))
            dlg_layout.addWidget(edit_button)
            close_button = QPushButton("Zavřít", dialog)
            close_button.clicked.connect(dialog.accept)
            dlg_layout.addWidget(close_button)
            dialog.setLayout(dlg_layout)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Chyba při otevírání velkého náhledu: {e}")

    def edit_page_text(self, page_number, parent_dialog):
        if not self.selected_pdf:
            QMessageBox.warning(self, "Varování", "Vyberte PDF soubor.")
            return
        try:
            pdf_path = self.database[self.selected_pdf]["path"]
            pdf_reader = PyPDF2.PdfReader(pdf_path)
            page = pdf_reader.pages[page_number - 1]
            initial_text = page.extract_text() or ""
        except Exception as e:
            initial_text = ""
            QMessageBox.warning(self, "Chyba", f"Chyba při načítání textu: {e}")
       

    def replace_page_in_pdf(self, file_name, page_number, new_text):
        try:
            original_path = self.database[file_name]["path"]
            pdf_reader = PyPDF2.PdfReader(original_path)
            pdf_writer = PyPDF2.PdfWriter()
            tmp_path = os.path.join(tempfile.gettempdir(), "edited_page.pdf")
            c = canvas.Canvas(tmp_path, pagesize=A4)
            lines = new_text.splitlines()
            x, y = 50, A4[1] - 50
            for line in lines:
                c.drawString(x, y, line)
                y -= 15
            c.save()
            new_page_reader = PyPDF2.PdfReader(open(tmp_path, "rb"))
            if len(new_page_reader.pages) < 1:
                raise Exception("Nově vygenerovaná stránka není dostupná.")
            for i, pg in enumerate(pdf_reader.pages):
                if self.page_order[i] == page_number:
                    pdf_writer.add_page(new_page_reader.pages[0])
                else:
                    pdf_writer.add_page(pg)
            output_path = original_path  # přepíšeme původní soubor
            with open(output_path, "wb") as f_out:
                pdf_writer.write(f_out)
            os.unlink(tmp_path)
            self.database[file_name]["path"] = os.path.abspath(output_path)
            self.database[file_name]["num_pages"] = len(pdf_writer.pages)
            self.save_database()
            QMessageBox.information(self, "Úspěch", "Stránka byla upravena a soubor byl přepsán.")
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Chyba při úpravě stránky: {e}")

    def delete_selected_pages(self):
        if not self.selected_pdf:
            QMessageBox.warning(self, "Varování", "Vyberte PDF soubor.")
            return
        pages_to_delete = []
        for i in range(self.pages_layout.count()):
            widget = self.pages_layout.itemAt(i).widget()
            if widget and hasattr(widget, "checkbox"):
                if widget.checkbox.isChecked():
                    pages_to_delete.append(widget.page_number)
        if not pages_to_delete:
            QMessageBox.information(self, "Informace", "Nevybral jste žádné stránky k odebrání.")
            return
        reply = QMessageBox.question(self, "Potvrdit", f"Opravdu chcete odebrat stránky {pages_to_delete}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.database[self.selected_pdf]["deleted_pages"] = pages_to_delete
            self.save_database()
            QMessageBox.information(self, "Úspěch", "Stránky byly označeny k odebrání. Pro aplikaci změn stiskněte 'Aplikovat odstranění stran'.")
    
    def apply_deleted_pages(self):
        if not self.selected_pdf:
            QMessageBox.warning(self, "Varování", "Vyberte PDF soubor.")
            return
        deleted_pages = self.database[self.selected_pdf].get("deleted_pages", [])
        if not deleted_pages:
            QMessageBox.information(self, "Informace", "Nebyly označeny žádné stránky k odstranění.")
            return
        reply = QMessageBox.question(self, "Potvrdit", f"Odebrat stránky {deleted_pages} z PDF?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            pdf_path = self.database[self.selected_pdf]["path"]
            pdf_reader = PyPDF2.PdfReader(pdf_path)
            pdf_writer = PyPDF2.PdfWriter()
            for i, page in enumerate(pdf_reader.pages):
                if (i + 1) not in deleted_pages:
                    pdf_writer.add_page(page)
            output_path = pdf_path  # přepíšeme původní soubor
            with open(output_path, "wb") as f_out:
                pdf_writer.write(f_out)
            self.database[self.selected_pdf]["path"] = os.path.abspath(output_path)
            self.database[self.selected_pdf]["num_pages"] = len(pdf_writer.pages)
            self.database[self.selected_pdf]["deleted_pages"] = []
            self.save_database()
            QMessageBox.information(self, "Úspěch", "Změny byly aplikovány a soubor byl přepsán.")
            self.show_pdf_details(self.pdf_list.currentItem())
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Chyba při aplikaci odebraných stran: {e}")

    def insert_pages_dialog(self):
        if not self.selected_pdf:
            QMessageBox.warning(self, "Varování", "Vyberte PDF soubor.")
            return
        dialog = InsertPagesDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_pages_path, page_number_to_insert_before, insert_type = dialog.get_insert_params()
            if new_pages_path:
                self.insert_pages(self.selected_pdf, new_pages_path, page_number_to_insert_before, insert_type)
                self.show_pdf_details(self.pdf_list.currentItem())
            else:
                QMessageBox.warning(self, "Varování", "Nevybrali jste soubor ke vložení.")

    def insert_pages(self, file_name, new_pages_path, page_number_to_insert_before, insert_type):
        if file_name in self.database:
            try:
                pdf_path = self.database[file_name]["path"]
                if insert_type == "pdf":
                    with open(pdf_path, 'rb') as main_pdf_file, open(new_pages_path, 'rb') as new_pages_pdf_file:
                        pdf_reader_main = PyPDF2.PdfReader(main_pdf_file)
                        pdf_reader_insert = PyPDF2.PdfReader(new_pages_pdf_file)
                        pdf_writer = PyPDF2.PdfWriter()
                        for i, page in enumerate(pdf_reader_main.pages):
                            if i == page_number_to_insert_before - 1:
                                for insert_page in pdf_reader_insert.pages:
                                    pdf_writer.add_page(insert_page)
                            pdf_writer.add_page(page)
                        if page_number_to_insert_before > len(pdf_reader_main.pages):
                            for insert_page in pdf_reader_insert.pages:
                                pdf_writer.add_page(insert_page)
                    output_path = pdf_path  # přepíšeme původní soubor
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                    self.database[file_name]["path"] = os.path.abspath(output_path)
                    self.database[file_name]["num_pages"] = len(pdf_writer.pages)
                    self.database[file_name]["inserted_pages"].extend(
                        list(range(len(pdf_reader_main.pages) + 1, len(pdf_writer.pages) + 1))
                    )
                    self.save_database()
                elif insert_type == "image":
                    # Načteme obrázek pomocí QPixmap (pro podporu průhlednosti)
                    pixmap = QPixmap(new_pages_path)
                    # Otevřeme editor obrázků pro oříznutí
                    crop_dialog = ImageCropDialog(pixmap, self)
                    if crop_dialog.exec_() == QDialog.Accepted:
                        cropped = crop_dialog.getCroppedPixmap()
                        # Uložíme oříznutý obrázek do dočasného souboru
                        temp_img_path = os.path.join(tempfile.gettempdir(), "cropped.png")
                        cropped.save(temp_img_path, "PNG")
                        # Vytvoříme PDF stránku z oříznutého obrázku
                        page_size = A4
                        fd, tmp_pdf_path = tempfile.mkstemp(suffix=".pdf")
                        os.close(fd)
                        c = canvas.Canvas(tmp_pdf_path, pagesize=A4)
                        c.drawImage(temp_img_path, 0, 0, page_size[0], page_size[1], mask='auto')
                        c.save()
                        # Zavoláme rekurzivně insert_pages s novým PDF a typem "pdf"
                        self.insert_pages(file_name, tmp_pdf_path, page_number_to_insert_before, "pdf")
                        os.unlink(temp_img_path)
                        os.unlink(tmp_pdf_path)
                QMessageBox.information(self, "Úspěch", "Stránky byly vloženy a soubor byl přepsán.")
            except Exception as e:
                QMessageBox.critical(self, "Chyba", f"Chyba při vkládání stránek: {e}")
        else:
            QMessageBox.warning(self, "Chyba", "PDF soubor nebyl nalezen v databázi")

    def auto_save_pdf(self):
        if not self.selected_pdf:
            QMessageBox.warning(self, "Varování", "Vyberte PDF soubor.")
            return
        try:
            pdf_path = self.database[self.selected_pdf]["path"]
            pdf_reader = PyPDF2.PdfReader(pdf_path)
            pdf_writer = PyPDF2.PdfWriter()
            deleted_pages = self.database[self.selected_pdf].get("deleted_pages", [])
            for i, page in enumerate(pdf_reader.pages):
                if (i + 1) not in deleted_pages:
                    pdf_writer.add_page(page)
            with open(pdf_path, 'wb') as f_out:
                pdf_writer.write(f_out)
            QMessageBox.information(self, "Úspěch", f"PDF bylo uloženo do původního souboru:\n{pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Chyba", f"Chyba při automatickém ukládání PDF: {e}")

    def save_edited_pdf(self):
        self.auto_save_pdf()

    def bulk_rename_dialog(self):
        dialog = BulkRenameDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            pattern, new_pattern = dialog.get_rename_params()
            self.bulk_rename_files(pattern, new_pattern)
            self.update_pdf_list()

    def bulk_rename_files(self, pattern, new_pattern):
        for file_name, file_data in list(self.database.items()):
            new_file_name = file_name.replace(pattern, new_pattern)
            if new_file_name != file_name:
                new_path = os.path.join(os.path.dirname(file_data["path"]), new_file_name)
                try:
                    os.rename(file_data["path"], new_path)
                    self.database[new_file_name] = self.database.pop(file_name)
                    self.database[new_file_name]["path"] = os.path.abspath(new_path)
                except FileNotFoundError:
                    QMessageBox.warning(self, "Chyba", f"Soubor {file_name} k přejmenování nebyl nalezen")
                except Exception as e:
                    QMessageBox.critical(self, "Chyba", f"Chyba při přejmenování {file_name}: {e}")
        self.save_database()
        QMessageBox.information(self, "Úspěch", "Soubory byly přejmenovány")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFManagerWindow()
    window.show()
    sys.exit(app.exec_())