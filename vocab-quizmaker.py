import sys
import csv
import random
import io
import os
import sys
import csv
import random
import io
import os
import platform  # <--- ADD THIS LINE

# --- PyQt6 UI and Utility Imports ---
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QVBoxLayout, QFileDialog, QMessageBox,
                             QLineEdit, QCheckBox)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import Qt, QUrl

# --- ReportLab PDF Imports ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

class VocabQuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Latin Vocabulary Quiz Generator")
        self.setGeometry(100, 100, 400, 400) # Made the window slightly taller

       # --- FONT REGISTRATION (Cross-Platform) ---
        self.font_name = 'Helvetica' # Default fallback
        font_path = None
        
        # 1. Detect Operating System
        current_os = platform.system()
        
        # 2. Assign the correct file paths based on OS
        if current_os == "Darwin":  # 'Darwin' is Python's internal name for macOS
            mac_paths = [
                "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
                "/Library/Fonts/Times New Roman.ttf"
            ]
            for p in mac_paths:
                if os.path.exists(p):
                    font_path = p
                    break
                    
        elif current_os == "Windows":
            # Windows usually calls the file 'times.ttf'
            win_path = "C:\\Windows\\Fonts\\times.ttf"
            if os.path.exists(win_path):
                font_path = win_path

        # 3. Try to load the font if we found a valid path
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path))
                self.font_name = 'TimesNewRoman'
                print(f"Successfully loaded font from: {font_path}")
            except Exception as e:
                print(f"Warning: Found font file but failed to load it: {e}")
        else:
            print("Warning: Times New Roman not found on this system. Macrons might break.")

        self.vocab_list =[]
        
        # --- UI LAYOUT ---
        layout = QVBoxLayout()

        # 1. Status Label
        self.label_status = QLabel("No vocabulary loaded.")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_status.setStyleSheet("color: red; padding: 10px;")
        layout.addWidget(self.label_status)

        # 2. Custom Title Input
        self.lbl_title_input = QLabel("Quiz Title:")
        self.lbl_title_input.setStyleSheet("font-weight: bold; color: #333333;")
        layout.addWidget(self.lbl_title_input)

        self.input_title = QLineEdit("Latin Vocabulary Trial") # Default text
        layout.addWidget(self.input_title)

        # 3. Auto-Open Checkbox
        self.check_open = QCheckBox("Open PDF automatically after generating")
        self.check_open.setChecked(True) # Default to checked
        layout.addWidget(self.check_open)

        # 4. Action Buttons
        self.btn_clipboard = QPushButton("Import from Clipboard")
        self.btn_clipboard.clicked.connect(self.load_from_clipboard)
        layout.addWidget(self.btn_clipboard)

        self.btn_file = QPushButton("Import from TSV File")
        self.btn_file.clicked.connect(self.load_from_file)
        layout.addWidget(self.btn_file)

        self.btn_generate = QPushButton("Generate PDF Quiz")
        self.btn_generate.clicked.connect(self.generate_pdf)
        self.btn_generate.setEnabled(False) # Start disabled
        self.btn_generate.setStyleSheet("padding: 10px; font-weight: bold;")
        layout.addWidget(self.btn_generate)

        # 5. Info Label
        self.lbl_info = QLabel("Requires Tab-Separated format (Term -> Definition)")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_info.setStyleSheet("font-size: 10pt; color: gray;")
        layout.addWidget(self.lbl_info)

        self.setLayout(layout)

    # --- DATA PARSING ---
    def parse_tsv_data(self, data_string):
        """Parses a string of TSV data into a list of tuples."""
        try:
            f = io.StringIO(data_string)
            reader = csv.reader(f, delimiter='\t')
            data =[]
            for row in reader:
                if len(row) >= 2:
                    term = row[0].strip()
                    definition = row[1].strip()
                    if term and definition:
                        data.append((term, definition))
            return data
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse data: {e}")
            return []
    def update_status(self):
        count = len(self.vocab_list)
        if count > 0:
            self.label_status.setText(f"Loaded {count} items successfully.")
            self.label_status.setStyleSheet("color: green; padding: 10px;")
            self.btn_generate.setEnabled(True)
        else:
            self.label_status.setText("No valid items found.")
            self.label_status.setStyleSheet("color: red; padding: 10px;")
            self.btn_generate.setEnabled(False)

    def load_from_clipboard(self):
        clipboard = QApplication.clipboard()
        content = clipboard.text()
        if not content:
            QMessageBox.warning(self, "Error", "Clipboard is empty.")
            return
        self.vocab_list = self.parse_tsv_data(content)
        self.update_status()

    def load_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "TSV Files (*.tsv *.txt);;All Files (*)")
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.vocab_list = self.parse_tsv_data(content)
                self.update_status()

    def generate_pdf(self):
        if not self.vocab_list:
            return

        # Get title from the input box
        quiz_title = self.input_title.text()
        if not quiz_title.strip():
            quiz_title = "Latin Vocabulary Quiz"

        num_items = min(20, len(self.vocab_list))
        quiz_items = random.sample(self.vocab_list, num_items)

        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "latin_quiz.pdf", "PDF Files (*.pdf)")
        if not save_path:
            return

        try:
            self.create_pdf_layout(save_path, quiz_items, quiz_title)
            
            # Check the box state for auto-opening
            if self.check_open.isChecked():
                QDesktopServices.openUrl(QUrl.fromLocalFile(save_path))
            else:
                QMessageBox.information(self, "Success", f"Quiz saved to:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF: {e}\n{sys.exc_info()}")

    def create_pdf_layout(self, filename, items, title):
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        margin = 0.75 * inch
        column_gap = 0.5 * inch
        col_width = (width - (2 * margin) - column_gap) / 2
        
        c.setFont(self.font_name, 18)
        c.drawString(margin, height - margin, title)
        
        c.setFont(self.font_name, 12)
        c.drawRightString(width - margin, height - margin, "Nōmen mihi est: _________________")
        c.drawRightString(width - margin, height - margin - 20, "Diēs: __________________")

        c.line(margin, height - margin - 40, width - margin, height - margin - 40)

        y_start = height - margin - 60
        items_per_col = 10
        
        style = ParagraphStyle(
            'LatinItem',
            fontName=self.font_name,
            fontSize=11,
            leading=13,
            firstLineIndent=0,
            leftIndent=10 
        )

        slot_height = 65 

        for index, (term, definition) in enumerate(items):
            col = 0 if index < items_per_col else 1
            row_in_col = index if index < items_per_col else index - items_per_col
            
            x_pos = margin + (col * (col_width + column_gap))
            slot_top_y = y_start - (row_in_col * slot_height)

            c.setFont(self.font_name, 11)
            c.drawString(x_pos, slot_top_y, f"{index + 1}.")

            p = Paragraph(term, style)
            actual_width, actual_height = p.wrap(col_width - 25, slot_height)
            
            text_x = x_pos + 25
            p.drawOn(c, text_x, slot_top_y - actual_height + 11) 

            line_gap = 25 
            line_y = slot_top_y - actual_height - line_gap
            
            c.setLineWidth(0.5)
            c.line(text_x, line_y, x_pos + col_width, line_y)

        c.setFont(self.font_name, 8)
        c.drawCentredString(width / 2, margin / 2, "Generated automatically by VocabQuizMaker")
        c.save()

# --- Execution Block (Must be completely un-indented, aligned to the far left edge) ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VocabQuizApp()
    window.show()
    sys.exit(app.exec())