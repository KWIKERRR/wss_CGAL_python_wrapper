import ctypes
import os
import numpy as np

PROJECT_ROOT = os.getenv('WSS_PROJECT_ROOT', os.getcwd())

lib_path = os.path.join(PROJECT_ROOT, "build/libweighted_straight_skeleton.so")
lib = ctypes.CDLL(lib_path)

lib.compute_straight_skeleton_and_save.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # points
    ctypes.POINTER(ctypes.c_double),  # angles
    ctypes.c_size_t,                  # points_rows
    ctypes.c_size_t,                  # points_cols
    ctypes.c_char_p,                  # output_file_path
    ctypes.c_bool,                    # verbose
    ctypes.c_char_p,                  # error_log
    ctypes.c_size_t,                  # buffer_size
]
lib.compute_straight_skeleton_and_save.restype = ctypes.c_bool

lib.compute_straight_skeleton_with_holes_and_save.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # points
    ctypes.POINTER(ctypes.c_double),  # holes
    ctypes.POINTER(ctypes.c_double),  # angles
    ctypes.c_size_t,                  # points_rows
    ctypes.c_size_t,                  # points_cols
    ctypes.POINTER(ctypes.c_int),     # holes_rows
    ctypes.POINTER(ctypes.c_int),     # holes_cols
    ctypes.c_size_t,                  # holes_number
    ctypes.c_char_p,                  # output_file_path
    ctypes.c_bool,                    # verbose
    ctypes.c_char_p,                  # error_log
    ctypes.c_size_t,                  # buffer_size
]
lib.compute_straight_skeleton_with_holes_and_save.restype = ctypes.c_bool


def flatten(lst):
    """Recursively flattens a nested list."""
    flat_list = []
    for item in lst:
        if isinstance(item, (list, tuple, np.ndarray)):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list


def _rotate_angles(segment):
    """
    Applies the edge→vertex index shift expected by the C++ side for one contour.
    The last angle wraps around to become the first.
    """
    seg = list(segment)
    return [seg[-1]] + seg[:-1]


def _prepare_angles(angles, n_outer, holes_list):
    """
    Splits the flat angles array into per-contour slices, applies the
    rotation independently on each one, then concatenates the results.

    The C++ wrapper consumes angles contour by contour
    (outer first, then each hole in order), advancing its pointer by the
    contour size each time, so the rotation must be applied per-contour —
    not on the whole array at once.

    Args:
        angles  : flat sequence of length n_outer + sum(len(h) for h in holes_list)
        n_outer : number of vertices in the outer contour
        holes_list : list of holes (may be None or empty)

    Returns:
        np.ndarray of float64, ready to pass to ctypes
    """
    angles = list(angles)
    result = _rotate_angles(angles[:n_outer])

    if holes_list:
        offset = n_outer
        for hole in holes_list:
            n = len(hole)
            result += _rotate_angles(angles[offset:offset + n])
            offset += n

    return np.ascontiguousarray(result, dtype=np.float64)


def compute_straight_skeleton(arr, angles, output_file_path, holes_list=None, verbose=False):
    """
    Computes the weighted straight skeleton via CGAL.

    Args:
        arr (list/np.array): Outer contour [[x,y], [x,y],...]
        angles (list/np.array): Angles for each edge, outer contour first then
                                holes in order, as a flat sequence.
        output_file_path (str): Output file path (.off)
        holes_list (list): List of holes [[[x,y],...], [[x,y],...]]
        verbose (bool): Print details from the C++ side

    Raises:
        RuntimeError: If CGAL encounters a geometric error or an intercepted crash.
    """
    # Force memory contiguity and float64 (C++ double) type.
    # Local variable assignment prevents the GC from freeing data during C++ execution.
    points_np = np.ascontiguousarray(arr, dtype=np.float64)
    rows, cols = points_np.shape

    angles_np = _prepare_angles(angles, rows, holes_list)

    input_points = points_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    input_angles = angles_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    c_rows = ctypes.c_size_t(rows)
    c_cols = ctypes.c_size_t(cols)
    c_verbose = ctypes.c_bool(verbose)
    c_output_path = ctypes.c_char_p(output_file_path.encode('utf-8'))

    # 4 KB buffer to receive error messages from C++
    error_buffer_size = 4096
    error_buffer = ctypes.create_string_buffer(error_buffer_size)
    c_buffer_size = ctypes.c_size_t(error_buffer_size)

    success = False

    if holes_list:
        holes_rows_list = [len(hole) for hole in holes_list]
        holes_cols_list = [len(hole[0]) if len(hole) > 0 else 0 for hole in holes_list]

        holes_rows_np = np.ascontiguousarray(holes_rows_list, dtype=np.int32)
        holes_cols_np = np.ascontiguousarray(holes_cols_list, dtype=np.int32)

        holes_flat = flatten(holes_list)
        holes_np = np.ascontiguousarray(holes_flat, dtype=np.float64)

        input_holes = holes_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        input_holes_rows = holes_rows_np.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        input_holes_cols = holes_cols_np.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
        c_num_holes = ctypes.c_size_t(len(holes_list))

        success = lib.compute_straight_skeleton_with_holes_and_save(
            input_points,
            input_holes,
            input_angles,
            c_rows,
            c_cols,
            input_holes_rows,
            input_holes_cols,
            c_num_holes,
            c_output_path,
            c_verbose,
            error_buffer,
            c_buffer_size,
        )
    else:
        success = lib.compute_straight_skeleton_and_save(
            input_points,
            input_angles,
            c_rows,
            c_cols,
            c_output_path,
            c_verbose,
            error_buffer,
            c_buffer_size,
        )

    if not success:
        error_message = error_buffer.value.decode('utf-8', errors='replace')
        if not error_message:
            error_message = "Unknown error occurred in CGAL wrapper (no log returned)."
        raise RuntimeError(f"CGAL Execution Failed: {error_message}")

    return True