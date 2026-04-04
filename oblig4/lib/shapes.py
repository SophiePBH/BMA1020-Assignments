from pyglet.graphics import Batch, Group
import pyglet
from typing import Sequence
from pyglet.graphics.shader import ShaderProgram
import random
from pyglet.gl import GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA
from icosphere import icosphere
import math
from .model_importer import load_obj



vertex_source = """#version 150 core
    in vec3 position;
    in vec3 translation;
    in vec4 colors;

    in float rotation;

    out vec4 vertex_colors;

    uniform WindowBlock
    {
        mat4 projection;
        mat4 view;
    } window;

    uniform mat4 m_rotation = mat4(1.0);
    mat4 m_translate = mat4(1.0);

    void main()
    {
        m_translate[3][0] = translation.x;
        m_translate[3][1] = translation.y;
        m_translate[3][2] = translation.z;
        gl_Position = window.projection * window.view * m_translate * m_rotation * vec4(position, 1.0);
        vertex_colors = colors;
    }
"""

fragment_source = """#version 150 core
    in vec4 vertex_colors;
    out vec4 final_color;

    void main()
    {
        final_color = vertex_colors; //vec4(1.0, 1.0, 1.0, 1.0);
        // No GL_ALPHA_TEST in core, use shader to discard.
        if(final_color.a < 0.01){
            discard;
        }
    }
"""

world_grid_vert = """
#version 410 core

/**
 * Shader for rendering an infinite world grid.
 *
 * @details The code is taken from Marie at:
 * <a href="http://asliceofrendering.com/scene%20helper/2020/01/05/InfiniteGrid/">
 * asliceofrendering.com
 * </a>
 * License: <a href="https://github.com/BugzTroll/bugztroll.github.io/blob/master/LICENSE">
 * MIT License </a>
 *
 * @details It has been adjusted to suit the needs for this project.
 */

in vec3 position;

out vec3 nearPoint;
out vec3 farPoint;

out mat4 fragProj;
out mat4 fragView;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

/**
 * Unproject point from clip space to world space.
 */
vec3 UnprojectPoint(float x, float y, float z, mat4 view, mat4 projection) {
    mat4 viewInv = inverse(view);
    mat4 projInv = inverse(projection);
    vec4 unprojectedPoint =  viewInv * projInv * vec4(x, y, z, 1.0);
    return unprojectedPoint.xyz / unprojectedPoint.w;
}

// normal vertice projection
void main() {
    fragProj = window.projection;
    fragView = window.view;

    nearPoint = UnprojectPoint(position.x, position.y, 0.0, fragView, fragProj).xyz; // unprojecting on the near plane
    farPoint = UnprojectPoint(position.x, position.y, 1.0, fragView, fragProj).xyz; // unprojecting on the far plane
    gl_Position = vec4(position, 1.0);
}
"""

world_grid_frag = """
#version 410 core

/**
 * Shader for rendering an infinite world grid.
 *
 * @details The code is taken from Marie at:
 * <a href="http://asliceofrendering.com/scene%20helper/2020/01/05/InfiniteGrid/">
 * asliceofrendering.com
 * </a>
 * License: <a href="https://github.com/BugzTroll/bugztroll.github.io/blob/master/LICENSE">
 * MIT License </a>
 *
 * @details It has been adjusted to suit the needs for this project.
 */

in vec3 nearPoint;
in vec3 farPoint;
out vec4 outColor;

in mat4 fragView;
in mat4 fragProj;

// Near and far clip from camera frustum
uniform float u_nearClip = 0.01;
uniform float u_farClip = 100.0;

uniform vec3 lineColor = vec3(0.1);
uniform float tileScale = 10.0;

uniform float axisWidth = 0.5;
float aWidth = axisWidth / 2.0;

vec4 grid(vec3 fragPos3D, float scale, bool drawAxis) {
    vec2 coord = fragPos3D.xz * scale;
    vec2 derivative = fwidth(coord);
    vec2 grid = abs(fract(coord - 0.5) - 0.5) / derivative;
    float line = min(grid.x, grid.y);
    float minimumz = min(derivative.y, 1);
    float minimumx = min(derivative.x, 1);
    vec4 color = vec4(lineColor, 1.0 - min(line, 1.0));
    // z axis
    if(fragPos3D.x > -aWidth * minimumx && fragPos3D.x < aWidth * minimumx)
    color.z = 1.0;
    // x axis
    if(fragPos3D.z > -aWidth * minimumz && fragPos3D.z < aWidth * minimumz)
    color.x = 1.0;
    return color;
}
float computeDepth(vec3 pos) {
    vec4 clip_space_pos = fragProj * fragView * vec4(pos.xyz, 1.0);
    return (clip_space_pos.z / clip_space_pos.w);
}
float computeLinearDepth(vec3 pos) {
    vec4 clip_space_pos = fragProj * fragView * vec4(pos.xyz, 1.0);
    float clip_space_depth = (clip_space_pos.z / clip_space_pos.w) * 2.0 - 1.0; // put back between -1 and 1
    float linearDepth = (2.0 * u_nearClip * u_farClip) / (u_farClip + u_nearClip - clip_space_depth * (u_farClip - u_nearClip)); // get linear value between 0.01 and 100
    return linearDepth / u_farClip; // normalize
}
void main() {
    float t = -nearPoint.y / (farPoint.y - nearPoint.y);
    vec3 fragPos3D = nearPoint + t * (farPoint - nearPoint);

    gl_FragDepth = computeDepth(fragPos3D);

    float linearDepth = computeLinearDepth(fragPos3D);
    float fading = max(0, (0.5 - linearDepth));

    outColor = (grid(fragPos3D, 1/tileScale, true) + grid(fragPos3D, 1, true))* float(t > 0); // adding multiple resolution for the grid
    outColor.a *= fading;
}

"""


class Sphere(pyglet.shapes.ShapeBase):
    def __init__(
        self,
        x: float, y: float, z: float,
        radius: float,
        color: tuple,
        batch: Batch | None = None
    ):
        """Create a square or rectangle grid.

        The grid's anchor point defaults to the ``(x, y)``
        coordinates, which are at the bottom left.
        Args:
        x:
            The X coordinate of the grid.
        y:
            The Y coordinate of the grid.
        z:
            The Z coordinate of the grid.
        width:
            The width of the grid.
        height:
            The height of the grid.
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
        self._color = color
        self._radius = radius

        subdivision_frequency = 6
        # num_vertices = 12 + 10 * (4**subdivision_frequency - 1)
        vertices, indices = icosphere(subdivision_frequency)
        vertices *= self._radius
        num_vertices = vertices.shape[0]
        indices = indices.flatten().tolist()
        vertices = vertices.flatten().tolist()

        self._program = pyglet.gl.current_context.create_program((vertex_source, 'vertex'),
                                                                 (fragment_source, 'fragment'))

        self._verts = vertices
        self._indices = indices
        super().__init__(
            num_vertices,
            pyglet.gl.GL_SRC_ALPHA,
            pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
            batch,
            None,
            self._program,
        )

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list_indexed(
            self._num_verts, self._draw_mode,
            self._indices,
            self._batch, self._group,
            position=('f', self._get_vertices()),
            colors=('Bn', self._color * self._num_verts),
            translation=('f', (self._x, self._y, self._z) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0, 0) * self._num_verts
        else:
            return self._verts

    def _update_vertices(self):
        self._vertex_list.position[:] = self._get_vertices()

    def _update_translation(self) -> None:
        self._vertex_list.translation[:] = (
            self._x, self._y, self._z) * self._num_verts

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()



class CustomModel(pyglet.shapes.ShapeBase):
    def __init__(
        self,
        filepath: str,
        x: float, y: float, z: float,
        size: float,
        batch: Batch | None = None,
    ):
        """Import an OBJ model"""

        self._x = x
        self._y = y
        self._z = z

        self._program = pyglet.gl.current_context.create_program((vertex_source, 'vertex'),
                                                                 (fragment_source, 'fragment'))
        
        vertices, indices = load_obj(filepath)

        self._verts = vertices * size
        self._indices = indices

        # Build vertex list structure (just like Rectangle)
        super().__init__(
            len(vertices) // 3,
            pyglet.gl.GL_SRC_ALPHA,
            pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
            batch,
            None,
            self._program,
        )

    def _create_colours(self):
        c = []
        for i in range(self._num_verts):
            # c.extend((150, 150, 150, 255))
            c.extend((random.randint(0, 255), random.randint(
                0, 255), random.randint(0, 255), 255))
        return c

    def _create_vertex_list(self) -> None:
        self._vertex_list = self._program.vertex_list_indexed(
            self._num_verts, self._draw_mode,
            self._indices,
            self._batch, self._group,
            position=('f', self._get_vertices()),
            # self._rgba * self._num_verts),
            colors=('Bn', self._create_colours()),
            translation=('f', (self._x, self._y, self._z) * self._num_verts))

    def _get_vertices(self) -> Sequence[float]:
        if not self._visible:
            return (0, 0) * self._num_verts
        else:
            return self._verts

    def _update_vertices(self):
        self._vertex_list.position[:] = self._get_vertices()
        
    def _update_translation(self) -> None:
        self._vertex_list.translation[:] = (self._x, self._y, self._z) * self._num_verts

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = value
        self._update_translation()


class Rectangle3D(pyglet.shapes.ShapeBase):
    def __init__(
            self,
            x: float, y: float, z: float,
            width: float, height: float,
            color: tuple[int, int, int, int] | tuple[int,
                                                     int, int] = (255, 255, 255, 255),
            batch: Batch | None = None,
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

        self._program = pyglet.gl.current_context.create_program((vertex_source, 'vertex'),
                                                                 (fragment_source, 'fragment'))

        super().__init__(6, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, batch, None, self._program)

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
        self.shader = pyglet.gl.current_context.create_program((world_grid_vert, 'vertex'),
                                                               (world_grid_frag, 'fragment'))

        super().__init__(x=-10, y=-10, z=0,
                         width=20, height=20,
                         color=(255, 255, 255, 255),
                         blend_src=GL_SRC_ALPHA,
                         blend_dest=GL_ONE_MINUS_SRC_ALPHA,
                         batch=batch,
                         program=self.shader)


class Circle3D(pyglet.shapes.ShapeBase):
    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        radius: float,
        segments: int | None = None,
        color: tuple[int, int, int, int] | tuple[int,
                                                 int, int] = (255, 255, 255, 255),
        batch: Batch | None = None,
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

        self._program = pyglet.gl.current_context.create_program((vertex_source, 'vertex'),
                                                                 (fragment_source, 'fragment'))

        super().__init__(
            self._segments * 3,
            GL_SRC_ALPHA,
            GL_ONE_MINUS_SRC_ALPHA,
            batch,
            None,
            self._program,
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
        self._vertex_list.translation[:] = (
            self._x, self._y, self._z) * self._num_verts

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
