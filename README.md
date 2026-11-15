# DAA Project: Divide and Conquer Algorithms

Course project for Design and Analysis of Algorithms. It implements two divide and conquer algorithms, generates random input datasets for each, and provides a desktop GUI where you pick an algorithm, choose an input file, and see the algorithm run on it.

| # | Problem | Algorithm | Time complexity |
|---|---------|-----------|-----------------|
| 1 | Integer multiplication | Karatsuba | O(n^log₂3) ≈ O(n^1.585) |
| 2 | Closest pair of points | Divide by x-coordinate, check the strip around the dividing line | O(n log² n) (strip is re-sorted at every level; O(n log n) with a pre-sorted y-list) |

## Project structure

```
DAA_Project/
├── Gui.py                   # entry point: main page ("Select algorithm") + window
├── GUI/
│   ├── Common.py            # theme, shared widgets, algorithm loader, dataset generators
│   ├── karatsubapage.py     # Karatsuba page
│   └── Closestpairpage.py   # Closest pair page
├── algorithms/
│   ├── Karatsuba.py         # Karatsuba(x, y)
│   └── closest_pair.py      # closest_pair(points), distance(), mergesort()
├── datasets/                # generated automatically (git-ignored)
│   ├── karatsuba/input_1.txt ... input_10.txt
│   └── closest_pair/input_1.txt ... input_10.txt
└── README.md
```

## Requirements

- Python 3.8 or newer
- [PySide6](https://pypi.org/project/PySide6/) (Qt for Python) for the GUI

The algorithms and dataset generators use only the standard library. PySide6 is installed automatically the first time you run `Gui.py` (`pip install --user PySide6`), or install it yourself:

```
pip install PySide6
```

## Running

```
python3 Gui.py
```

Each launch generates 20 fresh random input files in `datasets/` (10 per problem), overwriting the previous ones. To keep a particular set (for example, the one you report results from), copy the `datasets/` folder somewhere else before launching again.

### Using the GUI

1. **Main page:** choose **Karatsuba** or **Closest Pair**.
2. **Algorithm page:** click **Choose input file…** and pick a file from `datasets/<algorithm>/`. The result appears immediately.
3. Use **Back** to return to the main page and pick the other algorithm.

**Karatsuba page** shows the digit counts of both numbers, the time taken, the number of recursive calls, a check of the product against Python's own `x*y`, a recursion tree of the first levels (children are z2, z1, z0), and the top-level working (divide, conquer, combine) with the final product.

**Closest pair page** shows the number of points, the time taken and the closest distance. The plot highlights the closest pair: one point in red and one in blue, with their coordinates listed below the plot. The other points are drawn faintly for context (set `SHOW_ALL_POINTS = False` in `Closestpairpage.py` to draw only the pair).

## Input file formats

**Karatsuba** (`datasets/karatsuba/input_N.txt`): two positive integers, one per line, each between 150 and 300 digits.

```
<number 1>
<number 2>
```

**Closest pair** (`datasets/closest_pair/input_N.txt`): one point per line as `x,y`. Each file has between 150 and 500 points with integer coordinates in [-10000, 10000].

```
x1,y1
x2,y2
...
```

All input sizes are above 100, as the assignment requires.

## Algorithms

### Karatsuba integer multiplication

`Karatsuba(x, y)` multiplies two integers using three recursive multiplications instead of four.

Split each number around m = ⌊n/2⌋ digits, where n is the larger digit count:

- x = a·10^m + b
- y = c·10^m + d

Then:

- z2 = a·c
- z0 = b·d
- z1 = (a + b)(c + d)
- x·y = z2·10^2m + (z1 − z2 − z0)·10^m + z0

Recursion stops when either number has a single digit.

### Closest pair of points

`closest_pair(points)` returns `(distance, (p1, p2))`.

1. If there are 3 or fewer points, compare every pair (brute force).
2. Sort the points by x and split them at the middle point.
3. Solve each half recursively to get the best distances `dl` and `dr`. Let `d = min(dl, dr)`.
4. Collect the points within `d` of the dividing line (the strip) and sort them by y.
5. For each strip point, compare it only with the points above it whose y-difference is less than `d`. Stop as soon as the gap is at least `d`. A constant number of neighbours is checked per point.
6. Return the smallest distance found.

Distance is d = √((x₁ − x₂)² + (y₁ − y₂)²). Sorting uses the project's own `mergesort(arr, key)`.


## Team Members
Faran Mukhtar - 24k-0646
Alyan Ahmed - 24k-0743