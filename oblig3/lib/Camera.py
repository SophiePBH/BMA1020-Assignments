import numpy as np
from .transformations import *
from pyglet.math import Mat4, Vec3
import math


class Camera:
    def __init__(self, width, height, fov, near, far):
        self.distance = 10
        self.theta = 0
        self.phi = 0

        self.width = width
        self.height = height
        self.fov = math.radians(fov)
        self.near = near
        self.far = far
        self.perspective: np.array = object
        self.view: np.array = object

    def get_position(self) -> Vec3:
        x = self.distance * np.cos(self.phi) * np.sin(self.theta)
        y = self.distance * np.sin(self.phi)
        z = self.distance * np.cos(self.phi) * np.cos(self.theta)

        return Vec3(x, y, z)

    def get_projection(self) -> Mat4:
        """Get the camera's projection matrix. Returns a 4x4 matrix"""
        # Translated from GLU's source code:
        # https://gitlab.freedesktop.org/mesa/glu/-/blob/master/src/libutil/project.c#L66
        half_fov = self.fov/2
        aspect = self.width/self.height
        delta_z = self.far - self.near
        sine = math.sin(half_fov)

        if delta_z == 0.0 or sine == 0.0 or aspect == 0.0:
            raise ValueError("Invalid perspective parameters")

        cotangent = math.cos(half_fov) / sine

        return Mat4(
            cotangent / aspect, 0, 0, 0,
            0, cotangent, 0, 0,
            0, 0, -(self.far + self.near) / delta_z, -1,
            0, 0, -(2.0 * self.near * self.far) / delta_z, 1,
        )
        
    def get_look_at(self) -> Mat4:
        """Get a look at matrix. Returns a 4x4 matrix."""
        # Task 4
        # This is a placement matrix. Adjust this according to the task.

        rotate_xy = rotate_x(self.phi) @ rotate_y(self.theta)

        return Mat4(
            rotate_xy[0][0], rotate_xy[1][0], rotate_xy[2][0], 0.0,
            rotate_xy[0][1], rotate_xy[1][1], rotate_xy[2][1], 0.0,
            rotate_xy[0][2], rotate_xy[1][2], rotate_xy[2][2], 0.0,
            0.0,             0.0,             -self.distance,  1.0,
        )