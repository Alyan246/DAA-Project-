"""Closest pair page: shows the closest pair of points (one red, one blue)."""
import time

from GUI.Common import (BLUE, MUTED, RED, AlgoPage, StatCard, load_module,
                        generate_closestpair_dataset)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

closest_pair = load_module("closest_pair.py").closest_pair

SHOW_ALL_POINTS = True   # False = draw only the two closest points


class PairCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.points = []
        self.pair = None
        self.setMinimumSize(420, 320)

    def set_data(self, points, pair):
        self.points = points
        self.pair = pair
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        self.bounds = (min(xs), max(xs), min(ys), max(ys))
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor("#0b1220"))
        if not self.points:
            p.setPen(QColor(MUTED))
            p.drawText(self.rect(), Qt.AlignCenter, "Choose an input file to begin")
            return

        min_x, max_x, min_y, max_y = self.bounds
        rx, ry = max(max_x - min_x, 1), max(max_y - min_y, 1)
        w, h, pad = self.width(), self.height(), 24

        def pt(q):
            return QPointF(pad + (q[0] - min_x) / rx * (w - 2 * pad),
                           h - (pad + (q[1] - min_y) / ry * (h - 2 * pad)))

        if SHOW_ALL_POINTS:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#475569"))
            for q in self.points:
                p.drawEllipse(pt(q), 2.5, 2.5)

        a, b = self.pair
        p.setPen(QPen(QColor("#94a3b8"), 1, Qt.DashLine))
        p.drawLine(pt(a), pt(b))
        p.setPen(QPen(QColor("white"), 1.5))
        p.setBrush(QColor(RED))
        p.drawEllipse(pt(a), 5, 5)
        p.setBrush(QColor(BLUE))
        p.drawEllipse(pt(b), 5, 5)


class ClosestPairPage(AlgoPage):
    def __init__(self, go_home):
        super().__init__("CLOSEST PAIR  ·  POINTS IN THE PLANE", go_home, "closest_pair")
        generate_closestpair_dataset()

        row = QHBoxLayout()
        self.c_n = StatCard("Points")
        self.c_time = StatCard("Time taken")
        self.c_dist = StatCard("Closest distance")
        for c in (self.c_n, self.c_time, self.c_dist):
            row.addWidget(c)
        self.root.addLayout(row)

        self.canvas = PairCanvas()
        self.root.addWidget(self.canvas, stretch=1)

        self.legend = QLabel("")
        self.legend.setTextFormat(Qt.RichText)
        self.root.addWidget(self.legend)

    def load(self, lines):
        points = []
        for line in lines:
            try:
                x, y = map(float, line.strip().split(","))
                points.append((x, y))
            except ValueError:
                continue
        if len(points) < 2:
            self.error("Closest pair needs a file with at least 2 points (format: x,y).")
            return

        t0 = time.perf_counter()
        min_dist, pair = closest_pair(points)
        elapsed = time.perf_counter() - t0

        self.c_n.set(f"{len(points):,}")
        self.c_time.set(f"{elapsed * 1000:.3f} ms")
        self.c_dist.set(f"{min_dist:.4f}")
        self.canvas.set_data(points, pair)

        a, b = pair
        self.legend.setText(
            f'<span style="color:{RED}">●</span> Red point: ({a[0]:g}, {a[1]:g}) &nbsp;&nbsp; '
            f'<span style="color:{BLUE}">●</span> Blue point: ({b[0]:g}, {b[1]:g})')