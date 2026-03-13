import pyglet
from pyglet.graphics import Batch, Group
from pyglet.graphics.shader import ShaderProgram
from pyglet.gl import GL_BLEND, GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, GL_TRIANGLES, glBlendFunc, glDisable, glEnable
from typing import Sequence
import numpy as np
from .shaders import *
import math

import os


def relative_path(*paths):
    """Get the relative path to a file.

    The problem with retrieving a file with relative path is it is based on the
    current working directory (CWD, sometimes known as the PWD - present working
    directory). A solution to this is to find the file relative to the called
    function's script's filepath.
    """
    return os.path.join(os.path.dirname(__file__), *paths)


class Rectangle3D(pyglet.shapes.ShapeBase):
    def __init__(
            self,
            x: float, y: float, z: float,
            width: float, height: float,
            color: tuple[int, int, int, int] | tuple[int,
                                                     int, int] = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ):
        """Create a rectangle or square.

        The rectangle's anchor point defaults to the ``(x, y)``
        coordinates, which are at the bottom left.

        Args:
            x:
                The X coordinate of the rectangle.
            y:
                The Y coordinate of the rectangle.
            width:
                The width of the rectangle.
            height:
                The height of the rectangle.
            color:
                The RGB or RGBA color of the circle, specified as a
                tuple of 3 or 4 ints in the range of 0-255. RGB colors
                will be treated as having an opacity of 255.
            blend_src:
                OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
            blend_dest:
                OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
            batch:
                Optional batch to add the shape to.
            group:
                Optional parent group of the shape.
        """
        self._x = x
        self._y = y
        self._z = z
        self._width = width
        self._height = height
        self._rotation = 0

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(6, blend_src, blend_dest, batch, group, program)

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            6, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y, self._z) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts
        else:
            x1 = self.x
            y1 = self.y
            x2 = x1 + self._width
            y2 = y1 + self._height
            z = self.z

            return x1, y1, 0, x2, y1, 0, x2, y2, 0, x1, y1, 0, x2, y2, 0, x1, y2, 0

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def width(self) -> float:
        """Get/set width of the rectangle.

        The new left and right of the rectangle will be set relative to
        its :py:attr:`.anchor_x` value.
        """
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._update_vertices()

    @property
    def height(self) -> float:
        """Get/set the height of the rectangle.

        The bottom and top of the rectangle will be positioned relative
        to its :py:attr:`.anchor_y` value.
        """
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value
        self._update_vertices()

    def _update_translation(self) -> None:
        """Overwrite this method to support 3d position"""
        self._vertex_list.translation[:] = (
            self._x, self._y, self._z) * self._num_verts

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()


class WorldGrid(Rectangle3D):
    def __init__(self, batch):
        self.shader = createWorldGridShader()
        super().__init__(x=-10, y=-10, z=0,
                         width=20, height=20,
                         color=(255, 255, 255, 255),
                         blend_src=GL_SRC_ALPHA,
                         blend_dest=GL_ONE_MINUS_SRC_ALPHA,
                         batch=batch,
                         program=self.shader)


class Line3D(pyglet.shapes.ShapeBase):
    def __init__(
            self,
            x0: float, y0: float, z0: float,
            x1: float, y1: float, z1: float,
            thickness: float,
            color: tuple[int, int, int, int] | tuple[int,
                                                     int, int] = (255, 255, 255, 255),
            batch: Batch | None = None,
            program: ShaderProgram | None = None,
    ):
        """Create a rectangle or square.

        The rectangle's anchor point defaults to the ``(x, y)``
        coordinates, which are at the bottom left.

        Args:
            x:
                The X coordinate of the rectangle.
            y:
                The Y coordinate of the rectangle.
            width:
                The width of the rectangle.
            height:
                The height of the rectangle.
            color:
                The RGB or RGBA color of the circle, specified as a
                tuple of 3 or 4 ints in the range of 0-255. RGB colors
                will be treated as having an opacity of 255.
            blend_src:
                OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
            blend_dest:
                OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
            batch:
                Optional batch to add the shape to.
            group:
                Optional parent group of the shape.
        """
        self._x1 = x0
        self._y1 = y0
        self._z1 = z0
        self._x2 = x1
        self._y2 = y1
        self._z2 = z1
        self._thickness = thickness

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        if program is None:
            program = create3DShader()
        super().__init__(24, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, batch, None, program)

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            24, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y, self._z) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0.0, 0.0, 0.0) * self._num_verts
        else:
            t = self._thickness * 0.5

            p0 = np.array([self._x1, self._y1, self._z1], dtype=np.float32)
            p1 = np.array([self._x2, self._y2, self._z2], dtype=np.float32)

            length = np.linalg.norm(p1 - p0)
            direction = (p1-p0) / length

            up = np.array([0, 1, 0], dtype=np.float32)
            x = direction
            z = np.cross(x, up)
            z /= np.linalg.norm(z)
            y = np.cross(z, x)

            R = np.column_stack((x, y, z))

            local_vertices = np.array([
                [0, -t,  t],
                [length, -t,  t],
                [length,  t,  t],
                [0,  t,  t],
                [0, -t, -t],
                [length, -t, -t],
                [length,  t, -t],
                [0,  t, -t],
            ], dtype=np.float32)

            world_vertices = (R @ local_vertices.T).T + p0
            v0, v1, v2, v3, v4, v5, v6, v7 = world_vertices

            return (
                *v0, *v1, *v2,  # Front
                *v0, *v2, *v3,

                *v4, *v5, *v6,  # Rear
                *v4, *v6, *v7,

                *v3, *v2, *v6,  # Top
                *v3, *v6, *v7,

                *v0, *v1, *v5,  # Bottom
                *v0, *v5, *v4,
            )


    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    def _update_translation(self) -> None:
        """Overwrite this method to support 3d position"""
        self._vertex_list.translation[:] = (
            self._x, self._y, self._z) * self._num_verts

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()


class Prism3D(pyglet.shapes.ShapeBase):
    def __init__(
            self,
            x: float, y: float, z: float,
            width: float, height: float, depth: float,
            color: tuple[int, int, int, int] | tuple[int,
                                                     int, int] = (255, 255, 255, 255),
            blend_src: int = GL_SRC_ALPHA,
            blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
            batch: Batch | None = None,
            group: Group | None = None,
            program: ShaderProgram | None = None,
    ):
        """Create a rectangle or square.

        The rectangle's anchor point defaults to the ``(x, y)``
        coordinates, which are at the bottom left.

        Args:
            x:
                The X coordinate of the rectangle.
            y:
                The Y coordinate of the rectangle.
            width:
                The width of the rectangle.
            height:
                The height of the rectangle.
            color:
                The RGB or RGBA color of the circle, specified as a
                tuple of 3 or 4 ints in the range of 0-255. RGB colors
                will be treated as having an opacity of 255.
            blend_src:
                OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
            blend_dest:
                OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
            batch:
                Optional batch to add the shape to.
            group:
                Optional parent group of the shape.
        """
        self._x = x
        self._y = y
        self._z = z
        self._width = width
        self._height = height
        self._depth = depth
        self._rotation = 0

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(36, blend_src, blend_dest, batch, group, program)

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            self._num_verts, self._draw_mode, self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._rgba * self._num_verts),
            translation=('f', (self._x, self._y, self._z) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
            # Centralise the rectangle
            w = self._width/2
            h = self._height/2
            d = self._depth/2

            v0 = (self._x - w, self.height - h, d)
            v1 = (self._x + w, self.height - h, d)
            v2 = (self._x + w, self.height + h, d)
            v3 = (self._x - w, self.height + h, d)
            v4 = (self._x - w, self.height - h, -d)
            v5 = (self._x + w, self.height - h, -d)
            v6 = (self._x + w, self.height + h, -d)
            v7 = (self._x - w, self.height + h, -d)

            return (
                *v0, *v1, *v2,  # Front
                *v0, *v2, *v3,  # Front
                *v4, *v5, *v6,  # Rear
                *v4, *v6, *v7,  # Rear
                *v3, *v2, *v6,  # Top
                *v3, *v6, *v7,  # Top
                *v0, *v1, *v5,  # Bottom
                *v0, *v5, *v4,  # Bottom
                *v1, *v5, *v6, # Right
                *v1, *v6, *v3, # Right
                *v0, *v4, *v7, # Left
                *v0, *v7, *v3 # Left
            )

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    @property
    def width(self) -> float:
        """Get/set width of the rectangle.

        The new left and right of the rectangle will be set relative to
        its :py:attr:`.anchor_x` value.
        """
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._update_vertices()

    @property
    def height(self) -> float:
        """Get/set the height of the rectangle.

        The bottom and top of the rectangle will be positioned relative
        to its :py:attr:`.anchor_y` value.
        """
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value
        self._update_vertices()

    def _update_translation(self) -> None:
        """Overwrite this method to support 3d position"""
        self._vertex_list.translation[:] = (self._x, self._y, self._z) * self._num_verts

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()


class Circle3D(pyglet.shapes.ShapeBase):

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        radius: float,
        segments: int | None = None,
        color: tuple[int, int, int, int] | tuple[int, int, int] = (255, 255, 255, 255),
        blend_src: int = GL_SRC_ALPHA,
        blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
        batch: Batch | None = None,
        group: Group | None = None,
        program: ShaderProgram | None = None,
    ) -> None:
        """Create a circle.

        The circle's anchor point (x, y) defaults to the center of the circle.

        Args:
            x:
                X coordinate of the circle.
            y:
                Y coordinate of the circle.
            z:
                Z coordinate of the circle.
            radius:
                The desired radius.
            segments:
                You can optionally specify how many distinct triangles
                the circle should be made from. If not specified it will
                be automatically calculated using the formula:
                `max(14, int(radius / 1.25))`.
            color:
                The RGB or RGBA color of the circle, specified as a
                tuple of 3 or 4 ints in the range of 0-255. RGB colors
                will be treated as having an opacity of 255.
            blend_src:
                OpenGL blend source mode; for example, ``GL_SRC_ALPHA``.
            blend_dest:
                OpenGL blend destination mode; for example, ``GL_ONE_MINUS_SRC_ALPHA``.
            batch:
                Optional batch to add the shape to.
            group:
                Optional parent group of the shape.
            program:
                Optional shader program of the shape.
        """
        self._x = x
        self._y = y
        self._z = z
        self._radius = radius
        self._segments = segments or max(14, int(radius / 1.25))
        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        super().__init__(
            self._segments * 3,
            blend_src,
            blend_dest,
            batch,
            group,
            program,
        )

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list(
            self._segments * 3,
            self._draw_mode,
            self._batch,
            self._group,
            position=("f", self._get_vertices()),
            colors=("Bn", self._rgba * self._num_verts),
            translation=("f", (self._x, self._y, self._z) * self._num_verts),
        )

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0, 0) * self._num_verts

        x = -self._anchor_x
        y = -self._anchor_y
        r = self._radius
        tau_segs = math.pi * 2 / self._segments

        # 3D points on the circle in local XY plane (z=0)
        points = [
            (x + r * math.cos(i * tau_segs), y + r * math.sin(i * tau_segs), 0.0)
            for i in range(self._segments)
        ]

        vertices = []
        for i, point in enumerate(points):
            # Center vertex + two edge vertices, all with z=0
            triangle = (x, y, 0.0, *points[i - 1], *point)
            vertices.extend(triangle)

        return vertices

    def _update_vertices(self) -> None:
        self._vertex_list.position[:] = self._get_vertices()

    def _update_translation(self) -> None:
        self._vertex_list.translation[:] = (self._x, self._y, self._z) * self._num_verts

    @property
    def radius(self) -> float:
        """Gets/set radius of the circle."""
        return self._radius

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()

    @radius.setter
    def radius(self, value: float) -> None:
        self._radius = value
        self._update_vertices()
