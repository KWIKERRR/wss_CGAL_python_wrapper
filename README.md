# Weighted Straight Skeleton Wrapper

A Python/C++ wrapper around [CGAL](https://www.cgal.org/)'s weighted straight skeleton and skeleton extrusion (`CGAL::extrude_skeleton`) for generating 3D roof-like meshes from 2D polygon footprints with per-edge angle control.

---

## Overview

This library exposes two C++ functions via a shared library (`libweighted_straight_skeleton.so` / `.dll`):

- **`compute_straight_skeleton_and_save`** — computes the weighted straight skeleton of a simple polygon and saves the resulting 3D mesh.

The Python wrapper (`weighted_straight_skeleton.py`) handles all ctypes bridging and exposes a single clean function: `compute_straight_skeleton`.

Output is saved as an `.off` mesh file (Object File Format), readable by most 3D tools.

---

## Requirements

| Dependency | Version |
|---|---|
| CGAL | 5.6.2 |
| Boost | 1.71.0 |
| GMP | 6.3.0 |
| MPFR | 4.2.1 |
| CMake | ≥ 3.10 |
| Python | ≥ 3.x |

> All dependencies are built locally under `dependencies/`. No system-wide installation is required.

---

## Building

### 1. Set up the environment variable

The build system relies on `WSS_GEN_PROJECT_ROOT` to locate dependencies and `WSS_PROJECT_ROOT` to locate the compiled shared library at runtime.

```bash
export WSS_PROJECT_ROOT=$(pwd)
```

### 2. Download and build dependencies

A convenience script is provided to download and compile all dependencies from source:

```bash
bash install.sh
```

This will download and build GMP, MPFR, Boost, CGAL into `dependencies/` and compiled the library. The compiled library will be placed in `build/libweighted_straight_skeleton.so` (Linux).

### 3. Build the shared library

```bash
cmake -S ./ -B ./build -DCMAKE_BUILD_TYPE=Release
cmake --build ./build --config Release
```

The compiled library will be placed in `build/libweighted_straight_skeleton.so` (Linux) or `build/weighted_straight_skeleton.dll` (Windows).

---

## Usage

```python
from weighted_straight_skeleton import compute_straight_skeleton
from utils import ensure_counterclockwise, load_off_file, visualize_mesh

# Footprint vertices must be in counterclockwise order
footprint = ensure_counterclockwise([(-10, 10), (-10, -10), (10, -10), (10, 10)])

# One angle per edge (in degrees), controls the roof slope per face
angles = [90, 45, 90, 45]
output_file_path = "roof.off"

compute_straight_skeleton(footprint, angles=angles, output_file_path=output_file_path, verbose=True)

vertices, faces = load_off_file(output_file_path)
visualize_mesh(vertices, faces)
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `arr` | `list` / `np.ndarray` | Outer contour as `[[x, y], ...]`, counterclockwise |
| `angles` | `list` / `np.ndarray` | Roof slope angle per edge (degrees). Covers outer contour + all holes in order |
| `output_file_path` | `str` | Path to the output `.off` file |
| `holes_list` | `list` (optional) | List of hole contours `[[[x,y], ...], ...]` |
| `verbose` | `bool` (optional) | Print polygon and angle details from the C++ side |

---


## Project Structure

```
.
├── weighted_straight_skeleton.cpp   # C++ CGAL wrapper
├── weighted_straight_skeleton.py    # Python ctypes bindings
├── CMakeLists.txt                   # Build configuration
├── install.sh                       # Dependency download & build script
├── utils.py                         # Helper python functions
└── build/
    └── libweighted_straight_skeleton.so 
```

---