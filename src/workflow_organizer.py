import sys
import os
import ctypes
import json
import uuid 
import math

# --- Safe Import Logic ---
def show_error_and_exit(missing_module):
    """Displays a native error dialog and exits."""
    message = (f"Error: Could not import '{missing_module}'.\n\n"
               "Please ensure you are running this script within the Python Virtual Environment.\n"
               "Try running: .venv\\Scripts\\python.exe workflow_organizer.py")
    title = "Dependency Missing"
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x10 | 0x0)
    sys.exit(1)

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, 
                                 QGraphicsScene, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                                 QGraphicsRectItem, QGraphicsItem, QGraphicsTextItem, 
                                 QPushButton, QGraphicsLineItem, QMenu, QFileDialog, 
                                 QInputDialog, QComboBox, QMessageBox, QGraphicsProxyWidget,
                                 QFrame, QTextEdit, QGraphicsDropShadowEffect, QLineEdit) # Added items
    from PyQt6.QtGui import (QColor, QFont, QPen, QBrush, QAction, QDesktopServices, 
                             QPainter, QCursor, QTransform, QLinearGradient, QPainterPath)
    from PyQt6.QtCore import Qt, QTimer, QLineF, QUrl, QPointF, QRectF, QSizeF
except ImportError:
    show_error_and_exit("PyQt6")

# --- 1. Custom Graphics View ---
class SmartView(QGraphicsView):
    def __init__(self, scene, main_window_ref):
        super().__init__(scene)
        self.main_window = main_window_ref 
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag) 
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self._is_panning = False
        self._pan_start = QPointF(0, 0)
        
        self._current_zoom = 1.0
        self._min_zoom = 0.5  
        self._max_zoom = 2.0 

        self.grid_color_light = QColor("#2d2d30")
        self.grid_color_dark = QColor("#1e1e1e")
        self.setBackgroundBrush(self.grid_color_dark)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        grid_size = 50
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        
        lines = []
        right = int(rect.right())
        bottom = int(rect.bottom())
        
        for x in range(left, right, grid_size):
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
        
        for y in range(top, bottom, grid_size):
            lines.append(QLineF(rect.left(), y, rect.right(), y))

        pen = QPen(self.grid_color_light)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLines(lines)

    def keyPressEvent(self, event):
        # Check if a text widget has focus
        focus_widget = QApplication.focusWidget()
        if isinstance(focus_widget, (QTextEdit, QLineEdit)):
             super().keyPressEvent(event)
             return

        focus_item = self.scene().focusItem()
        if isinstance(focus_item, (QGraphicsTextItem, QGraphicsProxyWidget)):
            super().keyPressEvent(event)
            return

        if event.key() == Qt.Key.Key_Space:
            self.main_window.focus_camera_on_nodes()
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            zoom_in_factor = 1.1
            zoom_out_factor = 1 / zoom_in_factor

            if event.angleDelta().y() > 0:
                zoom_factor = zoom_in_factor
            else:
                zoom_factor = zoom_out_factor
            
            new_zoom = self._current_zoom * zoom_factor

            if self._min_zoom <= new_zoom <= self._max_zoom:
                self.scale(zoom_factor, zoom_factor)
                self._current_zoom = new_zoom
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

# --- 2. The Connection Line Class ---
class ConnectionLine(QGraphicsLineItem):
    def __init__(self, start_node, end_node):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        
        pen = QPen(QColor("#666666"))
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine) 
        self.setPen(pen)
        self.setZValue(-1) 
        
        self.update_position()

    def update_position(self):
        if not self.start_node.scene() or not self.end_node.scene():
            return

        start_pos = self.start_node.scenePos()
        end_pos = self.end_node.scenePos()
        
        offset_x = 100 
        offset_y = 40
        source_point = start_pos + QPointF(offset_x, offset_y)
        dest_point = end_pos + QPointF(offset_x, offset_y)
        self.setLine(QLineF(source_point, dest_point))

# --- 3a. Note Popup Class ---
class NotePopup(QGraphicsProxyWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setZValue(1000) 
        self.setAcceptHoverEvents(True) # Crucial for grace period logic
        
        # Container Widget
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: #2D2D30;
                border: 1px solid #454545;
                border-radius: 6px;
            }
            QLabel { color: #d4d4d4; border: none; }
            QTextEdit { 
                background-color: #1e1e1e; 
                color: #e0e0e0; 
                border: 1px solid #3e3e42;
                border-radius: 3px;
                font-family: 'Segoe UI';
                font-size: 11px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px;
            }
            QPushButton:hover { background-color: #1177bb; }
        """)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Title
        self.lbl_title = QLabel("Node Title")
        self.lbl_title.setStyleSheet("font-weight: bold; font-size: 13px; color: white;")
        layout.addWidget(self.lbl_title)
        
        # Type/Path
        self.lbl_info = QLabel("Type: None")
        self.lbl_info.setStyleSheet("color: #888888; font-size: 10px;")
        layout.addWidget(self.lbl_info)
        
        # Separator
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setStyleSheet("background-color: #454545; max-height: 1px;")
        layout.addWidget(self.line)

        # Notes Area (Interactive)
        self.txt_notes = QTextEdit()
        self.txt_notes.setPlaceholderText("Add notes here...")
        self.txt_notes.setReadOnly(False) 
        self.txt_notes.setMaximumHeight(100)
        self.txt_notes.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.txt_notes)
        
        # Image Preview
        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setVisible(False)
        layout.addWidget(self.lbl_image)

        # Action Buttons
        self.btn_open = QPushButton("🚀 Open Attachment")
        self.btn_open.clicked.connect(self._on_open_clicked)
        self.btn_open.setVisible(False)
        layout.addWidget(self.btn_open)

        self.setWidget(self.container)
        self.setVisible(False)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.updating = False

    def update_content(self, title, type_str, path, notes):
        self.updating = True # Block signal loop
        
        self.lbl_title.setText(title)
        
        info_text = f"Type: {type_str}"
        if path:
            info_text += f"\nPath: {path}"
        self.lbl_info.setText(info_text)
        
        self.txt_notes.setPlainText(notes)
        self.txt_notes.setVisible(True)

        # Image Preview
        self.lbl_image.setVisible(False)
        if type_str == "File" and path:
            ext = os.path.splitext(path)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                img_html = f"<img src='{QUrl.fromLocalFile(path).toString()}' width='200'>"
                self.lbl_image.setText(img_html)
                self.lbl_image.setVisible(True)

        # Action Button
        if type_str != "None" and path:
             self.btn_open.setVisible(True)
        else:
             self.btn_open.setVisible(False)

        self.container.adjustSize()
        self.resize(QSizeF(self.container.size()))
        self.updating = False

    def _on_text_changed(self):
        if self.updating: return
        # Update parent node notes
        if self.parentItem():
             self.parentItem().update_notes_from_popup(self.txt_notes.toPlainText())

    def _on_open_clicked(self):
        if self.parentItem():
             self.parentItem().open_attachment()

    def hoverEnterEvent(self, event):
        if self.parentItem():
            self.parentItem().stop_hide_timer()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if self.parentItem():
             self.parentItem().start_hide_timer()
        super().hoverLeaveEvent(event)

# --- 3. The Smart Node Class ---
class SmartNode(QGraphicsRectItem):
    def __init__(self, name, x, y, main_window_ref, watch_path=None, node_id=None):
        super().__init__(0, 0, 200, 80) 
        
        self.main_window = main_window_ref 
        self.name = name
        self.id = node_id if node_id else str(uuid.uuid4()) 
        
        self.watch_path = watch_path
        self.attachment_type = "None" 
        self.connected_lines = [] 
        self.custom_color = None 
        self.is_completed = False 
        self.is_start_node = False 
        
        # New Features
        self.notes = ""
        self.is_collapsed = False

        self.setPos(x, y)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        # Default Pens
        self.pen_default = QPen(Qt.PenStyle.NoPen)
        # Gold Pen for Start Node
        self.pen_start = QPen(QColor("#FFD700")) 
        self.pen_start.setWidth(3)

        self.brush_pending = QBrush(QColor("#3e3e42")) 
        self.brush_done = QBrush(QColor("#2da44e"))   
        self.brush_link = QBrush(QColor("#007acc"))   
        self.brush_disabled = QBrush(QColor("#252526")) 
        
        self.setBrush(self.brush_pending)
        self.setPen(self.pen_default)

        # Title
        self.text_item = QGraphicsTextItem(name, self)
        self.set_text_style(completed=False)
        self.text_item.setPos(10, 15)
        self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.text_item.document().contentsChanged.connect(self.update_name_from_text)

        # Type Indicator
        self.type_item = QGraphicsTextItem("", self)
        self.type_item.setDefaultTextColor(QColor("#aaaaaa"))
        self.type_item.setFont(QFont("Segoe UI", 8))
        self.type_item.setPos(10, 45)

        # Note Indicator
        self.note_item = QGraphicsTextItem("📝", self)
        self.note_item.setDefaultTextColor(QColor("#ffd700"))
        self.note_item.setPos(165, 5) # Shifted slightly left
        self.note_item.setVisible(False)

        # Collapse Button
        self.collapse_btn = QGraphicsTextItem("[-]", self)
        self.collapse_btn.setDefaultTextColor(QColor("#00aaff"))
        self.collapse_btn.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.collapse_btn.setPos(180, 2)
        
        # Hover Support
        self.setAcceptHoverEvents(True)
        self.popup = NotePopup(self)
        self.popup.setVisible(False) 
        
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(lambda: self.popup.setVisible(False))

    def hoverEnterEvent(self, event):
        self.stop_hide_timer()
        # Update Popup Data
        self.popup.update_content(self.name, self.attachment_type, self.watch_path, self.notes)
        
        # Position Popup 
        self.popup.setPos(self.rect().width() + 10, 0)
        self.popup.setVisible(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.start_hide_timer()
        super().hoverLeaveEvent(event)
        
    def start_hide_timer(self):
        from src.config_manager import ConfigManager
        # Access static method, which returns instance
        cfg = ConfigManager._get_shared_instance()
        if cfg.get_hover_persistence():
            self.hide_timer.start(300) 
        else:
            self.hide_timer.start(0)

    def stop_hide_timer(self):
        self.hide_timer.stop()

    def update_notes_from_popup(self, new_text):
        self.notes = new_text
        self.check_status() # Update icon if notes added/removed

    def open_attachment(self):
        if self.watch_path and os.path.exists(self.watch_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.watch_path))
        else:
            print(f"Cannot open file: {self.watch_path}")

    def mousePressEvent(self, event):
        # Check if click is on the collapse button
        # Map event pos to local coordinates
        local_pos = event.pos()
        btn_rect = self.collapse_btn.mapRectToParent(self.collapse_btn.boundingRect())
        
        if btn_rect.contains(local_pos):
            self.toggle_collapse()
            event.accept()
        else:
            super().mousePressEvent(event)

    def set_text_style(self, completed=False):
        font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        if completed:
            font.setStrikeOut(True)
            self.text_item.setDefaultTextColor(QColor("#B0B0B0"))
        else:
            font.setStrikeOut(False)
            self.text_item.setDefaultTextColor(Qt.GlobalColor.white)
        self.text_item.setFont(font)

    def update_name_from_text(self):
        self.name = self.text_item.toPlainText()

    def contextMenuEvent(self, event):
        menu = QMenu()
        
        # Start Node Toggle
        if self.is_start_node:
            action_start = menu.addAction("🚫 Unset Start Node")
        else:
            action_start = menu.addAction("🏁 Set as Start Node")
        action_start.triggered.connect(self.toggle_start_node)

        menu.addSeparator()

        # Collapse / Expand
        if self.is_collapsed:
            action_col = menu.addAction("🔼 Expand")
        else:
            action_col = menu.addAction("🔽 Collapse")
        action_col.triggered.connect(self.toggle_collapse)

        action_notes = menu.addAction("📝 Edit Notes")
        action_notes.triggered.connect(self.edit_notes)

        menu.addSeparator()

        if self.is_completed:
            action_done = menu.addAction("Incomplete Task")
        else:
            action_done = menu.addAction("✅ Mark as Done")
        action_done.triggered.connect(self.toggle_complete)
        
        menu.addSeparator()

        color_menu = menu.addMenu("🎨 Set Color")
        colors = {"Default": None, "Urgent (Red)": "#d73a49", "Work (Blue)": "#0366d6", 
                  "Idea (Purple)": "#6f42c1", "Warning (Orange)": "#d19a66"}
        for name, hex_code in colors.items():
            action = color_menu.addAction(name)
            action.triggered.connect(lambda checked, h=hex_code: self.set_custom_color(h))

        menu.addSeparator()

        if not self.is_collapsed:
            action_file = menu.addAction("📄 Attach File")
            action_file.triggered.connect(self.browse_file)
            action_folder = menu.addAction("📁 Attach Folder")
            action_folder.triggered.connect(self.browse_folder)
            action_link = menu.addAction("🌐 Attach Web Link")
            action_link.triggered.connect(self.input_link)
            
            if self.watch_path:
                menu.addSeparator()
                action_open = menu.addAction("🚀 Open Attachment")
                action_open.triggered.connect(self.open_attachment)
                action_remove = menu.addAction("❌ Remove Attachment")
                action_remove.triggered.connect(self.remove_attachment)

            menu.addSeparator()
            
        action_delete = menu.addAction("🗑️ Delete Node")
        action_delete.triggered.connect(self.delete_self)

        menu.exec(event.screenPos())

    def toggle_start_node(self):
        self.is_start_node = not self.is_start_node
        self.check_status() 

    def delete_self(self):
        self.main_window.delete_node(self)

    def toggle_complete(self):
        self.is_completed = not self.is_completed
        self.set_text_style(self.is_completed)
        self.check_status()
        self.main_window.update_progress()

    def set_custom_color(self, color_hex):
        self.custom_color = color_hex
        self.check_status()

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(None, "Select File")
        if path: self.set_attachment(path, "File")

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(None, "Select Folder")
        if path: self.set_attachment(path, "Folder")

    def input_link(self):
        text, ok = QInputDialog.getText(None, "Attach Link", "Enter URL:")
        if ok and text: self.set_attachment(text, "Link")

    def remove_attachment(self):
        self.watch_path = None
        self.attachment_type = "None"
        self.check_status()

    def set_attachment(self, path, type_name):
        self.watch_path = path
        self.attachment_type = type_name
        self.check_status() 

    def open_attachment(self):
        if self.watch_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.watch_path) if self.attachment_type != "Link" else QUrl(self.watch_path))

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for line in self.connected_lines:
                line.update_position()
            
            # --- CRASH FIX ---
            # Removed the ensureVisible call. 
            # It creates infinite recursion loops during drag events.
            # Stability is prioritized over auto-scroll.
            
        return super().itemChange(change, value)

    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.collapse_btn.setPlainText("[+]")
            # self.setRect(0, 0, 200, 35) # NO SHRINKING
            # self.type_item.setVisible(False) 
            # self.text_item.setPos(5, 5)
            self.set_visibility_recursive(False) # Hide children
        else:
            self.collapse_btn.setPlainText("[-]")
            # self.setRect(0, 0, 200, 80) # Expanding back (if we were shrinking)
            # self.type_item.setVisible(True)
            # self.text_item.setPos(10, 15)
            self.set_visibility_recursive(True) # Show children
        
        self.update()

    def set_visibility_recursive(self, visible):
        """Recursively hide/show downstream nodes."""
        # Find downstream nodes via connected_lines where self is start_node
        for line in self.connected_lines:
            if line.start_node == self:
                line.setVisible(visible)
                child = line.end_node
                
                # Recursion:
                child.setVisible(visible) 
                
                if visible:
                    if not child.is_collapsed:
                        child.set_visibility_recursive(True)
                else:
                    child.set_visibility_recursive(False)

    def check_status(self):
        # Update Color
        if self.is_completed:
            self.setBrush(self.brush_done)
        elif self.custom_color:
             self.setBrush(QBrush(QColor(self.custom_color)))
        elif self.watch_path:
            if self.attachment_type == "Link":
                self.setBrush(self.brush_link)
            elif self.watch_path and os.path.exists(self.watch_path):
                self.setBrush(self.brush_done)
            else:
                 self.setBrush(self.brush_pending)
        else:
            self.setBrush(self.brush_pending)

        # Update Pen (Start Node)
        if self.is_start_node:
            self.setPen(self.pen_start)
        else:
            self.pen_default.setColor(QColor("#555555")) # Subtle border
            self.pen_default.setWidth(1)
            self.setPen(self.pen_default)

        # Update Text
        display_text = f"{self.attachment_type}: {os.path.basename(self.watch_path)}" if self.watch_path else ""
        self.type_item.setPlainText(display_text)
        
        # Note Visibility
        self.note_item.setVisible(bool(self.notes))

        # --- RICH TOOLTIP REMOVED (Replaced by Popup) ---
        self.setToolTip("") # clear old tooltip logic

    def edit_notes(self):
        text, ok = QInputDialog.getMultiLineText(None, "Edit Notes", "Notes for this node:", self.notes)
        if ok:
            self.notes = text
            self.check_status()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x(),
            "y": self.y(),
            "watch_path": self.watch_path,
            "attachment_type": self.attachment_type,
            "custom_color": self.custom_color,
            "is_completed": self.is_completed,
            "is_start_node": self.is_start_node,
            "notes": self.notes,
            "is_collapsed": self.is_collapsed
        }

# --- 4. The Main Window ---
class SmartWorkflowOrganizer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize Config Manager
        from src.config_manager import ConfigManager
        self.config_manager = ConfigManager()

        self.setWindowTitle("Project Genesis - Workflow Organizer")
        self.resize(1200, 800) 

        # Load Path from Config
        self.save_file_path = self.config_manager.get_data_path()
        self.pipelines_data = {} 
        self.current_pipeline_name = "Default Project"

        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QGraphicsView { background-color: #1e1e1e; border: 1px solid #3e3e42;}
            QLabel { color: #d4d4d4; font-family: 'Segoe UI'; }
            QPushButton { 
                background-color: #007acc; color: white; border: none; 
                padding: 6px 12px; font-size: 13px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #0062a3; }
            QComboBox { 
                background-color: #3e3e42; color: white; padding: 5px; border-radius: 4px; min-width: 150px;
            }
            QMenu { background-color: #252526; color: white; border: 1px solid #3e3e42; }
            QMenu::item:selected { background-color: #007acc; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- Toolbar ---
        toolbar_layout = QHBoxLayout()
        
        self.btn_home = QPushButton("🏠 Menu")
        self.btn_home.setFixedWidth(80)
        self.btn_home.setStyleSheet("background-color: #3e3e42; border: 1px solid #555;")
        self.btn_home.clicked.connect(self.return_to_launcher)
        toolbar_layout.addWidget(self.btn_home)

        # Assistant Button
        self.btn_ai = QPushButton("🤖")
        self.btn_ai.setToolTip("Open Neural Assistant")
        self.btn_ai.setFixedWidth(40)
        self.btn_ai.clicked.connect(self.open_assistant)
        self.btn_ai.setStyleSheet("background-color: #3e3e42; border: 1px solid #555;")
        toolbar_layout.addWidget(self.btn_ai)

        # Global Settings
        self.btn_settings = QPushButton("⚙️ Settings")
        self.btn_settings.clicked.connect(self.open_settings)
        toolbar_layout.addWidget(self.btn_settings)

        toolbar_layout.addSpacing(10)

        lbl_pipe = QLabel("Project:")
        lbl_pipe.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        toolbar_layout.addWidget(lbl_pipe)

        self.combo_pipelines = QComboBox()
        self.combo_pipelines.currentIndexChanged.connect(self.change_pipeline)
        toolbar_layout.addWidget(self.combo_pipelines)

        self.btn_proj_opt = QPushButton("⚙️")
        self.btn_proj_opt.setFixedWidth(40)
        self.btn_proj_opt.clicked.connect(self.show_project_options)
        toolbar_layout.addWidget(self.btn_proj_opt)

        self.btn_new_pipe = QPushButton("+ New")
        self.btn_new_pipe.clicked.connect(self.create_new_pipeline)
        toolbar_layout.addWidget(self.btn_new_pipe)

        toolbar_layout.addSpacing(20)
        self.progress_label = QLabel("0 / 0 Completed")
        self.progress_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        toolbar_layout.addWidget(self.progress_label)

        toolbar_layout.addStretch() 
        
        self.btn_add = QPushButton("+ Add Node")
        self.btn_add.clicked.connect(self.add_new_node_center)
        toolbar_layout.addWidget(self.btn_add)

        self.btn_connect = QPushButton("Connect Selected")
        self.btn_connect.clicked.connect(self.connect_selected_nodes)
        toolbar_layout.addWidget(self.btn_connect)
        
        main_layout.addLayout(toolbar_layout)

        # Scene & Custom View
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 10000, 10000) 
        
        self.view = SmartView(self.scene, self)
        main_layout.addWidget(self.view)

        self.nodes = [] 
        self.lines = []

        self.load_from_disk()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_nodes)
        self.timer.start(2000) 

    # --- NAVIGATION LOGIC ---
    def open_settings(self):
        from src.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            # 1. Reload Path
            new_path = self.config_manager.get_data_path()
            if new_path != self.save_file_path:
                self.save_file_path = new_path
                self.load_from_disk()
                print(f"Reloaded data from: {self.save_file_path}")
            
            # 2. Reload Auto-Save
            interval = self.config_manager.get_auto_save_interval()
            self.timer.setInterval(interval * 1000)
            
            # 3. Apply Theme (Stub for now, but logical place)
            # theme = self.config_manager.get_theme()
            # self.apply_theme(theme)

    def return_to_launcher(self):
        self.save_current_pipeline_to_memory()
        self.save_to_disk()
        try:
            from launcher import GenesisLauncher
            self.launcher = GenesisLauncher()
            self.launcher.show()
            self.close() 
        except ImportError:
            QMessageBox.warning(self, "Navigation Error", "Could not find 'launcher.py'.\nEnsure it is in the same directory.")

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

    # --- FOCUS LOGIC ---
    def focus_camera_on_nodes(self):
        if not self.nodes:
            return
        min_x = min(n.x() for n in self.nodes)
        max_x = max(n.x() + 200 for n in self.nodes)
        min_y = min(n.y() for n in self.nodes)
        max_y = max(n.y() + 80 for n in self.nodes)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        self.view.centerOn(center_x, center_y)

    # --- NODE MANAGEMENT ---
    def delete_node(self, node):
        for line in node.connected_lines:
            if line in self.lines:
                self.scene.removeItem(line)
                self.lines.remove(line)
        if node in self.nodes:
            self.nodes.remove(node)
        self.scene.removeItem(node)
        self.update_progress()

    def update_progress(self):
        total = len(self.nodes)
        completed = sum(1 for n in self.nodes if n.is_completed)
        self.progress_label.setText(f"{completed} / {total} Completed")

    # --- PROJECT MANAGEMENT ---
    def show_project_options(self):
        menu = QMenu()
        act_rename = menu.addAction("Rename Project")
        act_rename.triggered.connect(self.rename_project)
        act_delete = menu.addAction("Delete Project")
        act_delete.triggered.connect(self.delete_project)
        menu.exec(self.btn_proj_opt.mapToGlobal(self.btn_proj_opt.rect().bottomLeft()))

    def rename_project(self):
        old_name = self.current_pipeline_name
        new_name, ok = QInputDialog.getText(self, "Rename Project", "New Name:", text=old_name)
        if ok and new_name and new_name != old_name:
            if new_name in self.pipelines_data:
                QMessageBox.warning(self, "Error", "Name already exists!")
                return
            
            self.save_current_pipeline_to_memory()
            self.pipelines_data[new_name] = self.pipelines_data.pop(old_name)
            self.current_pipeline_name = new_name
            
            self.combo_pipelines.blockSignals(True)
            idx = self.combo_pipelines.findText(old_name)
            self.combo_pipelines.setItemText(idx, new_name)
            self.combo_pipelines.blockSignals(False)

    def delete_project(self):
        if len(self.pipelines_data) <= 1:
            QMessageBox.warning(self, "Error", "Cannot delete the only project.")
            return

        reply = QMessageBox.question(self, "Confirm Delete", 
                                     f"Are you sure you want to delete '{self.current_pipeline_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.pipelines_data[self.current_pipeline_name]
            self.current_pipeline_name = list(self.pipelines_data.keys())[0]
            
            self.combo_pipelines.blockSignals(True)
            self.combo_pipelines.clear()
            self.combo_pipelines.addItems(list(self.pipelines_data.keys()))
            self.combo_pipelines.setCurrentText(self.current_pipeline_name)
            self.combo_pipelines.blockSignals(False)
            
            self.load_pipeline_to_scene(self.current_pipeline_name)

    # --- SAVE / LOAD ---
    def closeEvent(self, event):
        self.save_current_pipeline_to_memory()
        self.save_to_disk()
        super().closeEvent(event)

    def save_current_pipeline_to_memory(self):
        node_data = [n.to_dict() for n in self.nodes]
        edge_data = []
        for line in self.lines:
            if line.start_node in self.nodes and line.end_node in self.nodes:
                edge_data.append({
                    "start": line.start_node.id,
                    "end": line.end_node.id
                })
        
        self.pipelines_data[self.current_pipeline_name] = {
            "nodes": node_data,
            "edges": edge_data
        }

    # --- ATOMIC SAFE SAVE ---
    def save_to_disk(self):
        """Writes to a temporary file first to prevent corruption."""
        temp_file = self.save_file_path + ".tmp"
        try:
            with open(temp_file, 'w') as f:
                json.dump(self.pipelines_data, f, indent=4)
            
            # If successful, replace the old file
            if os.path.exists(self.save_file_path):
                os.remove(self.save_file_path)
            os.rename(temp_file, self.save_file_path)
            print("Saved successfully.")
        except Exception as e:
            print(f"Save Failed: {e}")

    def load_from_disk(self):
        if os.path.exists(self.save_file_path):
            try:
                with open(self.save_file_path, 'r') as f:
                    self.pipelines_data = json.load(f)
            except Exception:
                self.pipelines_data = {"Default Project": {"nodes": [], "edges": []}}
        else:
            self.pipelines_data = {"Default Project": {"nodes": [], "edges": []}}

        self.combo_pipelines.blockSignals(True) 
        self.combo_pipelines.clear()
        self.combo_pipelines.addItems(list(self.pipelines_data.keys()))
        self.combo_pipelines.blockSignals(False)

        if self.pipelines_data:
            self.current_pipeline_name = list(self.pipelines_data.keys())[0]
            self.load_pipeline_to_scene(self.current_pipeline_name)

    def load_pipeline_to_scene(self, pipeline_name):
        self.scene.clear()
        self.nodes = []
        self.lines = []
        
        data = self.pipelines_data.get(pipeline_name, {"nodes": [], "edges": []})
        
        node_map = {} 
        for n_data in data["nodes"]:
            node = SmartNode(n_data["name"], n_data["x"], n_data["y"], self, 
                             watch_path=n_data.get("watch_path"), node_id=n_data.get("id"))
            
            node.attachment_type = n_data.get("attachment_type", "None")
            node.custom_color = n_data.get("custom_color")
            node.is_completed = n_data.get("is_completed", False)
            node.is_start_node = n_data.get("is_start_node", False)
            node.notes = n_data.get("notes", "")
            
            # Checks status (color, icon, etc)
            node.check_status() 
            node.set_text_style(node.is_completed) 
            
            # Apply collapsed state
            if n_data.get("is_collapsed", False):
                node.toggle_collapse()

            self.scene.addItem(node)
            self.nodes.append(node)
            node_map[node.id] = node
            
        for e_data in data["edges"]:
            start = node_map.get(e_data["start"])
            end = node_map.get(e_data["end"])
            if start and end:
                self.create_connection(start, end)
        
        if self.nodes:
            self.focus_camera_on_nodes()
        self.update_progress() 

    def change_pipeline(self, index):
        self.save_current_pipeline_to_memory()
        new_name = self.combo_pipelines.currentText()
        self.current_pipeline_name = new_name
        self.load_pipeline_to_scene(new_name)

    def create_new_pipeline(self):
        name, ok = QInputDialog.getText(self, "New Project", "Project Name:")
        if ok and name:
            if name in self.pipelines_data:
                QMessageBox.warning(self, "Error", "Project already exists!")
                return
            
            self.save_current_pipeline_to_memory()
            self.pipelines_data[name] = {"nodes": [], "edges": []}
            self.combo_pipelines.addItem(name)
            self.combo_pipelines.setCurrentText(name) 

    # --- STANDARD FUNCTIONS ---
    def add_node(self, name, x, y):
        node = SmartNode(name, x, y, self)
        self.scene.addItem(node)
        self.nodes.append(node)
        self.update_progress() # Update bar on add
        return node

    def add_new_node_center(self):
        center = self.view.mapToScene(self.view.viewport().rect().center())
        self.add_node("New Task", center.x() - 100, center.y() - 40)

    def connect_selected_nodes(self):
        selected_items = self.scene.selectedItems()
        selected_nodes = [item for item in selected_items if isinstance(item, SmartNode)]
        if len(selected_nodes) == 2:
            self.create_connection(selected_nodes[0], selected_nodes[1])

    def create_connection(self, start_node, end_node):
        line = ConnectionLine(start_node, end_node)
        self.scene.addItem(line)
        self.lines.append(line)
        start_node.connected_lines.append(line)
        end_node.connected_lines.append(line)

    def update_all_nodes(self):
        for node in self.nodes:
            node.check_status()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartWorkflowOrganizer()
    window.show()
    sys.exit(app.exec())