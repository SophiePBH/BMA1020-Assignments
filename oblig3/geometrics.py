""" 
    Window size: 1280x720. ☑️

    Implement a thick lens placed at the origin of the 3D world.

    The lens could be made by either Circle3D, or Line3D from lib.

    Given a ray origin and direction, find the nearest valid intersection with the lens surface.

    The ray should be made with Line3D from lib.
    The ray should be at a point source.

    When there is an intersection, the rays should either reflect or refract.
    Use Snell's Law to compute refraction. If total internal reflection occurs, reflect the ray instead.

    Refracted and reflected segments should have different colors.
"""

import numpy as np
import pyglet
from pyglet.window import key
import lib
from pyglet.gl import *
import random

# Window properties
# -----------------
window = pyglet.window.Window()
window.width = 1280
window.height = 720

# Shaders
# -----------------
shader = lib.create3DShader()

# Objects
# -------
batch = pyglet.graphics.Batch()

# The world grid helps us navigating the 3d world space
world_grid = lib.shapes.WorldGrid(batch)

# Camera
# ------
# We introduce the camera as a concept. It is our eyes into the 3d world.
camera = lib.Camera(width=window.width, height=window.height,
                    fov=60,  # Measured in degrees
                    near=0.01, far=1000.0)

# Objects
# -------
# Lens
lens_batch = pyglet.graphics.Batch()
# Lens isn't thick like the task wants it to be. IDK how to fix lol xD rofl
lens_position = np.array([0, 3, -10])
# A vector on the lens
lens_v1 = np.array([1, 0, -10]) - lens_position
# Another vector on the lens
lens_v2 = np.array([-1, 2, -10]) - lens_position
# Lens normal vector
lens_norm = np.cross(lens_v1, lens_v2)

lens = lib.shapes.Circle3D(x=lens_position[0], y=lens_position[1], z=lens_position[2],
                           radius=5,
                           color=(255,255,255, 128),
                           batch=lens_batch, program=shader)

# Lightsource and rays
rays_batch = pyglet.graphics.Batch()
lightsource = [0, 1.5, 2]
rays = []

# Camera position with spherical coordinates
camera.distance = 10
camera.phi = np.pi/6
camera.theta = np.pi / 4

# Input
# -----
key_handler = key.KeyStateHandler()
window.push_handlers(key_handler)


class Ray():
    def __init__(self):
        # Start position
        self.x0 = lightsource[0]
        self.y0 = lightsource[1]
        self.z0 = lightsource[2]

        # Length of ray
        self.length = 20

        # Angles
        self.theta = random.uniform(-np.pi, np.pi)
        self.phi = random.uniform(-np.pi, np.pi)

        # End position
        self.x1 = self.length * np.sin(self.phi) * np.cos(self.theta)
        # self.x1 = self.length * 0.2
        self.y1 = self.length * np.sin(self.phi) * np.sin(self.theta)
        # self.y1 = self.length * 0.1
        self.z1 = -self.length

        # Vector of line
        self.vector = np.array([self.x1, self.y1, self.z1]) - lightsource

        # Thickness
        self.thickness = 0.02

        # Colour
        self.R = 252
        self.G = 249
        self.B = 217

        # Calculate intersection point and update end position of collision
        # is detected
        Intersection(self)
        self.x1 = Intersection(self)[0]
        self.y1 = Intersection(self)[1]
        self.z1 = Intersection(self)[2]
        
        # Ray shape
        self.shape = lib.shapes.Line3D(x0=self.x0, y0=self.y0, z0=self.z0,
                                       x1=self.x1, y1=self.y1, z1=self.z1,
                                       thickness=self.thickness,
                                       color=(self.R, self.G, self.B, 100),
                                       batch=rays_batch, program=shader)


def Intersection(ray):
    # Google what this stuff does. It works but idk why
    # https://rosettacode.org/wiki/Find_the_intersection_of_a_line_with_a_plane

    # TODO: adjust code so intersection is only detected within the lens and
    #       not the entire plane thingy

    epsilon = 1e-6

    # Whaddahelly is 'ndotu' 🙏😭
    ndotu = lens_norm.dot(ray.vector)
    if abs(ndotu) < epsilon:
        return None
    # What is 'w' 🙏😭
    w = lightsource - lens_position
    # What is 'si' 🙏😭
    si = -lens_norm.dot(w) / ndotu
    intersection_point = w + si * ray.vector + lens_position
    
    return intersection_point


def on_update(delta: float):
    global camera

    # Move the camera
    movement_step = np.pi/2 * delta

    if key_handler[key.W]:
        camera.phi += movement_step
    if key_handler[key.S]:
        camera.phi -= movement_step
    if key_handler[key.D]:
        camera.theta += movement_step
    if key_handler[key.A]:
        camera.theta -= movement_step

# Creates 100 rays
rays = np.append(rays, [Ray() for _ in range(500)])

@window.event
def on_draw():
    window.clear()

    # Camera matrices
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    shader["u_projection"] = camera.get_projection()
    shader["u_view"] = camera.get_look_at()
    # prism.draw()

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    world_grid.shader["u_projection"] = camera.get_projection()
    world_grid.shader["u_view"] = camera.get_look_at()
    batch.draw()

    rays_batch.draw()
    lens_batch.draw()


@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    global camera

    min_distance = 1

    if camera.distance <= min_distance and scroll_y == 1:
        camera.distance = min_distance
    else:
        scroll_speed = -scroll_y
        camera.distance += scroll_speed


pyglet.clock.schedule_interval(on_update, 1/60)
pyglet.app.run()
