import numpy as np
import plotly.graph_objects as go

def is_counterclockwise(polygon):
    """Check if the points in the polygon are ordered counterclockwise."""
    n = len(polygon)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += polygon[i][0] * polygon[j][1]
        area -= polygon[j][0] * polygon[i][1]
    return area > 0

def ensure_counterclockwise(polygon):
    """Ensure that the points in the polygon are ordered counterclockwise."""
    if not is_counterclockwise(polygon):
        # The polygon is clockwise; reverse the order of its vertices.
        return list(reversed(polygon))
    else:
        # The polygon is already counterclockwise; return it as is.
        print('Polygon is counterclockwise')
        return polygon[:]
    
def ensure_clockwise(polygon):
    """Ensure that the points in the polygon are ordered clockwise."""
    if is_counterclockwise(polygon):
        return list(reversed(polygon))
    else:
        print('Polygon is clockwise')
        return polygon[:]
 
def load_off_file(file_path: str) -> tuple[list, list]:
    """Load a .off file and return list of vertices and list of faces."""
    # Open the file and read its contents
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Strip empty lines and comments (lines starting with '0' or '#')
    lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]

    # Check if it's a valid OFF file
    if lines[0] != 'OFF':
        raise ValueError("The file is not in OFF format")

    # Read the header (number of vertices, faces, edges)
    num_vertices, num_faces, _ = map(int, lines[1].split())

    # Read vertices (each vertex is a line with 3 float values)
    vertices = []
    for i in range(2, 2 + num_vertices):
        vertices.append(list(map(float, lines[i].split())))

    # Read faces (each face starts with the number of vertices followed by indices)
    faces = []
    for i in range(2 + num_vertices, 2 + num_vertices + num_faces):
        face_data = list(map(int, lines[i].split()))
        faces.append(face_data[1:])  # Skip the first number, which is the number of vertices in the face
    return vertices, faces

 
def visualize_mesh(vertices, faces):
    """
    Visualize a 3D mesh with colored faces and visible vertices.
 
    Parameters
    ----------
    vertices : array-like, shape (N, 3)  — x, y, z coordinates of the vertices
    faces    : array-like, shape (M, 3)  — triangle indices
    """
    v = np.asarray(vertices)
    f = np.asarray(faces)
 
    # One color value per face (face index used as intensity)
    face_colors = np.arange(len(f))
 
    fig = go.Figure()
 
    # Mesh with one color per face
    fig.add_trace(go.Mesh3d(
        x=v[:, 0], y=v[:, 1], z=v[:, 2],
        i=f[:, 0], j=f[:, 1], k=f[:, 2],
        intensity=face_colors,
        intensitymode="cell",
        colorscale="Viridis",
        showscale=False,
        opacity=1.0,
    ))
 
    # Vertices displayed as scatter points
    fig.add_trace(go.Scatter3d(
        x=v[:, 0], y=v[:, 1], z=v[:, 2],
        mode="markers",
        marker=dict(size=3, color="red"),
        name="vertices",
    ))
 
    fig.update_layout(scene=dict(aspectmode="data"), margin=dict(l=0, r=0, t=0, b=0))
    fig.show()