import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QPlainTextEdit, QLabel, 
                             QPushButton, QInputDialog, QMessageBox, QSplitter,
                             QComboBox, QTabWidget, QLineEdit)
from PyQt6.QtGui import QColor, QFont, QIcon, QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtCore import Qt, QRegularExpression, QFileSystemWatcher, QTimer
from src.themes import ThemeManager
from config_manager import ConfigManager

# ... (Previous imports remain, ensure QFileSystemWatcher is added)

# --- SYNTAX HIGHLIGHTER ---
# --- SYNTAX HIGHLIGHTER ---
class UniversalHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []
        self.current_language = "Python"
        self.update_rules("Python")

    def set_language(self, language):
        self.current_language = document_language = language
        self.update_rules(language)
        self.rehighlight()

    def update_rules(self, language):
        self.rules = []
        
        # Common formats
        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor("#569cd6")) 
        keyword_fmt.setFontWeight(QFont.Weight.Bold)
        
        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor("#ce9178"))
        
        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#6a9955"))
        
        class_fmt = QTextCharFormat()
        class_fmt.setForeground(QColor("#4ec9b0"))
        
        if language == "Python":
            keywords = [
                "def", "class", "if", "else", "elif", "while", "for", "in", "try", "except",
                "import", "from", "return", "True", "False", "None", "and", "or", "not", "as",
                "with", "pass", "lambda", "break", "continue", "global", "nonlocal", "raise", 
                "yield", "del", "assert", "async", "await"
            ]
            self.rules.append((QRegularExpression(r"\".*\""), string_fmt))
            self.rules.append((QRegularExpression(r"'.*'"), string_fmt))
            self.rules.append((QRegularExpression(r"#[^\n]*"), comment_fmt))
            
        elif language == "Java":
            keywords = [
                "public", "private", "protected", "class", "static", "void", "main", "int", 
                "double", "float", "boolean", "char", "String", "if", "else", "for", "while", 
                "return", "new", "this", "super", "extends", "implements", "interface", "package", 
                "import", "try", "catch", "finally", "throw", "throws", "null", "true", "false"
            ]
            self.rules.append((QRegularExpression(r"\".*\""), string_fmt))
            self.rules.append((QRegularExpression(r"//[^\n]*"), comment_fmt))
            self.rules.append((QRegularExpression(r"/\*.*?\*/"), comment_fmt)) # Multi-line simple approx
            
        else:
            keywords = []

        for word in keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.rules.append((pattern, keyword_fmt))

    def highlightBlock(self, text):
        for pattern, format in self.rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

# --- CONFIG ---
class ScriptLibrary(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Genesis - Script Library")
        self.resize(1000, 700)
        
        self.save_file = "data/genesis_scripts.json"
        
        # Data Structure: { "Script Name": { "content": "...", "language": "Python" } }
        self.scripts_data = {} 
        self.current_script = None

        # --- UI STYLING (Matching the DAG) ---
        cfg = ConfigManager._get_shared_instance()
        theme_name = cfg.get_theme()
        use_gradient = cfg.is_gradient_enabled()
        self.setStyleSheet(ThemeManager.get_stylesheet(theme_name, use_gradient))

        # Additional overrides handled by stylesheet in ThemeManager now
        # But we need to ensure specific widget styles that were inline are preserved if ThemeManager doesn't cover them.
        # ThemeManager stylesheet covers QListWidget, QPlainTextEdit generic colors.
        # But some specific borders/radius might be worth keeping if ThemeManager is generic.
        # Actually, ThemeManager is quite comprehensive now. Let's trust it for colors and add structural styles if needed.
        
        # Override for specific layout needs if not in ThemeManager
        # ... logic below handles layout widgets ...

        # --- Main Layout ---
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # 1. Toolbar
        toolbar = QHBoxLayout()
        
        self.btn_home = QPushButton("🏠 Menu")
        self.btn_home.clicked.connect(self.return_to_launcher)
        toolbar.addWidget(self.btn_home)

        # Assistant Button
        self.btn_ai = QPushButton("🤖")
        self.btn_ai.setToolTip("Open Neural Assistant")
        self.btn_ai.setFixedWidth(40)
        self.btn_ai.setStyleSheet("background-color: #3e3e42; border: 1px solid #555;")
        self.btn_ai.clicked.connect(self.open_assistant)
        toolbar.addWidget(self.btn_ai)

        toolbar.addSpacing(15)
        lbl_title = QLabel("Script Treasury")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        toolbar.addWidget(lbl_title)

        toolbar.addStretch()

        # Language Selector
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Plain Text", "Python", "Java"])
        self.combo_lang.currentIndexChanged.connect(self.change_language)
        toolbar.addWidget(self.combo_lang)

        # Search Bar
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Search scripts...")
        self.txt_search.setStyleSheet("background-color: #252526; color: #d4d4d4; border: 1px solid #3e3e42; padding: 4px; border-radius: 4px;")
        self.txt_search.setFixedWidth(200)
        self.txt_search.textChanged.connect(self.filter_scripts)
        toolbar.addWidget(self.txt_search)

        self.btn_run = QPushButton("▶ Run")
        self.btn_run.setStyleSheet("background-color: #2da44e; color: white; border: none; font-weight: bold;")
        self.btn_run.clicked.connect(self.run_script)
        toolbar.addWidget(self.btn_run)

        self.btn_new = QPushButton("+ New Script")
        self.btn_new.setObjectName("ActionBtn")
        self.btn_new.clicked.connect(self.new_script)
        toolbar.addWidget(self.btn_new)

        self.btn_save = QPushButton("💾 Save")
        self.btn_save.setObjectName("ActionBtn")
        self.btn_save.clicked.connect(self.save_current_script)
        toolbar.addWidget(self.btn_save)

        self.btn_copy = QPushButton("📋 Copy")
        self.btn_copy.setStyleSheet("background-color: #2da44e; border: none;") # Github Green
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        toolbar.addWidget(self.btn_copy)

        self.btn_delete = QPushButton("🗑️")
        self.btn_delete.setObjectName("DeleteBtn")
        self.btn_delete.clicked.connect(self.delete_script)
        toolbar.addWidget(self.btn_delete)

        main_layout.addLayout(toolbar)

        # 2. Splitter (Sidebar vs Editor)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Tabs (User vs Auto)
        self.tabs = QTabWidget()
        self.tabs.setFixedWidth(260)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #3e3e42; }
            QTabBar::tab { background: #2d2d2d; color: #888; padding: 6px; }
            QTabBar::tab:selected { background: #1e1e1e; color: white; border-top: 2px solid #007acc; }
        """)
        
        # Tab 1: User Scripts
        self.list_user = QListWidget()
        self.list_user.currentItemChanged.connect(self.load_selected_script)
        self.tabs.addTab(self.list_user, "User Scripts")
        
        # Tab 2: Genesis Learning
        self.list_auto = QListWidget()
        self.list_auto.currentItemChanged.connect(self.load_selected_script)
        self.tabs.addTab(self.list_auto, "Genesis Learning")
        
        splitter.addWidget(self.tabs)


        # Right: Editor & Output Splitter
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Select or create a script to begin writing...")
        right_splitter.addWidget(self.editor)
        
        # Console Output
        self.output_console = QPlainTextEdit()
        self.output_console.setPlaceholderText("Console Output...")
        self.output_console.setReadOnly(True)
        self.output_console.setStyleSheet("font-family: 'Consolas', monospace; font-size: 12px; background-color: #0a0a0a; color: #cccccc;")
        self.output_console.setFixedHeight(150)
        right_splitter.addWidget(self.output_console)
        
        splitter.addWidget(right_splitter)

        # Initialize Highlighter
        self.highlighter = UniversalHighlighter(self.editor.document())

        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(1, 1) # Give editor more space
        main_layout.addWidget(splitter)

        # Load Data
        self.load_data()

        # --- LIVE UPDATE WATCHER ---
        self.watcher = QFileSystemWatcher(self)
        if os.path.exists(self.save_file):
            self.watcher.addPath(os.path.abspath(self.save_file))
        self.watcher.fileChanged.connect(self.reload_external_changes)

    def reload_external_changes(self, path):
        """Called when genesis_scripts.json is modified externally (e.g. by AI)."""
        # We need to reload, but assume the User might be typing. 
        # Strategy: Reload list. If current script was modified externally, warn or update.
        print(f"File changed: {path} - Reloading...")
        
        # 1. Read Change
        new_data = {}
        try:
            with open(self.save_file, 'r') as f:
                new_data = json.load(f)
        except: return # File might be being written to, ignore partial

        # 2. Check diff
        # Simple approach: Just update the list items for now
        current_names = set(self.scripts_data.keys())
        new_names = set(new_data.keys())
        
        # If new scripts appeared (AI created one)
        if new_names != current_names:
            # Refresh Lists
            self.refresh_lists()
            
            # Try to restore selection
            if self.current_script and self.current_script in self.scripts_data:
                # Determine which list
                target_list = self.list_auto if self.current_script.startswith("auto_") or self.current_script.startswith("genesis_") else self.list_user
                items = target_list.findItems(self.current_script, Qt.MatchFlag.MatchExactly)
                if items:
                    target_list.setCurrentItem(items[0])

            
            # Re-add path to watcher (sometimes editors delete/recreate file breaking watch)
            if os.path.exists(self.save_file):
                self.watcher.addPath(os.path.abspath(self.save_file))

    # --- LOGIC ---
    def load_data(self):
        """Loads scripts from JSON."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    self.scripts_data = json.load(f)
            except:
                self.scripts_data = {}
        
        # Migration: Check raw content vs dict content
        for name, data in self.scripts_data.items():
            if isinstance(data, str):
                # Migrate to object
                self.scripts_data[name] = {
                    "content": data,
                    "language": "Plain Text" # Default
                }

        self.refresh_lists()
        
    def refresh_lists(self):
        """Sorts scripts into tabs."""
        self.list_user.clear()
        self.list_auto.clear()
        
        for name in sorted(self.scripts_data.keys()):
            # Filter logic
            search_text = self.txt_search.text().lower()
            if search_text and search_text not in name.lower():
                continue

            if name.startswith("auto_") or name.startswith("genesis_"):
                self.list_auto.addItem(name)
            else:
                self.list_user.addItem(name)

    def filter_scripts(self):
        self.refresh_lists()


    def save_data(self):
        """Writes data to JSON."""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.scripts_data, f, indent=4)
        except Exception as e:
            print(f"Save error: {e}")

    def new_script(self):
        name, ok = QInputDialog.getText(self, "New Script", "Script Name:")
        if ok and name:
            if name in self.scripts_data:
                QMessageBox.warning(self, "Error", "Script already exists!")
                return
            
            # Save current before switching
            if self.current_script:
                self.save_current_script()

            # Create new
            self.scripts_data[name] = {
                "content": "",
                "language": "Python" # Default for new
            }
            # New human scripts go to User tab
            self.list_user.addItem(name)
            self.list_user.setCurrentRow(self.list_user.count() - 1)
            self.tabs.setCurrentIndex(0) # Switch to User tab
            self.save_data()


    def load_selected_script(self, current, previous):
        """Called when user clicks a list item."""
        
        # 1. Save previous
        if previous:
            prev_name = previous.text()
            if prev_name in self.scripts_data:
                # Update content from editor
                self.scripts_data[prev_name]["content"] = self.editor.toPlainText()
                # Language is already active in combo, but we don't need to read it back 
                # because change_language logic handles updates instantly? 
                # Actually, better to just sync everything here to be safe.
                self.scripts_data[prev_name]["language"] = self.combo_lang.currentText()

        # 2. Block Signals (Prevent loop when setting combo)
        self.combo_lang.blockSignals(True)

        if current:
            self.current_script = current.text()
            data = self.scripts_data.get(self.current_script, {"content": "", "language": "Plain Text"})
            
            self.editor.setPlainText(data.get("content", ""))
            
            lang = data.get("language", "Plain Text")
            idx = self.combo_lang.findText(lang)
            if idx >= 0:
                self.combo_lang.setCurrentIndex(idx)
            else:
                self.combo_lang.setCurrentIndex(0)

            # Apply Highlighting logic
            self.apply_highlighting(lang)
        else:
            self.current_script = None
            self.editor.clear()
            self.combo_lang.setCurrentIndex(0)
            self.apply_highlighting("Plain Text")

        self.combo_lang.blockSignals(False)

    def change_language(self):
        """Called when combo box changes."""
        if not self.current_script: return
        
        new_lang = self.combo_lang.currentText()
        if self.current_script in self.scripts_data:
            self.scripts_data[self.current_script]["language"] = new_lang
        
        self.apply_highlighting(new_lang)

    def apply_highlighting(self, language):
        self.highlighter.set_language(language)

    def save_current_script(self):
        if self.current_script:
            self.scripts_data[self.current_script]["content"] = self.editor.toPlainText()
            self.scripts_data[self.current_script]["language"] = self.combo_lang.currentText()
            self.save_data()

    def delete_script(self):
        if not self.current_script: return
        
        confirm = QMessageBox.question(self, "Delete", f"Delete '{self.current_script}'?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            del self.scripts_data[self.current_script]
            self.save_data()
            self.load_data() 
            self.editor.clear()
            self.current_script = None # Reset

    def copy_to_clipboard(self):
        cb = QApplication.clipboard()
        cb.setText(self.editor.toPlainText())

    def return_to_launcher(self):
        self.save_current_script() # Auto-save
        try:
            from launcher import GenesisLauncher
            self.launcher = GenesisLauncher()
            self.launcher.show()
            self.close()
        except ImportError:
            QMessageBox.warning(self, "Error", "launcher.py not found.")

    def open_assistant(self):
        try:
            from config_manager import ConfigManager
            if ConfigManager and not ConfigManager.is_ai_enabled():
                QMessageBox.information(self, "AI Disabled", "Neural Assistant is currently disabled in settings.")
                return

            from src.ai.assistant import NeuralAssistant
            self.ai_window = NeuralAssistant()
            self.ai_window.show()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Could not import 'src.ai.assistant'.\n{e}")

    def run_script(self):
        if not self.current_script: return
        
        content = self.editor.toPlainText()
        if not content.strip(): return
        
        lang = self.combo_lang.currentText()
        
        self.output_console.clear()
        self.output_console.appendHtml(f"<b>Running ({lang})...</b><br>")
        
        import tempfile
        import subprocess
        
        try:
            creationflags = 0x08000000 if os.name == 'nt' else 0
            
            if lang == "Python":
                fd, path = tempfile.mkstemp(suffix=".py", text=True)
                with os.fdopen(fd, 'w') as tmp:
                    tmp.write(content)
                
                cmd = [sys.executable, path]
                self._execute_process(cmd, path) # Refactored common exec
                
            elif lang == "Java":
                # Java needs a class file. We need to find class name or force Main.
                # Regex to find 'public class X'
                match = QRegularExpression(r"public\s+class\s+(\w+)").match(content)
                class_name = match.captured(1) if match.hasMatch() else "Main"
                
                # Make a temp dir
                temp_dir = tempfile.mkdtemp()
                java_file = os.path.join(temp_dir, f"{class_name}.java")
                
                with open(java_file, 'w') as f:
                    f.write(content)
                    
                # Compile
                self.output_console.appendHtml("<i>Compiling...</i>")
                compile_proc = subprocess.run(
                    ["javac", java_file], 
                    capture_output=True, text=True, creationflags=creationflags
                )
                
                if compile_proc.returncode != 0:
                    self.output_console.appendHtml(f"<span style='color: #ff5555'>Compilation Failed:</span>")
                    self.output_console.appendPlainText(compile_proc.stderr)
                    shutil.rmtree(temp_dir)
                    return
                
                # Run
                cmd = ["java", "-cp", temp_dir, class_name]
                self._execute_process(cmd, temp_dir, is_dir=True)
                
            else:
                self.output_console.appendPlainText("Language not supported for execution.")

        except Exception as e:
            self.output_console.appendHtml(f"<b style='color: #ff5555'>Execution Error (System): {e}</b>")

    def _execute_process(self, cmd, resource_path, is_dir=False):
        import subprocess
        creationflags = 0x08000000 if os.name == 'nt' else 0
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=creationflags
        )
        
        stdout, stderr = process.communicate()
        
        if stdout:
            self.output_console.appendPlainText(stdout)
        if stderr:
             self.output_console.appendHtml(f"<span style='color: #ff5555'>{stderr}</span>")
        
        if process.returncode == 0:
             self.output_console.appendHtml("<br><b style='color: #2da44e'>Finished Successfully</b>")
        else:
             self.output_console.appendHtml(f"<br><b style='color: #ff5555'>Finished with Exit Code {process.returncode}</b>")
             
        # Cleanup
        if not is_dir and os.path.exists(resource_path):
            os.remove(resource_path)
        elif is_dir and os.path.exists(resource_path):
            import shutil
            shutil.rmtree(resource_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScriptLibrary()
    window.show()
    sys.exit(app.exec())