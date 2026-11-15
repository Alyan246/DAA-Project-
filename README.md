# DAA Project: Divide and Conquer Algorithms

Course project for Design and Analysis of Algorithms. It implements two divide and conquer algorithms, generates random datasets for each, runs the algorithms on them, and (in the GUI) lets the user pick an input file and watch the algorithms work.

| # | Problem | Algorithm | Time complexity |
|---|---------|-----------|-----------------|
| 1 | Closest pair of points | Divide by x-coordinate, check the strip around the dividing line | O(n log² n) (strip is re-sorted at every level; O(n log n) with a pre-sorted y-list) |
| 2 | Integer multiplication | Karatsuba | O(n^log₂3) ≈ O(n^1.585) |

## Project structure

```
DAA-Project-/
├── algorithms/
│   ├── Karatsuba.py        # Karatsuba(x, y)
│   └── closest_pair.py     # closest_pair(points), distance(), mergesort()
├── Generate_inputs.py      # creates the 20 input files
├── Gui.py                  # user interface (see "GUI" below)
├── datasets/               # generated inputs (git-ignored)
│   ├── karatsuba/input_1.txt ... input_10.txt
│   └── closest_pair/input_1.txt ... input_10.txt
└── README.md
```

## Requirements

- Python 3.8 or newer
- No external libraries for the algorithms or the generator (standard library only)

## Generating the datasets

```
python3 Generate_inputs.py
```

This creates 10 files for each problem (20 in total) inside `datasets/`.

**Karatsuba files** (`datasets/karatsuba/input_N.txt`): two positive integers, one per line. Each has a random length between 150 and 300 digits.

```
<number 1>
<number 2>
```

**Closest pair files** (`datasets/closest_pair/input_N.txt`): one point per line as `x,y`. Each file has a random number of points between 150 and 500, with integer coordinates in [-10000, 10000].

```
x1,y1
x2,y2
...
```

All input sizes are above 100, as the assignment requires.

## Algorithms

### Closest pair of points

`closest_pair(points)` returns `(distance, (p1, p2))`.

1. If there are 3 or fewer points, check every pair (brute force).
2. Sort the points by x and split them at the middle point.
3. Solve each half recursively to get the best distances `dl` and `dr`. Let `d = min(dl, dr)`.
4. Collect the points within `d` of the dividing line (the strip) and sort them by y.
5. For each strip point, compare it only with the points above it whose y-difference is less than `d`. Stop as soon as the gap is at least `d`. At most a constant number of neighbours are checked per point.
6. Return the smallest distance found.

Distance is d = √((x₁ − x₂)² + (y₁ − y₂)²). Sorting uses the project's own `mergesort(arr, key)`.

### Karatsuba integer multiplication

`Karatsuba(x, y)` multiplies two integers using three recursive multiplications instead of four.

Split each number around m = ⌊n/2⌋ digits:

- x = a·10^m + b
- y = c·10^m + d

Then:

- z2 = a·c
- z0 = b·d
- z1 = (a + b)(c + d)
- x·y = z2·10^2m + (z1 − z2 − z0)·10^m + z0

Recursion stops when either number is a single digit.

## Running the algorithms

```python
from algorithms.Karatsuba import Karatsuba
from algorithms.closest_pair import closest_pair

# Karatsuba
with open("datasets/karatsuba/input_1.txt") as f:
    a, b = (int(line) for line in f.read().split())
print(Karatsuba(a, b) == a * b)   # True

# Closest pair
with open("datasets/closest_pair/input_1.txt") as f:
    pts = [tuple(map(int, line.split(","))) for line in f if line.strip()]
print(closest_pair(pts))
```

## GUI

`Gui.py` is the interface for the assignment's part 4. It should let the user:

1. Choose an input file (Karatsuba or closest pair).
2. Run the matching algorithm on it.
3. See the working of the algorithm step by step:
   - **Closest pair:** the points plotted, the recursive splits, the strip, and the final closest pair highlighted.
   - **Karatsuba:** the split of each number, the values z0, z1, z2, and the recursive result.
4. See the final result and the running time.

> **Status:** `Gui.py` is currently empty. Fill in this section with the library used (for example Tkinter or Matplotlib) and how to launch it once it is written.

## Applying the algorithms to the datasets (part 3)

Run each algorithm on all 10 files of its problem and record the input size and running time (for example with `time.perf_counter()`). The results can go in a table:

| File | Input size | Time (s) | Result |
|------|-----------|----------|--------|
| input_1.txt | | | |

## Author

Faran Mukhtar