""" 
    Window size: 1280x720. ☑️

    Implement a thick lens placed at the origin of the 3D world.

    The lens could be made by either Circle3D, or Line3D from lib. ☑️

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


class Lens():
    def __init__(self):
        # Lens isn't thick like the task wants it to be. IDK how to fix lol xD rofl
        self.position = np.array([0, 0, -10])
        # A vector on the lens
        self.v1 = np.array([1, 2, -10]) - self.position
        # Another vector on the lens
        self.v2 = np.array([-1, 1, -10]) - self.position
        # Lens normal vector
        self.norm = np.cross(self.v1, self.v2)
        # Lens' centre
        self.centre = np.array([self.position[0], self.position[1]/2, self.position[2]])
        # Lens radius
        self.radius = 5

        self.lens = lib.shapes.Circle3D(x=self.position[0], y=self.position[1], z=self.position[2],
                                radius=self.radius,
                                segments=30,
                                color=(255,255,255, 128),
                                batch=lens_batch, program=shader)

class Ray():
    def __init__(self, lens):
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
        # self.x1 = self.length * np.sin(self.phi) * np.cos(self.theta)
        self.x1 = self.length * 0.2
        # self.y1 = self.length * np.sin(self.phi) * np.sin(self.theta)
        self.y1 = self.length * 0.1
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
        Intersection(self, lens)
        
        # Ray shape
        self.shape = lib.shapes.Line3D(x0=self.x0, y0=self.y0, z0=self.z0,
                                       x1=self.x1, y1=self.y1, z1=self.z1,
                                       thickness=self.thickness,
                                       color=(self.R, self.G, self.B, 100),
                                       batch=rays_batch, program=shader)
        
def Intersection(ray, lens):
    # Google what this stuff does. It works but idk why
    # https://rosettacode.org/wiki/Find_the_intersection_of_a_line_with_a_plane

    # Veeeery small positiv number for margin of error
    epsilon = 1e-6

    # Scalar represents how much lens_norm and ray vector align
    scalar = np.dot(lens.norm, ray.vector)
    # If the scalar is greater than 0, there is an intersection
    if np.abs(scalar) >= epsilon:
        # What is 'w' 🙏😭
        w = lightsource - lens.position
        # What is 'si' 🙏😭
        si = np.dot(-lens.norm, w) / scalar
        intersection_point = w + si * ray.vector + lens.position

        # Check if intersection is on the lens
        on_plane = np.linalg.norm(lens.centre - intersection_point)

        # If intersection is within the the lens radius, create new end position
        # for ray
        if(on_plane <= lens.radius):
            ray.x1 = intersection_point[0]
            ray.y1 = intersection_point[1]
            ray.z1 = intersection_point[2]

            ray.length = np.linalg.norm(lightsource-intersection_point)

            Reflect(ray, intersection_point)


def Refract(ray):
    pass


def Reflect(ray, intersection):
    ray.normalized = ray.vector/ray.length
    

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

lens = Lens()

# Creates 250 rays
rays = np.append(rays, [Ray(lens) for _ in range(1)])

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
