""" 
    Window size: 1280x720. ☑️

    Particles spawn with a random size. You are free to choose a reasonable size.
    
    All particles spawn from the same Cartesian coordinate (it's okay
    to move the spawning point with keyboard or mouse inputs during runtime).
    
    Particles spawn with colors of your choice.
    Once an invididual particle's color is set, it must
    persist throughout its lifetime.
    
    Particles spawn with a random velocity.
    
    Particles are affected by gravitational force.
    
    Particles spawn at a fixed rate.
    
    There is a boundary box that particles can only live in.
    Once a particle steps outside the boundary, it dies.
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

# Sees what is closest to the camera
glEnable(GL_DEPTH_TEST) 

# Shaders
# -----------------
shader = lib.create3DShader()

# Objects
# -------
# The world grid helps us navigating the 3d world space
grid_batch = pyglet.graphics.Batch()
world_grid = lib.shapes.WorldGrid(grid_batch)

# Camera
# ------
# We introduce the camera as a concept. It is our eyes into the 3d world.
camera = lib.Camera(width=window.width, height=window.height,
                    fov=60,  # Measured in degrees
                    near=0.01, far=1000.0)

# Objects
# -------
size = 3
prism = lib.shapes.Prism3D(x=0, y=-size/2, z=0,
                           width=size, height=size, depth=size,
                           color=(190, 30, 160, 255),
                           # You can add the prism to batch, also
                           # batch=batch,
                           program=shader)

# Camera position with spherical coordinates
camera.distance = 10
camera.phi = np.pi/6
camera.theta = np.pi / 4

# Particles
particle_batch = pyglet.graphics.Batch()
particles = []


# Input
# -----
key_handler = key.KeyStateHandler()
window.push_handlers(key_handler)


class Particle():
    def __init__(self, batch, shader):
        # Position
        self.x = 0
        self.y = size/2
        self.z = 0

        # Angle
        self.theta = random.uniform(-np.pi, np.pi)
        self.phi = random.uniform(-np.pi, np.pi)

        # Speed and velocity
        self.speed = random.randint(1, 2)
        self.velocity = np.array([self.speed * np.sin(self.phi) * np.cos(self.theta),
                                  self.speed * np.sin(self.phi) * np.sin(self.theta),
                                  self.speed * np.cos(self.phi)])

        # Size for width, height and depth
        self.size = random.uniform(0.1, 0.2)

        # Colour
        self.R = random.randint(0, 255)
        self.G = random.randint(0, 255)
        self.B = random.randint(0, 255)

        self.shape = lib.shapes.Prism3D(x=self.x, y=self.y, z=self.z,
                                         width=self.size, height=self.size, depth=self.size,
                                         color=(self.R, self.G, self.B),
                                         batch=batch, program=shader)
        
    def move(self, dt):
        # Calculate new position of particle
        new_position = dt * lib.transformations.translate(self.velocity[0],
                                                           self.velocity[1],
                                                           self.velocity[2])
        # Change the particle's position
        self.shape.x += new_position[0][3]
        self.shape.y += new_position[1][3]
        self.shape.z += new_position[2][3]


# Start
def start():
    particle_emitter(10)


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

    # Move particles
    global particles
    for particle in particles:
        particle.move(delta)


# Creating particles
def particle_emitter(amount):
    global particles
    particles = np.append(particles, [Particle(particle_batch, shader) for _ in range(amount)])

def create_particles(dt):
    particle_emitter(random.randint(5, 10))


@window.event
def on_draw():
    window.clear()

    # Camera matrices
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    shader["u_projection"] = camera.get_projection()
    shader["u_view"] = camera.get_look_at()
    prism.draw()

    # Particles
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    particle_batch.draw()

    # World grid
    world_grid.shader["u_projection"] = camera.get_projection()
    world_grid.shader["u_view"] = camera.get_look_at()
    grid_batch.draw()

    



@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    global camera

    min_distance = 1

    if camera.distance <= min_distance and scroll_y == 1:
        camera.distance = min_distance
    else:
        scroll_speed = -scroll_y
        camera.distance += scroll_speed


start()
pyglet.clock.schedule_interval(on_update, 1/60)
pyglet.clock.schedule_interval(create_particles, 1)
pyglet.app.run()