import numpy as np

def translate(x, y, z):
    """Return a 4x4 translation matrix."""
    # Task 1
    # This is a placement matrix. Adjust this according to the task.
    return np.array([
        [1.0, 0.0, 0.0, x],
        [0.0, 1.0, 0.0, y],
        [0.0, 0.0, 1.0, z],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float64)


def scale(sx, sy, sz):
    """Return a 4x4 scaling matrix."""
    # Task 2
    # This is a placement matrix. Adjust this according to the task.
    return np.array([
        [sx, 0.0, 0.0, 0.0],
        [0.0, sy, 0.0, 0.0],
        [0.0, 0.0, sz, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float64)

def rotate_z(angle_radians):
    # Task 3
    # This is a placement matrix. Adjust this according to the task.
    return np.array([
        [np.cos(angle_radians), -np.sin(angle_radians), 0.0, 0.0],
        [np.sin(angle_radians), np.cos(angle_radians), 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float64)

def rotate_x(angle_radians):
    # Task 3
    # This is a placement matrix. Adjust this according to the task.
    return np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, np.cos(angle_radians), -np.sin(angle_radians), 0.0],
        [0.0, np.sin(angle_radians), np.cos(angle_radians), 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float64)

def rotate_y(angle_radians):
    # Task 3
    # This is a placement matrix. Adjust this according to the task.
    return np.array([
        [np.cos(angle_radians), 0.0, -np.sin(angle_radians), 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [np.sin(angle_radians), 0.0, np.cos(angle_radians), 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float64)
