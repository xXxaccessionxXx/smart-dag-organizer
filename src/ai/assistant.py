import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextBrowser, QPlainTextEdit, QPushButton, 
                             QLabel, QComboBox, QCheckBox)
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

try:
    from src.ai.brain import NeuralBrain
except ImportError:
    NeuralBrain = None

class LearningWorker(QThread):
    """Background thread for continuous self-learning."""
    log_signal = pyqtSignal(str)
    
    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self.running = True
        
    def run(self):
        while self.running:
            if self.brain and hasattr(self.brain, 'auto_learner'):
                success, msg = self.brain.auto_learner.attempt_learning()
                self.log_signal.emit(msg)
                
                # Sleep based on success/failure (learning takes time)
                # Success = 10 sec rest, Failure = 5 sec rest
                self.msleep(10000 if success else 5000)
            else:
                self.msleep(2000)

    def stop(self):
        self.running = False
        self.wait()


class NeuralAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Genesis - Neural Assistant")
        self.resize(500, 700)
        
        self.brain = NeuralBrain() if NeuralBrain else None

        # --- UI STYLING ---
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QWidget { color: #d4d4d4; font-family: 'Segoe UI'; font-size: 14px; }
            
            QTextBrowser {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Segoe UI';
            }
            
            QPlainTextEdit {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Segoe UI';
            }

            QPushButton { 
                background-color: #007acc; color: white; border: none; 
                padding: 8px 15px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #0062a3; }
            
            QComboBox {
                background-color: #3e3e42; color: white; border: 1px solid #555;
                padding: 4px; border-radius: 4px;
            }
            QComboBox QAbstractItemView { background-color: #252526; color: white; selection-background-color: #007acc; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Header Area
        header_layout = QHBoxLayout()
        header = QLabel("Neural Assistant")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        # Persona Selector
        self.combo_persona = QComboBox()
        if self.brain:
            self.combo_persona.addItems(self.brain.get_persona_names())
            self.combo_persona.currentTextChanged.connect(self.change_persona)
            # Default to Shepherd as requested? Or Standard? Let's default to Standard but available.
            self.combo_persona.setCurrentText("Standard") 
        else:
            self.combo_persona.addItem("Brain Offline")
            self.combo_persona.setEnabled(False)
            
        header_layout.addWidget(self.combo_persona)
        
        # Auto-Learning Toggle
        self.check_learn = QCheckBox("Continuous Learning")
        self.check_learn.setToolTip("Enable background auto-coding loop")
        self.check_learn.stateChanged.connect(self.toggle_learning)
        header_layout.addWidget(self.check_learn)
        
        layout.addLayout(header_layout)
        
        # Worker Thread
        self.learning_worker = None


        # Chat History
        self.history = QTextBrowser()
        self.history.setOpenExternalLinks(True)
        layout.addWidget(self.history)

        # Input Area
        input_layout = QHBoxLayout()
        
        self.input_field = QPlainTextEdit()
        self.input_field.setFixedHeight(60)
        self.input_field.setPlaceholderText("Ask me anything...")
        input_layout.addWidget(self.input_field)

        self.btn_send = QPushButton("Send")
        self.btn_send.setFixedWidth(80)
        self.btn_send.setFixedHeight(60)
        self.btn_send.clicked.connect(self.send_message)
        input_layout.addWidget(self.btn_send)

        layout.addLayout(input_layout)

        # Welcome Message
        if self.brain:
            self.append_system_message(self.brain.get_response("hello"))
        else:
            self.append_system_message("System online. Brain module missing.")

    def change_persona(self, persona_name):
        if self.brain:
            self.brain.set_persona(persona_name)
            self.append_system_message(f"<i>Persona switched to: {persona_name}</i>")

    def send_message(self):
        text = self.input_field.toPlainText().strip()
        if not text:
            return
        
        self.append_user_message(text)
        self.input_field.clear()
        
        self.process_response(text)

    def process_response(self, text):
        if self.brain:
            response = self.brain.get_response(text)
            
            # Check for Thinking trace
            if response.startswith("(Thinking:"):
                # Split at the double newline we added in brain
                parts = response.split(")\n\n", 1)
                if len(parts) == 2:
                    trace = parts[0] + ")"
                    active_response = parts[1]
                    
                    # Style the Thinking part
                    self.history.append(f"<div style='color: #666; font-style: italic; font-size: 12px;'>{trace}</div>")
                    # Style the Actual Response
                    self.append_system_message(active_response)
                else:
                    self.append_system_message(response)
            else:
                self.append_system_message(response)
        else:
            self.append_system_message("Brain module not found.")

    def append_user_message(self, text):
        self.history.append(f"<div style='color: #4ec9b0;'><b>User:</b> {text}</div><br>")

    def append_system_message(self, text):
        self.history.append(f"<div style='color: #ce9178;'><b>Assistant:</b> {text}</div><br>")
        
    def toggle_learning(self, state):
        if state == 2: # Checked
            if not self.learning_worker:
                self.learning_worker = LearningWorker(self.brain)
                self.learning_worker.log_signal.connect(self.on_learning_log)
                self.learning_worker.start()
            self.append_system_message("<i>Continuous Learning Module: ACTIVATED. I will now practice coding in the background.</i>")
        else:
            if self.learning_worker:
                self.learning_worker.stop()
                self.learning_worker = None
            self.append_system_message("<i>Continuous Learning Module: DEACTIVATED.</i>")
            
    def on_learning_log(self, msg):
        """Displays learning events in the Thinking style."""
        self.history.append(f"<div style='color: #888; font-style: italic; font-size: 11px;'>[Auto-Learner] {msg}</div>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NeuralAssistant()
    window.show()
    sys.exit(app.exec())
