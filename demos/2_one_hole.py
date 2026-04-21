import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weighted_straight_skeleton import compute_straight_skeleton
from utils import ensure_clockwise, ensure_counterclockwise, load_off_file, visualize_mesh

footprint = ensure_counterclockwise([(-10, 10), (-10, -10), (10, -10), (10, 10)])
base_angles = [90, 45, 90, 45]

# Hole points should be in the clockwise order
hole = ensure_clockwise([(-5, 5), (-5, -5), (5, -5), (5, 5)])
hole_angles = [45, 90, 90, 45]

# Base angles and hole angles should be concatenate in one list
roof_with_one_hole_angles = base_angles + hole_angles

roof_with_one_hole_path = 'roof_with_one_hole.off'
verbose = True

compute_straight_skeleton(footprint, 
                          angles=roof_with_one_hole_angles, 
                          output_file_path=roof_with_one_hole_path, 
                          holes_list=[hole], verbose=verbose)

vertices, faces = load_off_file(roof_with_one_hole_path)
visualize_mesh(vertices, faces)