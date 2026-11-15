"""Karatsuba page: integer multiplication with a traced recursion tree."""
import time

from GUI.Common import (GREEN, MONO, RED, AlgoPage, StatCard, load_module, short , generate_karatsuba_dataset)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPlainTextEdit, QSplitter, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget,
)

Karatsuba = load_module("Karatsuba.py").Karatsuba


MAX_TREE_DEPTH = 3


def karatsuba_trace(x, y, depth, stats):
    """Same recursion as Karatsuba(); also records the first levels for display."""
    stats["calls"] += 1
    keep = depth <= MAX_TREE_DEPTH
    if x < 10 or y < 10:
        stats["base"] += 1
        res = x * y
        return res, ({"x": x, "y": y, "base": True, "result": res, "kids": []} if keep else None)

    n = max(len(str(x)), len(str(y)))
    m = n // 2
    high1, low1 = divmod(x, 10 ** m)
    high2, low2 = divmod(y, 10 ** m)

    z0, n0 = karatsuba_trace(low1, low2, depth + 1, stats)
    z1, n1 = karatsuba_trace(low1 + high1, low2 + high2, depth + 1, stats)
    z2, n2 = karatsuba_trace(high1, high2, depth + 1, stats)
    res = (z2 * 10 ** (2 * m)) + ((z1 - z2 - z0) * 10 ** m) + z0
    if not keep:
        return res, None
    node = {
        "x": x, "y": y, "n": n, "m": m, "base": False, "result": res,
        "high1": high1, "low1": low1, "high2": high2, "low2": low2,
        "z0": z0, "z1": z1, "z2": z2,
        "kids": [("z2", n2), ("z1", n1), ("z0", n0)],
    }
    return res, node


class KaratsubaPage(AlgoPage):
    def __init__(self, go_home):
        super().__init__("KARATSUBA  ·  INTEGER MULTIPLICATION", go_home, "karatsuba")

        generate_karatsuba_dataset()
        row = QHBoxLayout()
        self.c_x = StatCard("Digits in X")
        self.c_y = StatCard("Digits in Y")
        self.c_time = StatCard("Time taken")
        self.c_calls = StatCard("Recursive calls")
        self.c_ok = StatCard("Correct (x·y check)")
        for c in (self.c_x, self.c_y, self.c_time, self.c_calls, self.c_ok):
            row.addWidget(c)
        self.root.addLayout(row)

        split = QSplitter(Qt.Horizontal)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Subproblem  (x × y)", "n", "split m", "product"])
        self.tree.setColumnWidth(0, 330)
        self.tree.setColumnWidth(1, 50)
        self.tree.setColumnWidth(2, 70)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont(MONO)
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        cap = QLabel(f"Recursion tree (first {MAX_TREE_DEPTH} levels, children = z2, z1, z0)")
        cap.setObjectName("muted")
        ll.addWidget(cap)
        ll.addWidget(self.tree)
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        cap2 = QLabel("Step-by-step working (top level)")
        cap2.setObjectName("muted")
        rl.addWidget(cap2)
        rl.addWidget(self.text)
        split.addWidget(left)
        split.addWidget(right)
        split.setSizes([520, 460])
        self.root.addWidget(split, stretch=1)

    def load(self, lines):
        try:
            num1 = int(lines[0].strip())
            num2 = int(lines[1].strip())
        except (IndexError, ValueError):
            self.error("Karatsuba needs a file with exactly 2 integers on separate lines.")
            return

        # Real algorithm: result + timing
        t0 = time.perf_counter()
        product = Karatsuba(num1, num2)
        elapsed = time.perf_counter() - t0

        # Traced copy of the same recursion, for the display
        stats = {"calls": 0, "base": 0}
        traced, root = karatsuba_trace(num1, num2, 0, stats)
        ok = product == num1 * num2 == traced

        self.c_x.set(str(len(str(num1))))
        self.c_y.set(str(len(str(num2))))
        self.c_time.set(f"{elapsed * 1000:.3f} ms")
        self.c_calls.set(f"{stats['calls']:,}")
        self.c_ok.set("Yes" if ok else "NO", GREEN if ok else RED)

        self.tree.clear()
        self.add_node(self.tree.invisibleRootItem(), "root", root)
        self.tree.expandToDepth(1)

        self.text.setPlainText(self.working_text(num1, num2, root, product, elapsed, stats, ok))

    def add_node(self, parent, tag, node):
        label = f"[{tag}]  {short(node['x'])} × {short(node['y'])}"
        if node["base"]:
            item = QTreeWidgetItem([label, "-", "base case", short(node["result"])])
        else:
            item = QTreeWidgetItem([label, str(node["n"]), str(node["m"]), short(node["result"])])
        parent.addChild(item)
        for t, kid in node["kids"]:
            if kid is not None:
                self.add_node(item, t, kid)

    def working_text(self, x, y, r, product, elapsed, stats, ok):
        if r["base"]:
            return f"One of the numbers has a single digit, so it is multiplied directly.\n\nProduct = {product}"
        m = r["m"]
        L = [
            "STEP 1 - DIVIDE",
            f"  n = max(digits of x, digits of y) = {r['n']}",
            f"  m = n // 2 = {m}",
            f"  x = x_high·10^{m} + x_low",
            f"      x_high = {short(r['high1'])}",
            f"      x_low  = {short(r['low1'])}",
            f"  y = y_high·10^{m} + y_low",
            f"      y_high = {short(r['high2'])}",
            f"      y_low  = {short(r['low2'])}",
            "",
            "STEP 2 - CONQUER (only 3 recursive multiplications, not 4)",
            f"  z2 = x_high · y_high              = {short(r['z2'])}",
            f"  z0 = x_low · y_low                = {short(r['z0'])}",
            f"  z1 = (x_high+x_low)(y_high+y_low) = {short(r['z1'])}",
            "",
            "STEP 3 - COMBINE",
            f"  x·y = z2·10^{2 * m} + (z1 - z2 - z0)·10^{m} + z0",
            f"      = {short(product, 14)}",
            "",
            "RESULT",
            f"  Time taken       : {elapsed * 1000:.3f} ms",
            f"  Recursive calls  : {stats['calls']:,}  ({stats['base']:,} base cases)",
            f"  Matches Python's x*y : {'yes' if ok else 'NO'}",
            "",
            "Full product:",
            str(product),
        ]
        return "\n".join(L)