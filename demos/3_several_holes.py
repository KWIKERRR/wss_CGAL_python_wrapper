import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weighted_straight_skeleton import compute_straight_skeleton
from utils import ensure_clockwise, ensure_counterclockwise, load_off_file, visualize_mesh

footprint = ensure_counterclockwise([(-10, 10), (-10, -10), (10, -10), (10, 10)])
base_angles = [90, 45, 90, 45]

hole1 = ensure_clockwise([(2, 8), (8, 8), (8, 2), (2, 2)])
hole1_angles = [90, 45, 90, 45]

hole2 = ensure_clockwise([(-2, -8), (-8, -8), (-8, -2), (-2, -2)])
hole2_angles = [45, 90, 90, 45]

hole3 = ensure_clockwise([(-2, 8), (-8, 8), (-8, 2), (-2, 2)])
hole3_angles = [45, 90, 45, 90]

hole4 = ensure_clockwise([(2, -8), (8, -8), (8, -2), (2, -2)])
hole4_angles = [90, 90, 45, 45]

holes = [hole1, hole2, hole3, hole4]
roof_with_holes_angle = base_angles + hole1_angles + hole2_angles + hole3_angles + hole4_angles

roof_with_holes_path = 'roof_with_holes.off'
verbose = True

compute_straight_skeleton(footprint, 
                          angles=roof_with_holes_angle, 
                          output_file_path=roof_with_holes_path, 
                          holes_list=holes, verbose=verbose)

vertices, faces = load_off_file(roof_with_holes_path)
visualize_mesh(vertices, faces)