import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weighted_straight_skeleton import compute_straight_skeleton
from utils import ensure_counterclockwise, load_off_file, visualize_mesh

# Footprint should be in the counterclockwise order
footprint = ensure_counterclockwise([(-10, 10), (-10, -10), (10, -10), (10, 10)])
base_angles = [90, 45, 90, 45]
base_roof_path = "roof.off"
verbose = True

compute_straight_skeleton(footprint, angles=base_angles, output_file_path=base_roof_path, verbose=verbose)
vertices, faces = load_off_file(base_roof_path)
visualize_mesh(vertices, faces)