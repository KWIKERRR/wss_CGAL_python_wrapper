from weighted_straight_skeleton import compute_straight_skeleton
from utils import ensure_counterclockwise, load_off_file, visualize_mesh

# Footprint should be in the counterclockwise order
footprint = ensure_counterclockwise([(-10, 10), (-10, -10), (10, -10), (10, 10)])
angles = [90, 45, 90, 45]
output_file_path = "roof.off"
verbose = True

compute_straight_skeleton(footprint, angles=angles, output_file_path=output_file_path, verbose=verbose)
vertices, faces = load_off_file(output_file_path)
visualize_mesh(vertices, faces)