from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QDateTimeEdit, QTextEdit, QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import QDateTime, Qt

class EventDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Google Calendar Event")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # Summary
        layout.addWidget(QLabel("Event Title:"))
        self.txt_summary = QLineEdit()
        self.txt_summary.setPlaceholderText("e.g. Project Meeting")
        layout.addWidget(self.txt_summary)
        
        # Start Time
        layout.addWidget(QLabel("Start Time:"))
        self.dt_start = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_start.setCalendarPopup(True)
        layout.addWidget(self.dt_start)
        
        # End Time
        layout.addWidget(QLabel("End Time:"))
        self.dt_end = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600))
        self.dt_end.setCalendarPopup(True)
        layout.addWidget(self.dt_end)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.txt_description = QTextEdit()
        layout.addWidget(self.txt_description)
        
        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        # Apply Styles
        self.setStyleSheet("""
            QDialog { background-color: #252526; color: white; }
            QLabel { color: #cccccc; font-weight: bold; margin-top: 5px; }
            QLineEdit, QTextEdit, QDateTimeEdit { 
                background-color: #333333; 
                color: white; 
                border: 1px solid #555; 
                padding: 5px; 
                border-radius: 3px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #1177bb; }
        """)

    def validate_and_accept(self):
        if not self.txt_summary.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an event title.")
            return
            
        if self.dt_start.dateTime() >= self.dt_end.dateTime():
            QMessageBox.warning(self, "Validation Error", "End time must be after start time.")
            return
            
        self.accept()
    
    def get_data(self):
        return {
            "summary": self.txt_summary.text(),
            "description": self.txt_description.toPlainText(),
            "start_time": self.dt_start.dateTime().toPyDateTime(),
            "end_time": self.dt_end.dateTime().toPyDateTime()
        }
