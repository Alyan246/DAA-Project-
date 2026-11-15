"""Shared pieces: PySide6 bootstrap, algorithm loader, theme, base widgets."""
import os
import sys
import subprocess
import importlib.util

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
from Generate_inputs import generate_closestpair_dataset
from Generate_inputs import generate_karatsuba_dataset

try:
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QFileDialog, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton,
        QVBoxLayout, QWidget,
    )
except ImportError:
    print("PySide6 not found. Installing it (one time only)...")
    cmd = [sys.executable, "-m", "pip", "install", "--user", "PySide6"]
    if subprocess.call(cmd) != 0:
        subprocess.check_call(cmd + ["--break-system-packages"])
    os.execv(sys.executable, [sys.executable] + sys.argv)

def load_module(file_name):
    for folder in ("algorithms", "algorithms "):
        path = os.path.join(BASE_DIR, folder, file_name)
        if os.path.isfile(path):
            spec = importlib.util.spec_from_file_location(file_name[:-3], path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise FileNotFoundError(f"Could not find algorithms/{file_name} next to Gui.py")


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
BG, PANEL, BORDER = "#0f172a", "#1e293b", "#334155"
TEXT, MUTED = "#e2e8f0", "#94a3b8"
BLUE, VIOLET, AMBER, RED, GREEN = "#38bdf8", "#a78bfa", "#fbbf24", "#f43f5e", "#4ade80"

STYLE = f"""
QWidget {{ background: {BG}; color: {TEXT}; font-size: 14px; }}
QLabel#title {{ font-size: 30px; font-weight: bold; letter-spacing: 2px; }}
QLabel#hero {{ font-size: 44px; font-weight: bold; letter-spacing: 6px; }}
QLabel#sub {{ font-size: 16px; color: {MUTED}; letter-spacing: 8px; }}
QLabel#muted {{ color: {MUTED}; }}
QPushButton {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 8px;
               padding: 8px 16px; }}
QPushButton:hover {{ border-color: {BLUE}; }}
QPushButton#primary {{ background: {BLUE}; color: #0f172a; font-weight: bold; border: none; }}
QPushButton#primary:hover {{ background: #7dd3fc; }}
QPushButton#card {{ font-size: 22px; font-weight: bold; padding: 30px; min-width: 300px;
                    min-height: 150px; border-radius: 16px; border: 2px solid {BORDER}; }}
QPushButton#card:hover {{ border-color: {BLUE}; background: #243349; }}
QFrame#stat {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 10px; }}
QFrame#stat QLabel {{ background: transparent; }}
QPlainTextEdit, QTreeWidget, QListWidget {{ background: #0b1220; border: 1px solid {BORDER};
               border-radius: 8px; padding: 6px; }}
QListWidget::item {{ padding: 4px; }}
QListWidget::item:selected, QTreeWidget::item:selected {{ background: #1d4ed8; color: white; }}
QHeaderView::section {{ background: {PANEL}; color: {MUTED}; border: none; padding: 4px; }}
QSplitter::handle {{ background: {BORDER}; }}
"""

MONO = QFont("Monospace", 10)
MONO.setStyleHint(QFont.Monospace)


def short(n, keep=10):
    s = str(n)
    if len(s) <= 2 * keep + 6:
        return s
    return f"{s[:keep]}…{s[-keep:]} ({len(s)}d)"


class StatCard(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setObjectName("stat")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(2)
        t = QLabel(title)
        t.setObjectName("muted")
        self.value = QLabel("-")
        self.value.setStyleSheet("font-size: 18px; font-weight: bold;")
        lay.addWidget(t)
        lay.addWidget(self.value)

    def set(self, text, color=None):
        self.value.setText(text)
        self.value.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {color or TEXT};")


class AlgoPage(QWidget):
    """Common header (back button, title) and file bar for both algorithm pages."""

    def __init__(self, title, go_home, dataset_folder):
        super().__init__()
        self.dataset_folder = dataset_folder
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(20, 16, 20, 16)
        self.root.setSpacing(12)

        head = QHBoxLayout()
        back = QPushButton("←  Back")
        back.clicked.connect(go_home)
        label = QLabel(title)
        label.setObjectName("title")
        head.addWidget(back)
        head.addSpacing(16)
        head.addWidget(label)
        head.addStretch()
        self.root.addLayout(head)

        bar = QHBoxLayout()
        pick = QPushButton("Choose input file…")
        pick.setObjectName("primary")
        pick.clicked.connect(self.choose_file)
        self.path_label = QLabel("No file selected")
        self.path_label.setObjectName("muted")
        bar.addWidget(pick)
        bar.addWidget(self.path_label, stretch=1)
        self.root.addLayout(bar)

    def choose_file(self):
        start = os.path.join(BASE_DIR, "datasets", self.dataset_folder)
        if not os.path.isdir(start):
            start = BASE_DIR
        print("DIALOG START:", start, os.path.isdir(start),
      os.listdir(start) if os.path.isdir(start) else None)
        path, _ = QFileDialog.getOpenFileName(
            self, "Select input file", start, "Text files (*.txt);;All files (*)",
            options=QFileDialog.Option.DontUseNativeDialog)
        if not path:
            return
        try:
            with open(path, "r") as f:
                lines = f.readlines()
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Could not read file: {e}")
            return
        self.path_label.setText(path)
        self.load(lines)

    def load(self, lines):
        raise NotImplementedError

    def error(self, msg):
        QMessageBox.critical(self, "Invalid Format", msg)