import sys

def load_obj(filepath, flatten=True):
    """
    Load vertex positions and face indices from a Wavefront OBJ file.

    Returns:
        vertices: list of [x, y, z]
        indices: list of [i0, i1, i2] (0-based)
    """
    vertices = []
    indices = []

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            prefix = parts[0]

            # Vertex positions
            if prefix == "v":
                x, y, z = map(float, parts[1:4])
                vertices.append([x, y, z])

            # Faces
            elif prefix == "f":
                face_indices = []
                for v in parts[1:]:
                    # Handle v, v/vt, v//vn, v/vt/vn
                    idx = int(v.split("/")[0]) - 1
                    face_indices.append(idx)

                # Triangulate polygon faces
                for i in range(1, len(face_indices) - 1):
                    indices.append([
                        face_indices[0],
                        face_indices[i],
                        face_indices[i + 1]
                    ])

    if flatten:
        vertices = [
            x
            for xs in vertices
            for x in xs
        ]
        indices = [
            x
            for xs in indices
            for x in xs
        ]

    return vertices, indices
