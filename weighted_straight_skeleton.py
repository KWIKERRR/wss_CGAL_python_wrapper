import ctypes
import os 
import numpy as np

PROJECT_ROOT = os.getenv('WSS_PROJECT_ROOT', os.getcwd())

lib_path = os.path.join(PROJECT_ROOT, "build/libweighted_straight_skeleton.so")
lib = ctypes.CDLL(lib_path)

lib.compute_straight_skeleton_and_save.argtypes = lib.compute_straight_skeleton_and_save.argtypes = [
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
    flat_list = list()
    for item in lst:
        if isinstance(item, (list, tuple, np.ndarray)):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list


def compute_straight_skeleton(arr, angles, output_file_path, holes_list=None, verbose=False):
    """
    Computes the weighted straight skeleton via CGAL.

    Args:
        arr (list/np.array): Outer contour [[x,y], [x,y],...]
        angles (list/np.array): Angles for each edge (outer contour + holes)
        output_file_path (str): Output file path (.off)
        holes_list (list): List of holes [[[x,y],...], [[x,y],...]]
        verbose (bool): Print details from the C++ side

    Raises:
        RuntimeError: If CGAL encounters a geometric error or an intercepted crash.
    """

    # Force memory contiguity and float64 (C++ double) type.
    # Local variable assignment prevents the GC from freeing data during C++ execution.
    points_np = np.ascontiguousarray(arr, dtype=np.float64)

    angles = [angles[-1]] + list(angles[:-1])
    angles_np = np.ascontiguousarray(angles, dtype=np.float64)

    rows, cols = points_np.shape

    input_points = points_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    input_angles = angles_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    c_rows = ctypes.c_size_t(rows)
    c_cols = ctypes.c_size_t(cols)
    c_verbose = ctypes.c_bool(verbose)
    c_output_path = ctypes.c_char_p(output_file_path.encode('utf-8'))

    # 4KB buffer to receive error messages from C++
    error_buffer_size = 4096
    error_buffer = ctypes.create_string_buffer(error_buffer_size)
    c_buffer_size = ctypes.c_size_t(error_buffer_size)

    success = False

    if holes_list:
        holes_rows_list = [len(hole) for hole in holes_list]
        holes_cols_list = [len(hole) if len(hole) > 0 else 0 for hole in holes_list]

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
            c_buffer_size
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
            c_buffer_size
        )

    if not success:
        error_message = error_buffer.value.decode('utf-8', errors='replace')
        if not error_message:
            error_message = "Unknown error occurred in CGAL wrapper (no log returned)."
        raise RuntimeError(f"CGAL Execution Failed: {error_message}")

    return True