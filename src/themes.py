
class ThemeManager:
    THEMES = {
        "Dark": {
            "window_bg": "#1e1e1e",
            "text_color": "#d4d4d4",
            "text_dim": "#888888",
            "button_bg": "#252526",
            "button_fg": "white",
            "button_border": "#3e3e42",
            "button_hover": "#007acc",
            "grid_light": "#2d2d30",
            "grid_dark": "#1e1e1e",
            "node_bg": "#3e3e42",
            "node_border_color": "#555555",
            "line_color": "#666666",
            "accent_color": "#007acc",  # Blue
            "selection_color": "#264f78",
            "scrollbar_track": "#2b2b2b",
            "scrollbar_handle": "#424242",
            "window_gradient": "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1e1e1e, stop:1 #323232)"
        },
        "Light": {
            "window_bg": "#f3f3f3",
            "text_color": "#333333",
            "text_dim": "#666666",
            "button_bg": "#ffffff",
            "button_fg": "#333333",
            "button_border": "#cccccc",
            "button_hover": "#007acc",
            "grid_light": "#e0e0e0",
            "grid_dark": "#f3f3f3",
            "node_bg": "#ffffff",
            "node_border_color": "#bbbbbb",
            "line_color": "#999999",
            "accent_color": "#007acc",
            "selection_color": "#add6ff",
            "scrollbar_track": "#f0f0f0",
            "scrollbar_handle": "#cdcdcd",
            "window_gradient": "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #f3f3f3, stop:1 #e6e6e6)"
        },
        "Neon": {
            "window_bg": "#0f0f1a",
            "text_color": "#e0fbff",
            "text_dim": "#5d7a8c",
            "button_bg": "#191929",
            "button_fg": "#00f0ff", # Cyan
            "button_border": "#00f0ff",
            "button_hover": "#b829e0", # Purple accent
            "grid_light": "#1b1b2f",  
            "grid_dark": "#0f0f1a",
            "node_bg": "#191929",
            "node_border_color": "#00f0ff", 
            "line_color": "#b829e0",
            "accent_color": "#00f0ff",
            "selection_color": "#2a2a4e",
            "scrollbar_track": "#050510",
            "scrollbar_handle": "#333366",
            "window_gradient": "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0f0f1a, stop:1 #221c35)" 
        }
    }

    @staticmethod
    def get_theme(theme_name):
        return ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES["Dark"])

    @staticmethod
    def get_stylesheet(theme_name, use_gradient=False):
        t = ThemeManager.get_theme(theme_name)
        
        bg_style = f"background: {t['window_gradient']};" if use_gradient and 'window_gradient' in t else f"background-color: {t['window_bg']};"
        
        # Scrollbar Colors
        sb_track = t.get("scrollbar_track", "#2b2b2b")
        sb_handle = t.get("scrollbar_handle", "#424242")

        base_style = f"""
            QMainWindow, QDialog {{ {bg_style} }} 
            QWidget {{ color: {t['text_color']}; font-family: 'Segoe UI', sans-serif; font-size: 14px; }}
            QGraphicsView {{ background-color: {t['window_bg']}; border: 1px solid {t['button_border']}; }}
            QLabel {{ color: {t['text_color']}; font-family: 'Segoe UI'; background: transparent; }}
            QLineEdit, QSpinBox, QComboBox, QTextEdit, QPlainTextEdit, QListWidget, QTreeWidget, QTableWidget {{ 
                background-color: {t['button_bg']}; 
                color: {t['text_color']}; 
                border: 1px solid {t['button_border']}; 
                selection-background-color: {t['accent_color']};
            }}
            QPushButton {{ 
                background-color: {t['button_bg']}; 
                color: {t['button_fg']}; 
                border: 1px solid {t['button_border']}; 
                padding: 6px 12px; 
                border-radius: 4px;
            }}
            QPushButton:hover {{ 
                background-color: {t['button_hover']}; 
                color: white;
                border: 1px solid {t['accent_color']};
            }}
            QTabWidget::pane {{ border: 1px solid {t['button_border']}; background: transparent; }}
            QTabBar::tab {{
                background: {t['window_bg']}; 
                color: {t['text_color']}; 
                padding: 8px 12px;
                border: 1px solid {t['button_border']}; 
                border-bottom: none;
            }}
            QTabBar::tab:selected {{ 
                background: {t['button_bg']}; 
                color: {t['text_color']};
                border-bottom: 2px solid {t['accent_color']}; 
            }}
            QMenu {{ background-color: {t['button_bg']}; color: {t['text_color']}; border: 1px solid {t['button_border']}; }}
            QMenu::item:selected {{ background-color: {t['accent_color']}; color: white; }}
        """

        scrollbar_style = f"""
            QScrollBar:horizontal {{
                border: none;
                background: {sb_track};
                height: 14px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {sb_handle};
                min-width: 20px;
                border-radius: 7px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                background: none;
                border: none;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {sb_track};
                width: 14px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {sb_handle};
                min-height: 20px;
                border-radius: 7px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
                border: none;
            }}
        """

        return base_style + scrollbar_style
