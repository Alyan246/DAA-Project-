"""Closest pair page: shows the closest pair of points (one red, one blue).

Mouse: hover a point = see its coordinates, drag = pan, double-click = reset view.
Zoom: mouse wheel, or pinch in / pinch out (touchpad or touchscreen).
"""
import time

from GUI.Common import (BLUE, MUTED, RED, AlgoPage, StatCard, load_module,
                        generate_closestpair_dataset)
from PySide6.QtCore import QEvent, Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPinchGesture, QPushButton, QWidget

closest_pair = load_module("closest_pair.py").closest_pair

SHOW_ALL_POINTS = True   # False = draw only the two closest points
PAD = 24                 # empty margin around the plot (pixels)
HOVER_RADIUS = 10        # how close (pixels) the mouse must be to a point


class PairCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.points = []
        self.pair = None
        self.view = None          # visible data range: [x0, x1, y0, y1]
        self.hover = None         # point under the mouse
        self.last_mouse = None    # for dragging
        self.setMinimumSize(420, 320)
        self.setMouseTracking(True)
        self.grabGesture(Qt.PinchGesture)   # touchscreen pinch

    # ---------- data / view ----------
    def set_data(self, points, pair):
        self.points = points
        self.pair = pair
        self.hover = None
        self.reset_view()

    def reset_view(self):
        if not self.points:
            return
        xs, ys = [p[0] for p in self.points], [p[1] for p in self.points]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        self.view = [x0, x0 + max(x1 - x0, 1), y0, y0 + max(y1 - y0, 1)]
        self.update()

    def zoom_to_pair(self):
        """Zoom in around the two closest points (equal scale on both axes)."""
        if not self.pair:
            return
        (ax, ay), (bx, by) = self.pair
        span = max(abs(ax - bx), abs(ay - by), 1) * 4
        pw, ph = max(self.width() - 2 * PAD, 1), max(self.height() - 2 * PAD, 1)
        per_px = span / min(pw, ph)                    # data units per pixel
        cx, cy = (ax + bx) / 2, (ay + by) / 2
        self.view = [cx - per_px * pw / 2, cx + per_px * pw / 2,
                     cy - per_px * ph / 2, cy + per_px * ph / 2]
        self.update()

    def to_px(self, q):
        x0, x1, y0, y1 = self.view
        pw, ph = self.width() - 2 * PAD, self.height() - 2 * PAD
        return QPointF(PAD + (q[0] - x0) / (x1 - x0) * pw,
                       self.height() - (PAD + (q[1] - y0) / (y1 - y0) * ph))

    def to_data(self, px, py):
        x0, x1, y0, y1 = self.view
        pw, ph = self.width() - 2 * PAD, self.height() - 2 * PAD
        return (x0 + (px - PAD) / pw * (x1 - x0),
                y0 + (self.height() - py - PAD) / ph * (y1 - y0))

    def zoom_at(self, px, py, factor):
        if not self.points:
            return
        cx, cy = self.to_data(px, py)
        x0, x1, y0, y1 = self.view
        if factor > 1 and min(x1 - x0, y1 - y0) / factor < 1e-3:
            return                                      # don't zoom in forever
        self.view = [cx - (cx - x0) / factor, cx + (x1 - cx) / factor,
                     cy - (cy - y0) / factor, cy + (y1 - cy) / factor]
        self.update()

    # ---------- pinch zoom ----------
    def event(self, e):
        t = e.type()
        # Touchpad pinch (Wayland / macOS): the system sends a zoom gesture
        if t == QEvent.NativeGesture and e.gestureType() == Qt.ZoomNativeGesture:
            pos = e.position()
            self.zoom_at(pos.x(), pos.y(), max(1 + e.value(), 0.05))
            return True
        # Touchscreen pinch
        if t == QEvent.Gesture:
            pinch = e.gesture(Qt.PinchGesture)
            if pinch is not None:
                if pinch.changeFlags() & QPinchGesture.ScaleFactorChanged:
                    c = pinch.centerPoint()
                    self.zoom_at(c.x(), c.y(), max(pinch.scaleFactor(), 0.05))
                e.accept()
                return True
        return super().event(e)

    # ---------- mouse ----------
    def wheelEvent(self, e):
        step = e.angleDelta().y()
        if step:
            self.zoom_at(e.position().x(), e.position().y(), 1.25 ** (step / 120))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.last_mouse = e.position()

    def mouseReleaseEvent(self, e):
        self.last_mouse = None

    def mouseDoubleClickEvent(self, e):
        self.reset_view()

    def mouseMoveEvent(self, e):
        if not self.points:
            return
        pos = e.position()
        if self.last_mouse is not None:                 # dragging = pan
            dx, dy = pos.x() - self.last_mouse.x(), pos.y() - self.last_mouse.y()
            x0, x1, y0, y1 = self.view
            pw, ph = self.width() - 2 * PAD, self.height() - 2 * PAD
            sx, sy = dx / pw * (x1 - x0), dy / ph * (y1 - y0)
            self.view = [x0 - sx, x1 - sx, y0 + sy, y1 + sy]
            self.last_mouse = pos
            self.hover = None
        else:                                           # hovering = find nearest point
            self.hover = self.nearest(pos)
        self.update()

    def leaveEvent(self, _):
        self.hover = None
        self.update()

    def nearest(self, pos):
        best, best_d = None, HOVER_RADIUS ** 2
        for q in self.points:
            c = self.to_px(q)
            d = (c.x() - pos.x()) ** 2 + (c.y() - pos.y()) ** 2
            if d <= best_d:
                best, best_d = q, d
        return best

    # ---------- drawing ----------
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor("#0b1220"))
        if not self.points:
            p.setPen(QColor(MUTED))
            p.drawText(self.rect(), Qt.AlignCenter, "Choose an input file to begin")
            return

        if SHOW_ALL_POINTS:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#475569"))
            for q in self.points:
                p.drawEllipse(self.to_px(q), 2.5, 2.5)

        a, b = self.pair
        p.setPen(QPen(QColor("#94a3b8"), 1, Qt.DashLine))
        p.drawLine(self.to_px(a), self.to_px(b))
        p.setPen(QPen(QColor("white"), 1.5))
        p.setBrush(QColor(RED))
        p.drawEllipse(self.to_px(a), 5, 5)
        p.setBrush(QColor(BLUE))
        p.drawEllipse(self.to_px(b), 5, 5)

        if self.hover is not None:
            self.draw_hover(p, a, b)

    def draw_hover(self, p, a, b):
        c = self.to_px(self.hover)
        p.setPen(QPen(QColor("white"), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(c, 8, 8)

        text = f"({self.hover[0]:g}, {self.hover[1]:g})"
        if self.hover == a:
            text += "  red"
        elif self.hover == b:
            text += "  blue"
        fm = p.fontMetrics()
        w, h = fm.horizontalAdvance(text) + 14, fm.height() + 8
        x = min(max(c.x() + 12, 2), self.width() - w - 2)
        y = min(max(c.y() - h - 8, 2), self.height() - h - 2)
        p.setPen(QPen(QColor("#475569"), 1))
        p.setBrush(QColor("#1e293b"))
        p.drawRoundedRect(QRectF(x, y, w, h), 5, 5)
        p.setPen(QColor("#e2e8f0"))
        p.drawText(QRectF(x, y, w, h), Qt.AlignCenter, text)


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

        bottom = QHBoxLayout()
        self.legend = QLabel("")
        self.legend.setTextFormat(Qt.RichText)
        zoom_btn = QPushButton("Zoom to closest pair")
        zoom_btn.clicked.connect(self.canvas.zoom_to_pair)
        reset_btn = QPushButton("Reset view")
        reset_btn.clicked.connect(self.canvas.reset_view)
        bottom.addWidget(self.legend, stretch=1)
        bottom.addWidget(zoom_btn)
        bottom.addWidget(reset_btn)
        self.root.addLayout(bottom)

        hint = QLabel("Hover a point for its coordinates  ·  pinch or scroll to zoom  ·  "
                      "drag to pan  ·  double-click to reset")
        hint.setObjectName("muted")
        self.root.addWidget(hint)

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