import sys

from GUI.Common import STYLE
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget,
    QVBoxLayout, QWidget,
)
from GUI.karatsubapage import KaratsubaPage
from GUI.Closestpairpage import ClosestPairPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DAA Project - Divide and Conquer")
        self.resize(1100, 760)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.stack.addWidget(self.build_home())
        self.kara = KaratsubaPage(self.go_home)
        self.closest = ClosestPairPage(self.go_home)
        self.stack.addWidget(self.kara)
        self.stack.addWidget(self.closest)

    def build_home(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(18)

        hero = QLabel("DIVIDE AND CONQUER")
        hero.setObjectName("hero")
        hero.setAlignment(Qt.AlignCenter)
        sub = QLabel("SELECT ALGORITHM")
        sub.setObjectName("sub")
        sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(hero)
        lay.addWidget(sub)
        lay.addSpacing(30)

        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        row.setSpacing(30)
        b1 = QPushButton("KARATSUBA\n\nInteger multiplication")
        b2 = QPushButton("CLOSEST PAIR\n\nPoints in the plane")
        for b in (b1, b2):
            b.setObjectName("card")
        b1.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        b2.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        row.addWidget(b1)
        row.addWidget(b2)
        lay.addLayout(row)
        return page

    def go_home(self):

        self.stack.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())