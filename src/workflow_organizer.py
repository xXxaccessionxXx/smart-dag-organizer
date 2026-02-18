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
                                 QPushButton, QGraphicsItem, QGraphicsRectItem, 
                                 QGraphicsTextItem, QGraphicsLineItem, QGraphicsProxyWidget,
                                 QFrame, QTextEdit, QLineEdit, QComboBox, QMessageBox, 
                                 QFileDialog, QInputDialog, QGraphicsDropShadowEffect, QMenu, QStyle, QColorDialog,
                                 QTabWidget, QListWidget, QListWidgetItem) # Added Tab widgets
    from PyQt6.QtGui import (QColor, QFont, QPen, QBrush, QAction, QDesktopServices, 
                             QPainter, QCursor, QTransform, QLinearGradient, QPainterPath, QIcon)
    from PyQt6.QtCore import (Qt, QTimer, QLineF, QUrl, QPointF, QRectF, QSizeF, 
                              QVariantAnimation, QEasingCurve, QPropertyAnimation, pyqtSignal)
    try:
        from src.utils.assets import resource_path
    except ImportError:
        # Fallback if utils not found (e.g. running from scratch without package context)
        def resource_path(p): return p
except ImportError:
    show_error_and_exit("PyQt6")

from src.utils.status_checker import StatusChecker

# --- 1. Custom Graphics View ---
class SmartView(QGraphicsView):
    def __init__(self, scene, main_window_ref):
        super().__init__(scene)
        self.main_window = main_window_ref 
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag) 
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # NAVIGATION STATE
        self._is_panning = False
        self._pan_start = QPointF(0, 0)
        
        self._current_zoom = 1.0
        self._min_zoom = 0.5  
        self._max_zoom = 2.0 

        self.grid_color_light = QColor("#2d2d30")
        self.grid_color_dark = QColor("#1e1e1e")
        self.setBackgroundBrush(self.grid_color_dark)

    def drawBackground(self, painter, rect):
        # 1. Draw Gradient Background (Fixed to Viewport)
        theme_data = self.main_window.theme_data
        bg_color = QColor(theme_data["window_bg"])
        
        # Save painter state to switch to viewport coordinates
        painter.save()
        painter.resetTransform() # Switch to window coordinates
        
        viewport_rect = self.viewport().rect()
        
        if hasattr(self.main_window.config_manager, "is_gradient_enabled") and self.main_window.config_manager.is_gradient_enabled():
             # Convert to QPointF for Gradient constructor
             gradient = QLinearGradient(QPointF(viewport_rect.topLeft()), QPointF(viewport_rect.bottomRight()))
             gradient.setColorAt(0, bg_color)
             
             # End color
             end_color = QColor(bg_color)
             if end_color.lightness() > 128:
                  end_color = end_color.darker(115) 
             else:
                  end_color = end_color.lighter(115) 
                  
             gradient.setColorAt(1, end_color)
             painter.fillRect(viewport_rect, QBrush(gradient))
        else:
             painter.fillRect(viewport_rect, QBrush(bg_color))
        
        painter.restore() # Restore scene coordinates for grid
        
        # 2. Draw Grid (Scene Coordinates)
        grid_style = self.main_window.config_manager.get_grid_style()
        grid_color = QColor(theme_data["grid_light"])
        grid_color.setAlpha(40) 

        grid_size = 50
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        right = int(rect.right())
        bottom = int(rect.bottom())

        if grid_style == "Dots":
            pen = QPen(grid_color)
            pen.setWidth(2)
            painter.setPen(pen)
            
            for x in range(left, right, grid_size):
                for y in range(top, bottom, grid_size):
                     painter.drawPoint(x, y)
        else:
            # Default Lines
            lines = []
            for x in range(left, right, grid_size):
                lines.append(QLineF(x, rect.top(), x, rect.bottom()))
            
            for y in range(top, bottom, grid_size):
                lines.append(QLineF(rect.left(), y, rect.right(), y))

            pen = QPen(grid_color)
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
        elif event.key() == Qt.Key.Key_Delete:
            self.main_window.delete_selected_items()
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
        # LEFT CLICK -> PAN (ScrollHandDrag)
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if we clicked on an item (node) -> If so, let it handle selection/move
            if self.scene().itemAt(self.mapToScene(event.pos()), QTransform()):
                super().mousePressEvent(event)
                return
            
            # If on empty space, start panning
            self._is_panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()

        # RIGHT CLICK -> SELECT (RubberBandDrag)
        elif event.button() == Qt.MouseButton.RightButton:
            # Check if we clicked on an item -> If so, Context Menu (handled by item)
            item = self.scene().itemAt(self.mapToScene(event.pos()), QTransform())
            if item:
                # Pass to item for context menu
                super().mousePressEvent(event)
                return
            
            # If on empty space, ensure DragMode is RubberBand
            if self.dragMode() != QGraphicsView.DragMode.RubberBandDrag:
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            super().mousePressEvent(event)
        
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
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_panning:
                self._is_panning = False
                self.setCursor(Qt.CursorShape.ArrowCursor)
                event.accept()
            else:
                super().mouseReleaseEvent(event)
        elif event.button() == Qt.MouseButton.RightButton:
             super().mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)
# --- 2. The Connection Line Class ---
class SmartLine(QGraphicsLineItem):
    def __init__(self, start_node, end_node, main_window=None):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.main_window = main_window
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        self.pen_default = QPen(QColor("#666666"))
        self.pen_default.setWidth(2)
        self.pen_default.setStyle(Qt.PenStyle.DashLine) 
        
        self.pen_selected = QPen(QColor("#007acc"))
        self.pen_selected.setWidth(3)
        self.pen_selected.setStyle(Qt.PenStyle.SolidLine)
        
        self.setPen(self.pen_default)
        self.setZValue(-1) 
        
        self.drawing_progress = 1.0 # 0.0 to 1.0
        
        self.update_position()
        
    def set_drawing_progress(self, value):
        self.drawing_progress = value
        self.update()

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            painter.setPen(self.pen_selected)
        else:
            painter.setPen(self.pen_default)
            
        line = self.line()
        if self.drawing_progress < 1.0:
            p1 = line.p1()
            p2 = line.p2()
            # Vector math to find intermediate point
            # QPointF - QPointF = QPointF (vector)
            vec = p2 - p1
            new_p2 = p1 + (vec * self.drawing_progress)
            line = QLineF(p1, new_p2)
            
        painter.drawLine(line)

    def contextMenuEvent(self, event):
        menu = QMenu()
        action_del = menu.addAction("❌ Delete Connection")
        action_del.triggered.connect(self.delete_line)
        menu.exec(event.screenPos())
        
    def delete_line(self):
        if self.main_window:
            self.main_window.remove_line(self)
        elif self.scene():
             self.scene().removeItem(self)


    def update_position(self):
        if not self.start_node.scene() or not self.end_node.scene():
            return

        # Use boundingRect center for dynamic positioning
        start_rect = self.start_node.boundingRect()
        end_rect = self.end_node.boundingRect()
        
        start_center = self.start_node.mapToScene(start_rect.center())
        end_center = self.end_node.mapToScene(end_rect.center())
        
        self.setLine(QLineF(start_center, end_center))

# --- 3a. Note Popup Class ---
class NotePopup(QGraphicsProxyWidget):
    hoverLeave = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setZValue(1000) 
        self.setAcceptHoverEvents(True) 
        
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
            QLineEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3e3e42;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px;
            }
            QPushButton:hover { background-color: #1177bb; }
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #2D2D30;
                color: #888;
                padding: 5px 10px;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                color: white;
                border-bottom: 2px solid #0e639c;
            }
            QListWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: none;
            }
        """)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Header (Common)
        self.lbl_title = QLabel("Node Title")
        self.lbl_title.setStyleSheet("font-weight: bold; font-size: 13px; color: white;")
        main_layout.addWidget(self.lbl_title)
        
        self.lbl_info = QLabel("Type: None")
        self.lbl_info.setStyleSheet("color: #888888; font-size: 10px;")
        main_layout.addWidget(self.lbl_info)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- Tab 1: Notes ---
        self.tab_notes = QWidget()
        notes_layout = QVBoxLayout(self.tab_notes)
        notes_layout.setContentsMargins(5, 5, 5, 5)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(2)
        
        self.btn_bold = QPushButton("B")
        self.btn_bold.setFixedWidth(25)
        self.btn_bold.setStyleSheet("font-weight: bold;")
        self.btn_bold.clicked.connect(self.toggle_bold)
        toolbar_layout.addWidget(self.btn_bold)

        self.btn_italic = QPushButton("I")
        self.btn_italic.setFixedWidth(25)
        self.btn_italic.setStyleSheet("font-style: italic;")
        self.btn_italic.clicked.connect(self.toggle_italic)
        toolbar_layout.addWidget(self.btn_italic)
        
        self.btn_color = QPushButton("🎨")
        self.btn_color.setFixedWidth(25)
        self.btn_color.clicked.connect(self.pick_color)
        toolbar_layout.addWidget(self.btn_color)
        
        toolbar_layout.addStretch()
        notes_layout.addLayout(toolbar_layout)

        # Notes Area
        self.txt_notes = QTextEdit()
        self.txt_notes.setPlaceholderText("Add notes here...")
        self.txt_notes.setMinimumHeight(120)
        self.txt_notes.textChanged.connect(self._on_text_changed)
        notes_layout.addWidget(self.txt_notes)
        
        # Image Preview
        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setVisible(False)
        notes_layout.addWidget(self.lbl_image)

        # Action Buttons
        self.btn_open = QPushButton("🚀 Open Attachment")
        self.btn_open.clicked.connect(self._on_open_clicked)
        self.btn_open.setVisible(False)
        notes_layout.addWidget(self.btn_open)
        
        self.tabs.addTab(self.tab_notes, "Notes")
        
        # --- Tab 2: Calendar ---
        self.tab_calendar = QWidget()
        cal_layout = QVBoxLayout(self.tab_calendar)
        cal_layout.setContentsMargins(5, 5, 5, 5)
        
        self.list_events = QListWidget()
        self.list_events.setAlternatingRowColors(True)
        self.list_events.setEmptyLabel("No upcoming events found.") if hasattr(self.list_events, "setEmptyLabel") else None
        cal_layout.addWidget(self.list_events)
        
        h_cal = QHBoxLayout()
        self.btn_refresh_cal = QPushButton("🔄 Refresh")
        self.btn_refresh_cal.clicked.connect(self.refresh_calendar_events)
        h_cal.addWidget(self.btn_refresh_cal)
        
        self.btn_add_event = QPushButton("➕ Add Event")
        self.btn_add_event.clicked.connect(self.open_add_event_dialog)
        h_cal.addWidget(self.btn_add_event)
        
        cal_layout.addLayout(h_cal)
        
        self.tabs.addTab(self.tab_calendar, "Calendar")

        self.setWidget(self.container)
        self.setVisible(False)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.updating = False

    def refresh_calendar_events(self):
        self.list_events.clear()
        
        # Access Integration Manager through parent chain
        try:
            # NotePopup -> SmartNode -> SmartView (via scene?) -> SmartWorkflowOrganizer
            # Actually SmartNode stores self.mainWindow
            node = self.parentItem()
            if not node: return
            
            manager = node.main_window.integration_manager
            calendar_int = manager.get_integration("google_calendar")
            
            if not calendar_int or not calendar_int.is_configured():
                self.list_events.addItem("Google Calendar not configured.")
                return
                
            events = calendar_int.list_upcoming_events()
            if not events:
                self.list_events.addItem("No upcoming events.")
                return
                
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', '(No Title)')
                
                # Format start time string for display (simple slice)
                if 'T' in start:
                    display_time = start.split('T')[1][:5] + " " + start.split('T')[0]
                else:
                    display_time = start # All day
                
                item = QListWidgetItem(f"📅 {display_time} - {summary}")
                self.list_events.addItem(item)
                
        except Exception as e:
            self.list_events.addItem(f"Error: {str(e)}")

    def open_add_event_dialog(self):
        node = self.parentItem()
        if not node: return
        
        manager = node.main_window.integration_manager
        calendar_int = manager.get_integration("google_calendar")
        
        if calendar_int:
            calendar_int.action_create_custom_event(node)
            self.refresh_calendar_events() # Refresh after creation

    def update_content(self, title, type_str, path, notes):
        self.updating = True # Block signal loop
        
        self.lbl_title.setText(title)
        
        info_text = f"Type: {type_str}"
        if path:
            info_text += f"\nPath: {path}"
        self.lbl_info.setText(info_text)
        
        self.txt_notes.setHtml(notes)
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
             self.parentItem().update_notes_from_popup(self.txt_notes.toHtml())

    def _on_open_clicked(self):
        if self.parentItem():
             self.parentItem().open_attachment()

    def toggle_bold(self):
        fmt = self.txt_notes.currentCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if fmt.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal)
        self.txt_notes.mergeCurrentCharFormat(fmt)
        
    def toggle_italic(self):
        fmt = self.txt_notes.currentCharFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        self.txt_notes.mergeCurrentCharFormat(fmt)

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            fmt = self.txt_notes.currentCharFormat()
            fmt.setForeground(color)
            self.txt_notes.mergeCurrentCharFormat(fmt)


    def hoverEnterEvent(self, event):
        if self.parentItem():
            self.parentItem().stop_hide_timer()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if self.parentItem():
             self.parentItem().start_hide_timer()
        super().hoverLeaveEvent(event)
        self.hoverLeave.emit()



# --- 3b. Modern Text Item (No Dashed Outline) ---
class ModernTextItem(QGraphicsTextItem):
    def paint(self, painter, option, widget=None):
        # Remove the dashed focus border
        option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, widget)

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

        # Drop Shadow for Depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(4, 4)
        self.setGraphicsEffect(shadow)

        self.file_exists = False # Cache for file status


        # Theme Colors
        theme = self.main_window.theme_data
        
        # Default Pens
        self.pen_default = QPen(Qt.PenStyle.NoPen)
        # Start Node Pen
        self.pen_start = QPen(QColor("#FFD700")) 
        self.pen_start.setWidth(3)

        self.brush_pending = QBrush(QColor(theme["node_bg"])) 
        self.brush_done = QBrush(QColor("#2da44e")) # Keep semantic green for Done? Or theme? theme["accent_color"]? Green is standard for "Success".
        self.brush_link = QBrush(QColor(theme["accent_color"]))   
        self.brush_disabled = QBrush(QColor(theme["window_bg"])) 
        
        self.setBrush(self.brush_pending)
        self.setPen(self.pen_default)

        self.setPen(self.pen_default)

        # Title
        self.text_item = ModernTextItem(name, self)
        self.set_text_style(completed=False)
        self.text_item.setPos(10, 2) # Centered vertically in 30px header
        self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.text_item.document().contentsChanged.connect(self.update_name_from_text)

        # Type Indicator
        self.type_item = QGraphicsTextItem("", self)
        self.type_item.setDefaultTextColor(QColor(theme["text_dim"]))
        self.type_item.setFont(QFont("Segoe UI", 8))
        self.type_item.setPos(10, 45)

        # Note Indicator
        self.note_item = QGraphicsTextItem("📝", self)
        self.note_item.setDefaultTextColor(QColor("#ffd700"))
        self.note_item.setPos(165, 5) 
        self.note_item.setVisible(False)
        
        # Pop In Animation
        self.setTransformOriginPoint(100, 40) # Center of 200x80 node
        self.setScale(0.1)
        
        self.pop_anim = QVariantAnimation()
        self.pop_anim.setDuration(500)
        self.pop_anim.setStartValue(0.1)
        self.pop_anim.setEndValue(1.0)
        self.pop_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.pop_anim.valueChanged.connect(self.setScale)
        self.pop_anim.start()

        # Collapse Button
        self.collapse_btn = QGraphicsTextItem("−", self)
        # Use theme color if available, else standard
        btn_color = theme["text_dim"] if "text_dim" in theme else "#cccccc"
        self.collapse_btn.setDefaultTextColor(QColor(btn_color))
        self.collapse_btn.setFont(QFont("Arial", 14))
        
        # Initial sizing
        self.adjust_size()
        
        # Hover Support
        self.setAcceptHoverEvents(True)
        self.popup = NotePopup(self)
        self.popup.setVisible(False) 
        
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_popup)
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            # 1. Hide popup on drag
            if self.popup.isVisible():
                self.popup.setVisible(False)
            
            # 2. Magnetic Snapping
            new_pos = value
            x, y = new_pos.x(), new_pos.y()
            
            # Snap thresholds
            SNAP_DIST = 20
            snap_x, snap_y = x, y
            
            # Only snap if moving by mouse (optimization?) - strict check might be complex, verify simply first.
            if self.isSelected():
                for item in self.scene().items():
                    if item == self or not isinstance(item, SmartNode):
                        continue
                    
                    # Get other node pos
                    ox, oy = item.pos().x(), item.pos().y()
                    
                    # Snap X (Align Left)
                    if abs(x - ox) < SNAP_DIST:
                        snap_x = ox
                        
                    # Snap Y (Align Top)
                    if abs(y - oy) < SNAP_DIST:
                        snap_y = oy
            
            return QPointF(snap_x, snap_y)
            
        return super().itemChange(change, value)

    def adjust_size(self):
        # Calculate required width based on title
        text_width = self.text_item.boundingRect().width()
        new_width = max(200, text_width + 45) # 200 min width, 45 padding for buttons
        
        # Update Node Rect (Keep height 80)
        self.setRect(0, 0, new_width, 80)
        
        # Reposition Elements
        self.collapse_btn.setPos(new_width - 25, -2)
        self.note_item.setPos(new_width - 35, 5)
        
        # Update Pivot (Center)
        self.setTransformOriginPoint(new_width / 2, 40)

        # Update Pivot (Center)
        self.setTransformOriginPoint(new_width / 2, 40)

    def paint(self, painter, option, widget=None):
        # Custom Painting for Modern Look
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 10, 10)
        
        # Shadow / Glow
        if self.isSelected():
            painter.setPen(QPen(QColor("#007acc"), 3))
        else:
            painter.setPen(self.pen_default)
            
        # Background
        painter.fillPath(path, self.brush())
        
        # Header Strip
        # Draw a translucent overlay for the header area
        header_height = 30
        # Header Strip
        # Draw a translucent overlay for the header area
        header_height = 30
        header_rect = QRectF(0, 0, self.rect().width(), header_height)
        header_brush = QBrush(QColor(0, 0, 0, 40)) # 40/255 opacity black
        
        painter.save()
        painter.setClipPath(path) # Clip to rounded node shape
        painter.fillRect(header_rect, header_brush)
        
        # Draw status stripe if start node
        if self.is_start_node:
            painter.fillRect(QRectF(0, 0, 5, self.rect().height()), QColor("#FFD700"))
            
        painter.restore()
        
        # Draw Border
        painter.drawPath(path)

    def hoverEnterEvent(self, event):
        self.stop_hide_timer()
        # Update Popup Data
        self.popup.update_content(self.name, self.attachment_type, self.watch_path, self.notes)
        
        # Smart Positioning (Avoid Overlap)
        margin = 10
        node_w = self.rect().width()
        node_h = self.rect().height()
        pop_w = self.popup.boundingRect().width()
        pop_h = self.popup.boundingRect().height()
        
        # Candidate positions (local coords relative to Node)
        # 1. Right, 2. Left, 3. Bottom, 4. Top
        candidates = [
            QPointF(node_w + margin, 0),                  # Right
            QPointF(-pop_w - margin, 0),                 # Left
            QPointF(0, node_h + margin),                 # Bottom
            QPointF(0, -pop_h - margin)                  # Top
        ]
        
        best_pos = candidates[0] # Default to Right
        
        if self.scene():
            for pos in candidates:
                # Create a test rect in local coords
                test_rect = QRectF(pos.x(), pos.y(), pop_w, pop_h)
                # Map to scene to check collisions
                scene_rect = self.mapRectToScene(test_rect)
                
                # Check if this area hits any OTHER SmartNode
                # (items() returns all items in rect)
                items_in_rect = self.scene().items(scene_rect)
                collision = False
                for item in items_in_rect:
                    if isinstance(item, SmartNode) and item != self:
                        collision = True
                        break
                
                if not collision:
                    best_pos = pos
                    break # Found a clear spot!

        self.popup.setPos(best_pos)
        self.popup.setVisible(True)
        self.setZValue(100) # Raise on hover
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.start_hide_timer()
        super().hoverLeaveEvent(event)
        
    def start_hide_timer(self):
        from src.config_manager import ConfigManager
        # Access static method, which returns instance
        cfg = ConfigManager._get_shared_instance()
        if cfg.get_hover_persistence():
            self.hide_timer.start(50) 
        else:
            self.hide_timer.start(0)

    def stop_hide_timer(self):
        self.hide_timer.stop()

    def hide_popup(self):
        self.popup.setVisible(False)
        self.setZValue(0) # Reset Z-Index

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
            # Hide popup immediately on interaction/drag start
            self.stop_hide_timer()
            self.popup.setVisible(False)
            super().mousePressEvent(event)

    def set_text_style(self, completed=False):
        font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        theme = self.main_window.theme_data
        if completed:
            font.setStrikeOut(True)
            self.text_item.setDefaultTextColor(QColor(theme["text_dim"]))
        else:
            font.setStrikeOut(False)
            self.text_item.setDefaultTextColor(QColor(theme["text_color"]))
        self.text_item.setFont(font)

    def update_name_from_text(self):
        self.name = self.text_item.toPlainText()
        self.adjust_size()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        
        # Smart Linking (Drop-to-Connect)
        # Check for collision with other nodes (Overlap)
        colliding_items = self.scene().collidingItems(self, Qt.ItemSelectionMode.IntersectsItemShape)
        
        target_node = None
        # Find the first valid SmartNode that isn't self
        for item in colliding_items:
            if isinstance(item, SmartNode) and item != self:
                target_node = item
                break
        
        if target_node:
            # Found a target (Parent)! 
            # Drop 'self' (Child) onto 'target_node' (Parent) -> Parent takes Child.
            if hasattr(self.main_window, "auto_connect_nodes"):
                # Connection: Target -> Self (Parent -> Child)
                new_line = self.main_window.auto_connect_nodes(target_node, self)
                
                # If connected successfully, Collapse the parent to "take in" the child?
                # User said: "parent node take in the child node by collapsing"
                if new_line:
                     if not target_node.is_collapsed:
                         target_node.toggle_collapse() # This will hide the new child (self)
                     else:
                         # Parent is ALREADY collapsed.
                         # We imply that 'self' (the child) should now disappear into it.
                         # Since it's a child of a collapsed node, it should be hidden.
                         self.setVisible(False)
                         self.popup.setVisible(False) 
                         # ALSO HIDE THE LINE!
                         new_line.setVisible(False)



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

        if not self.is_completed:
            # Integrations Submenu
            integrations_menu = menu.addMenu("🔌 Integrations")
            
            # Google Calendar
            cal_integration = self.main_window.integration_manager.get_integration("google_calendar")
            if cal_integration:
                cal_menu = integrations_menu.addMenu("Google Calendar")
                
                # Dynamic Actions from Integration
                for action_data in cal_integration.get_actions():
                    action = cal_menu.addAction(action_data["label"])
                    # Use default argument to capture current loop variable
                    action.triggered.connect(lambda checked, cb=action_data["callback"]: cb(self))

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
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            new_pos = value
            # Magnetic Snapping
            # Snap to grid or other nodes? Let's snap to other nodes (alignment)
            snap_distance = 15
            x_snap = new_pos.x()
            y_snap = new_pos.y()
            
            # Simple Grid Snap (if no other nodes close? or always?)
            # Let's do Node-to-Node alignment
            nearby_items = self.scene().items(QRectF(x_snap - 50, y_snap - 50, 300, 180)) # Search area
            
            sh = self.boundingRect().height()
            sw = self.boundingRect().width()
            
            for item in nearby_items:
                if isinstance(item, SmartNode) and item != self:
                    # Align Left
                    if abs(item.x() - x_snap) < snap_distance:
                        x_snap = item.x()
                    # Align Top
                    if abs(item.y() - y_snap) < snap_distance:
                         y_snap = item.y()
                    # Align Center X
                    if abs((item.x() + item.boundingRect().width()/2) - (x_snap + sw/2)) < snap_distance:
                         x_snap = item.x() + item.boundingRect().width()/2 - sw/2
                         
            new_pos.setX(x_snap)
            new_pos.setY(y_snap)
            
            # Update connected lines with snapped pos
            # We must use new_pos because 'value' is what will be set
            # But update_position uses self.pos() which isn't updated yet?
            # Actually, standard practice is to return the modified value.
            # The Lines will update in ItemPositionHasChanged or we just trigger it here but it might lag one frame.
            # Best to let scene handle line updates or call it after safely.
            # But here we just modify the return.
            
            value = new_pos

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
             for line in self.connected_lines:
                line.update_position()

        return super().itemChange(change, value)

    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            self.collapse_btn.setPlainText("+")
            # Animate Collapse
            self.animate_children_visibility(False)
        else:
            self.collapse_btn.setPlainText("−")
            # Smart Layout before showing
            self.smart_layout_children()
            # Animate Expand
            self.animate_children_visibility(True)
        
        self.update()

    def smart_layout_children(self):
        """Adjusts children positions to avoid collisions before expanding."""
        # Get direct children
        children = []
        for line in self.connected_lines:
            if line.start_node == self:
                children.append(line.end_node)
        
        if not children:
            return

        # Check for collisions and find new spots
        scene = self.scene()
        for child in children:
            # If child is accidentally on top of parent (e.g. just created), move it
            if self.collidesWithItem(child):
                 child.setPos(self.x() + 250, self.y())

            # Check collision with OTHERS
            # Simple spiral search or shift down
            original_pos = child.pos()
            target_pos = original_pos
            
            # Safety break
            attempts = 0
            while True:
                # Check collision at target_pos
                rect = child.rect()
                # fast check: map rect to scene at target_pos
                scene_rect = QRectF(target_pos.x(), target_pos.y(), rect.width(), rect.height())
                
                items = scene.items(scene_rect)
                collision = False
                for item in items:
                    if isinstance(item, SmartNode) and item != child and item != self:
                        # We collide with another node
                        # Is it a child of ours? Ignoring siblings for now might be okay, 
                        # but ideally we avoid them too. 
                        # For simple fix: avoid ANY SmartNode that isn't self or child itself.
                        collision = True
                        break
                
                if not collision:
                    break
                
                # Move down
                target_pos.setY(target_pos.y() + 100)
                attempts += 1
                if attempts > 20: break # Give up
            
            if target_pos != original_pos:
                child.setPos(target_pos)
                # print(f"Moved child {child.name} to avoid collision.")

    def animate_children_visibility(self, visible):
        """Recursively animate opacity for downstream nodes."""
        self.set_visibility_recursive_animated(visible)

    def set_visibility_recursive_animated(self, visible):
        for line in self.connected_lines:
            if line.start_node == self:
                child = line.end_node
                
                if visible:
                    # --- EXPAND SEQUENCE ---
                    # 1. Setup Initial State (Hidden but Present)
                    line.setVisible(True)
                    child.setVisible(True)
                    line.set_drawing_progress(0.0)
                    child.setOpacity(0.0)
                    
                    # 2. Animate Line Growth
                    anim_line = QVariantAnimation()
                    anim_line.setStartValue(0.0)
                    anim_line.setEndValue(1.0)
                    anim_line.setDuration(250) # Fast line
                    anim_line.setEasingCurve(QEasingCurve.Type.OutQuad)
                    anim_line.valueChanged.connect(line.set_drawing_progress)
                    
                    # 3. On Line Finish -> Fade In Node
                    def on_line_finished(captured_child=child):
                        # Fade In + Scale Up (Pop effect)
                        self.animate_node_appearance(captured_child)
                        
                        # CAUTION: If we recurse here, it creates a "wave"
                        if not captured_child.is_collapsed:
                            captured_child.set_visibility_recursive_animated(True)

                    anim_line.finished.connect(on_line_finished)
                    anim_line.start()
                    line._anim = anim_line # Keep reference
                    
                else:
                    # --- COLLAPSE SEQUENCE ---
                    # 1. Fade Out Node
                    def on_node_faded(captured_line=line, captured_child=child):
                        # 2. Retract Line
                        anim_line = QVariantAnimation()
                        anim_line.setStartValue(1.0)
                        anim_line.setEndValue(0.0)
                        anim_line.setDuration(200)
                        anim_line.setEasingCurve(QEasingCurve.Type.InQuad)
                        anim_line.valueChanged.connect(captured_line.set_drawing_progress)
                        
                        def on_line_retracted():
                            captured_line.setVisible(False)
                            captured_child.setVisible(False)
                            
                        anim_line.finished.connect(on_line_retracted)
                        anim_line.start()
                        captured_line._anim = anim_line

                    # Animate Out (Scale Down + Fade)
                    self.animate_node_disappearance(child, callback=on_node_faded)
                    
                    if not child.is_collapsed:
                         child.set_visibility_recursive_animated(False)

    def animate_node_appearance(self, node):
        node.setTransformOriginPoint(node.boundingRect().center())
        
        # We need to store animation ref
        anim = QVariantAnimation() 
        node._appear_anim = anim
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.Type.OutBack) # Slight overshoot for "pop"
        
        def update_props(val):
            node.setOpacity(val)
            node.setScale(val)
            
        anim.valueChanged.connect(update_props)
        anim.start()

    def animate_node_disappearance(self, node, callback=None):
        node.setTransformOriginPoint(node.boundingRect().center())
        
        anim = QVariantAnimation() 
        node._disappear_anim = anim
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setDuration(250)
        anim.setEasingCurve(QEasingCurve.Type.InBack)
        
        def update_props(val):
            node.setOpacity(val)
            node.setScale(val)
            
        anim.valueChanged.connect(update_props)
        if callback:
            anim.finished.connect(callback)
        anim.start()

    def fade_node(self, node, start, end, callback=None):
        # Legacy fade, keeping for generic use if needed
        anim = QVariantAnimation() 
        node._fade_anim = anim
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim.valueChanged.connect(node.setOpacity)
        
        if callback:
             anim.finished.connect(callback)
             
        anim.start()

    def check_status(self):
        # Update Color
        if self.is_completed:
            self.setBrush(self.brush_done)
        elif self.custom_color:
             self.setBrush(QBrush(QColor(self.custom_color)))
        elif self.watch_path:
            if self.attachment_type == "Link":
                self.setBrush(self.brush_link)
            elif self.file_exists: # Use cached status
                self.setBrush(self.brush_done)
            else:
                 self.setBrush(self.brush_pending)
        else:
            self.setBrush(self.brush_pending)

        # Update Pen (Start Node)
        if self.is_start_node:
            self.setPen(self.pen_start)
        else:
            # Use theme color for border
            self.pen_default.setColor(QColor(self.main_window.theme_data["node_border_color"])) 
            self.pen_default.setWidth(1)
            self.setPen(self.pen_default)

        # Update Text
        # Update Text
        display_text = ""
        if self.watch_path:
            if self.attachment_type == "Link" and "google.com/calendar/event" in self.watch_path:
                display_text = "📅 Google Event"
            else:
                display_text = f"{self.attachment_type}: {os.path.basename(self.watch_path)}"
        
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

        # Set Window Icon
        try:
            icon_path = resource_path("assets/icon.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass

        # Initialize Config Manager
        from src.config_manager import ConfigManager
        self.config_manager = ConfigManager()

        self.setWindowTitle("Project Genesis - Workflow Organizer")
        self.resize(1200, 800) 
        
        # Restore Window State
        saved_geometry = self.config_manager.get_window_geometry()
        if saved_geometry:
            try:
                self.restoreGeometry(bytes.fromhex(saved_geometry))
            except Exception:
                pass # Invalid geometry data 

        # Load Path from Config
        self.save_file_path = self.config_manager.get_data_path()
        self.pipelines_data = {} 
        self.current_pipeline_name = "Default Project"
        
        # Load Theme
        self.theme_data = self.config_manager.get_theme_data()
        from src.themes import ThemeManager
        use_gradient = self.config_manager.is_gradient_enabled()
        self.setStyleSheet(ThemeManager.get_stylesheet(self.config_manager.get_theme(), use_gradient))

        # --- Integrations ---
        from src.integrations.manager import IntegrationManager
        from src.integrations.google_calendar import GoogleCalendarIntegration
        self.integration_manager = IntegrationManager(self)
        self.integration_manager.register_integration(GoogleCalendarIntegration)


        # Inline overrides for specific needs if any, utilizing theme variables would be better but stylesheet handles most.
        # However, QGraphicsView bg is handled by stylesheet now in ThemeManager.


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
        
        self.animate_fade_in()

        # First Run Check
        QTimer.singleShot(100, self.check_first_run)
        
        # Status Checker Thread
        self.status_checker = StatusChecker()
        self.status_checker.results_ready.connect(self.apply_status_updates)
        self.status_checker.start()
        
        # Register Crash Callback (specific to this window instance)
        from src.utils.logger import CrashHandler
        CrashHandler.register_save_callback(self.emergency_save)

    def emergency_save(self):
        """Called by CrashHandler."""
        try:
            self.save_current_pipeline_to_memory()
            self.save_to_disk()
        except:
            pass

    def check_first_run(self):
        """Checks if there are no pipelines and prompts for a project name."""
        if len(self.pipelines_data) <= 1 and not self.pipelines_data.get("Default Project", {}).get("nodes"):
             # It seems empty, or just default.
             # Let's check if we just loaded the default empty one.
             if list(self.pipelines_data.keys()) == ["Default Project"]:
                 self.prompt_initial_project_name()

    def prompt_initial_project_name(self):
        name, ok = QInputDialog.getText(self, "Welcome!", "Let's name your first project:")
        if ok and name:
            # Rename Default Project
            self.pipelines_data[name] = self.pipelines_data.pop("Default Project")
            self.current_pipeline_name = name
            
            self.combo_pipelines.blockSignals(True)
            self.combo_pipelines.clear()
            self.combo_pipelines.addItem(name)
            self.combo_pipelines.setCurrentText(name)
            self.combo_pipelines.blockSignals(False)
            
            self.save_to_disk()

    # --- SAVE HELPER ---
    def trigger_autosave(self):
        """Autosaves if interval or critical action."""
        # For now, we save on every structural change as requested by 'unwanted loss' fear, 
        # but locally (to memory/disk).
        self.save_current_pipeline_to_memory()
        self.save_to_disk()

    def animate_fade_in(self):
        try:
            from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
            from PyQt6.QtWidgets import QGraphicsOpacityEffect
            self.opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self.opacity_effect)
            
            self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.anim.setDuration(800)
            self.anim.setStartValue(0)
            self.anim.setEndValue(1)
            self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.anim.start()
        except ImportError:
            pass 

    # --- NAVIGATION LOGIC ---
    def open_settings(self):
        try:
            from src.settings_dialog import SettingsDialog
            dlg = SettingsDialog(self.config_manager, self, apply_callback=self.apply_theme)
            if dlg.exec():
                # Reload settings if saved (redundant if using live preview, but good practice)
                self.apply_theme()
                self.update_grid_color() # Grid might change
        except Exception as e:
            QMessageBox.critical(self, "Settings Error", f"Could not open settings:\n{e}")
            import traceback
            traceback.print_exc() # Print to console for debugging

    def apply_theme(self):
        """Reloads the theme from config."""
        from src.themes import ThemeManager
        theme = self.config_manager.get_theme()
        use_gradient = self.config_manager.is_gradient_enabled()
        self.setStyleSheet(ThemeManager.get_stylesheet(theme, use_gradient))
        
        # Grid color might change
        self.update_grid_color()
        
        # Redraw nodes to update borders
        for item in self.scene.items():
            if hasattr(item, "update_style"):
                item.update_style()
                
        # Apply Globally to ensure Scrollbars (and everything else) get styled
        app = QApplication.instance()
        if app:
            app.setStyle("Fusion")
            stylesheet = ThemeManager.get_stylesheet(theme, use_gradient)
            app.setStyleSheet(stylesheet)
            
            # Also apply to self to be safe
            self.setStyleSheet(stylesheet)

    def update_grid_color(self):
        """Forces a repaint of the graphics view to update the grid."""
        self.view.viewport().update()

    def return_to_launcher(self):
        self.save_current_pipeline_to_memory()
        self.save_to_disk()
        
        # Save Window State
        if self.normalGeometry().isValid(): # Don't save if minimized/maximized weirdness
             self.config_manager.set_window_geometry(self.saveGeometry().toHex().data().decode())

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

    def closeEvent(self, event):
        # Save Data
        self.save_current_pipeline_to_memory()
        self.save_to_disk()

        # Save Window State on Close
        if self.normalGeometry().isValid():
             self.config_manager.set_window_geometry(self.saveGeometry().toHex().data().decode())
             
        super().closeEvent(event)

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
        
        menu.addSeparator()
        
        act_export = menu.addAction("Export Project (JSON)")
        act_export.triggered.connect(self.export_project)
        
        act_import = menu.addAction("Import Project (JSON)")
        act_import.triggered.connect(self.import_project)
        
        menu.exec(self.btn_proj_opt.mapToGlobal(self.btn_proj_opt.rect().bottomLeft()))

    def export_project(self):
        """Exports the current project to a JSON file."""
        self.save_current_pipeline_to_memory()
        data = self.pipelines_data.get(self.current_pipeline_name, {})
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Project", 
            f"{self.current_pipeline_name}.json", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                QMessageBox.information(self, "Success", f"Project exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Could not save file:\n{e}")

    def import_project(self):
        """Imports a project from a JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Project", 
            "", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Basic Validation
                if "nodes" not in data or "edges" not in data:
                    QMessageBox.warning(self, "Invalid File", "This JSON does not look like a valid project file.")
                    return

                # Determine New Name
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                new_name = base_name
                counter = 1
                while new_name in self.pipelines_data:
                    new_name = f"{base_name} ({counter})"
                    counter += 1
                
                # Add to Pipelines
                self.pipelines_data[new_name] = data
                
                # Update UI
                self.combo_pipelines.addItem(new_name)
                self.combo_pipelines.setCurrentText(new_name)
                
                QMessageBox.information(self, "Success", f"Project imported as '{new_name}'")
                
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", f"Could not load file:\n{e}")

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
        try:
            center = self.view.mapToScene(self.view.viewport().rect().center())
            self.add_node("New Task", center.x() - 100, center.y() - 40)
            self.trigger_autosave()
        except Exception as e:
            print(f"Error adding node: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Could not create node: {e}")

    def connect_selected_nodes(self):
        selected_items = self.scene.selectedItems()
        selected_nodes = [item for item in selected_items if isinstance(item, SmartNode)]
        if len(selected_nodes) == 2:
            self.create_connection(selected_nodes[0], selected_nodes[1])

    def auto_connect_nodes(self, start_node, end_node):
        # Auto-connect logic (Drop-to-Connect)
        # Returns the created line if connection created, None otherwise
        line = self.create_connection(start_node, end_node)
        if line:
            print(f"Auto-connected {start_node.name} -> {end_node.name}")
            return line
        return None

    def create_connection(self, start, end):
        # Prevent self-loops
        if start == end:
            return None

        # Check duplicates
        for line in self.lines:
            if line.start_node == start and line.end_node == end:
                return None
            if line.start_node == end and line.end_node == start:
                return None 

        # Create Line
        line = SmartLine(start, end, self)
        self.scene.addItem(line)
        self.lines.append(line)
        
        start.connected_lines.append(line)
        end.connected_lines.append(line)
        
        # Send behind nodes
        line.setZValue(-1) 
        
        self.trigger_autosave()
        return line

    def delete_node(self, node):
        # Remove connections first
        for line in list(node.connected_lines):
            self.remove_line(line)
        
        self.scene.removeItem(node)
        if node in self.nodes:
            self.nodes.remove(node)
        self.update_progress()
        self.trigger_autosave()

    def remove_line(self, line):
        if line in self.lines:
             self.lines.remove(line)
        self.scene.removeItem(line)
        # Update nodes
        if line.start_node and line in line.start_node.connected_lines:
            line.start_node.connected_lines.remove(line)
        if line.end_node and line in line.end_node.connected_lines:
            line.end_node.connected_lines.remove(line)
        self.trigger_autosave()

    def delete_selected_items(self):
        selected = self.scene.selectedItems()
        for item in selected:
            if isinstance(item, SmartLine):
                self.remove_line(item)
            elif isinstance(item, SmartNode):
                self.delete_node(item)

    def update_all_nodes(self):
        paths = []
        for node in self.nodes:
            node.check_status()
            if node.watch_path:
                paths.append(node.watch_path)
        
        # Update checker paths
        if self.status_checker.isRunning():
            self.status_checker.set_paths(paths)

    def apply_status_updates(self, results):
        """Update nodes with results from background thread."""
        for node in self.nodes:
            if node.watch_path and node.watch_path in results:
                node.file_exists = results[node.watch_path]
                node.check_status() # Refresh visual
    
    def closeEvent(self, event):
        self.status_checker.stop()
        super().closeEvent(event)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SmartWorkflowOrganizer()
    window.show()
    sys.exit(app.exec())