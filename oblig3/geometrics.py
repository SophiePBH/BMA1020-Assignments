""" 
    Window size: 1280x720. ☑️

    Implement a thick lens placed at the origin of the 3D world. 

    The lens could be made by either Circle3D, or Line3D from lib. ☑️

    Given a ray origin and direction, find the nearest valid intersection with the lens surface. ☑️

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
reflected_batch = pyglet.graphics.Batch()
refracted_batch = pyglet.graphics.Batch()
lightsource = [0, 0, 6]
rays = []
refracted_rays = []
refracted_rays2 = []

# Camera position with spherical coordinates
camera.distance = 10
camera.phi = np.pi/6
camera.theta = np.pi / 4

# Input
# -----
key_handler = key.KeyStateHandler()
window.push_handlers(key_handler)


class Lens():
    def __init__(self, position):
        # Lens isn't thick like the task wants it to be. IDK how to fix lol xD rofl
        self.position = position
        # A vector on the lens
        self.v1 = np.array([position[0]+1, position[1]+2, position[2]]) - self.position
        # Another vector on the lens
        self.v2 = np.array([position[0]-1, position[1]+1, position[2]]) - self.position
        # Lens normal vector
        # self.norm = np.cross(self.v1, self.v2)
        self.norm = np.array([0,0,1])
        # Lens' centre
        self.centre = np.array([self.position[0], self.position[1]/2, self.position[2]])
        # Lens radius
        self.radius = 5

        self.lens = lib.shapes.Circle3D(x=self.position[0], y=self.position[1], z=self.position[2],
                                radius=self.radius,
                                segments=30,
                                color=(255,255,255, 100),
                                batch=lens_batch, program=shader)

class Ray():
    def __init__(self, start_pos, colour, batch, n_1, n_2, end_pos: tuple[float, float, float] | None = None, lens: Lens | None = None):
        # Rendering batch
        self.batch = batch

        self.n_1 = n_1
        self.n_2 = n_2

        # Start position
        self.x0 = start_pos[0]
        self.y0 = start_pos[1]
        self.z0 = start_pos[2]
        self.start_pos = np.array([self.x0, self.y0, self.z0])

        # Length of ray
        self.length = 20

        # Angles
        self.theta = random.uniform(-np.pi, np.pi)
        self.phi = random.uniform(-np.pi, np.pi)

        # End position
        if end_pos is None:
            self.x1 = self.length * np.sin(self.phi) * np.cos(self.theta)
            self.y1 = self.length * np.sin(self.phi) * np.sin(self.theta)
            self.z1 = -self.length
        else:
            self.x1 = end_pos[0]
            self.y1 = end_pos[1]
            self.z1 = end_pos[2]

        # Vector of line
        self.vector = np.array([self.x1, self.y1, self.z1]) - self.start_pos

        # Thickness
        self.thickness = 0.02

        # Colour
        self.R = colour[0]
        self.G = colour[1]
        self.B = colour[2]

        # Calculate intersection point and update end position of collision
        # is detected
        if lens is not None:
            self.intersection = Intersection(self, lens)
            self.reflected_refracted = self.intersection
        
        # Ray shape
        self.shape = lib.shapes.Line3D(x0=self.x0, y0=self.y0, z0=self.z0,
                                       x1=self.x1, y1=self.y1, z1=self.z1,
                                       thickness=self.thickness,
                                       color=(self.R, self.G, self.B, 100),
                                       batch=self.batch, program=shader)
        
def Intersection(ray, lens):
    # Google what this stuff does. It works but idk why
    # https://rosettacode.org/wiki/Find_the_intersection_of_a_line_with_a_plane

    # Veeeery small positiv number for margin of error
    epsilon = 1e-6

    # Scalar represents how much lens_norm and ray vector align
    scalar = np.dot(lens.norm, ray.vector)
    # If the scalar is greater than 0, there is an intersection
    if np.abs(scalar) >= epsilon:
        # What is 'w' 🙏😭 (think it might be a point?)
        w = ray.start_pos - lens.position 
        # t(?) lowkey not sure what it is tho
        t = np.dot(-lens.norm, w) / scalar
        intersection_point = w + t * ray.vector + lens.position

        # Check if intersection is on the lens
        on_plane = np.linalg.norm(lens.centre - intersection_point)

        # If intersection is within the the lens radius, create new end position
        # for ray
        if(on_plane <= lens.radius):
            ray.x1 = intersection_point[0]
            ray.y1 = intersection_point[1]
            ray.z1 = intersection_point[2]

            ray.length = np.linalg.norm(ray.start_pos - intersection_point)

            Refract(ray, lens, intersection_point)
            reflected_ray = Reflect(ray, lens, intersection_point)
            return reflected_ray


def Refract(ray, lens, intersection):
    ray_norm = ray.vector/ray.length
    normal_norm = lens.norm/np.linalg.norm(lens.norm)

    scalar = np.dot(normal_norm, ray_norm)
    if scalar < 0:
        normal_norm *= -1

    ratio = ray.n_1/ray.n_2

    end_pos = ratio * ray_norm + normal_norm * np.sqrt(1 - ratio**2 * (1 - (scalar**2))) * ratio * normal_norm * scalar
    
    if ray.n_1 == 1:
        colour=(255,67,255)
        global refracted_rays
        refracted_rays = np.append(refracted_rays, [Ray(start_pos=intersection,
                                                        colour=colour, batch=refracted_batch,
                                                        end_pos=end_pos, lens=lens2,
                                                        n_1=ray.n_2, n_2=ray.n_1)])

    elif ray.n_1 == 1.5:
        colour=(255,255,67)
        global refracted_rays2
        refracted_rays2 = np.append(refracted_rays2, [Ray(start_pos=intersection,
                                                        colour=colour, batch=refracted_batch,
                                                        end_pos=end_pos, n_1=ray.n_2, n_2=ray.n_1)])


def Reflect(ray, lens, intersection):
    ray_norm = ray.vector/ray.length
    normal_norm = lens.norm/np.linalg.norm(lens.norm)

    reflected_light = ray_norm - 2 * (np.dot(ray_norm, normal_norm) * normal_norm)
    end_pos = intersection + reflected_light * ray.length

    if ray.n_1 == 1:
        reflected = Ray(start_pos=intersection,
                        colour=(67,255,67), batch=reflected_batch,
                        end_pos=end_pos, n_1=ray.n_1, n_2=ray.n_2)
    else:
        reflected = Ray(start_pos=intersection,
                        colour=(67,67,255), batch=reflected_batch,
                        end_pos=end_pos, n_1=ray.n_1, n_2=ray.n_2)
    return reflected
    

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

lens1 = Lens(position=np.array([0, 0, 0]))
lens2 = Lens(position=np.array([0, 0, -1]))

# Creates 250 rays
rays = np.append(rays, [Ray(start_pos=lightsource,
                            colour=(252,249,217), batch=rays_batch,
                            lens=lens1, n_1=1, n_2=1.5)
                            for _ in range(250)])

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
    reflected_batch.draw()
    refracted_batch.draw()
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
