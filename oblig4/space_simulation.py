"""


MUST BE IN CORRECT DIRECTORY IN TERMINAL FOR SPACE SHIP TO LOAD PROPERLY!!!!!!!
CD INTO \oblig4



In this program, we simulate the space. We introduce stars, a planet and a
spaceship to the simulation.

Particles are now spheres. A class Sphere has been added to the library provided. ☑️

Particles spawn from at least one point in Cartesian space.That means you can choose
to create and emit the particles from multiple, defined Cartesian coordinates. ☑️

Particles spawn with colors of your choice. Once an individual particle's
color is set, it must persist throughout its lifetime. ☑️

Particles spawn with a random velocity, radius, mass and charge. The charge can
be taken to be either 1 or −1 at random, the others should take positive values
within a range which gives visually satisfying results!

Particles die after a certain amount of time, e.g. 3 seconds. ☑️

Particles collide with each other with sphere-to-sphere collision.
Allow the user to adjust the coefficient of restitution e, taking e=0.8 as a default.

Particles are subject to mutual gravitational and electromagnetic forces.
You should be able to toggle each force on/off with a keystroke.
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

glEnable(GL_DEPTH_TEST)

FPS = 60

# Objects
# -------
# Batches
batch = pyglet.graphics.Batch()
spheres_batch = pyglet.graphics.Batch()
particle_batch = pyglet.graphics.Batch()

# Particles
particles = []
gravity = -3

# Spaceship
spaceship_model = lib.shapes.CustomModel(filepath="data/spaceship.obj",
                                         x=0.0, y=0.0, z=0.0,
                                         size=1)

# The world grid helps us navigating the 3d world space
world_grid = lib.shapes.WorldGrid(batch)

# Camera
# ------
# We introduce the camera as a concept. It is our eyes into the 3d world.
camera = lib.Camera(width=window.width, height=window.height,
                    fov=60,  # Measured in degrees
                    near=0.01, far=100.0)

# Camera position
camera.x = 3
camera.y = 2
camera.z = 3

# Input
# -----
key_handler = key.KeyStateHandler()
window.push_handlers(key_handler)


class Particle():
    def __init__(self, batch, spawnpoint):
        # TODO: Add mass and charge
        #       Add collision and mutual gravity stuff
        
        # Lifetime
        self.lifetime = 3 * FPS
        
        # Position
        self.x = spawnpoint[0]
        self.y = spawnpoint[0]
        self.z = spawnpoint[0]

        # Angle
        self.theta = random.uniform(-np.pi, np.pi)
        self.phi = random.uniform(-np.pi, np.pi)

        # Speed and velocity
        self.speed = random.randint(1, 5)
        self.velocity = np.array([self.speed * np.sin(self.phi) * np.cos(self.theta),
                                  self.speed * np.sin(self.phi) * np.sin(self.theta),
                                  self.speed * np.cos(self.phi)])

        # Size for width, height and depth
        self.radius = random.uniform(0.1, 0.2)

        # Colour
        self.R = 255
        self.G = [193, 154, 116, 77, 0]
        self.B = 0

        # The particles shape
        self.shape = lib.Sphere(x=self.x, y=self.y, z=self.z,
                                         radius=self.radius,
                                         color=(self.R, self.G[random.randint(0, 4)], self.B, 255),
                                         batch=batch)
        
    def move(self, dt):
        # Calculate and add gravities effect
        self.velocity[1] += dt * gravity

        # Calculate new position of particle
        new_position = dt * lib.transformations.translate(self.velocity[0],
                                                          self.velocity[1],
                                                          self.velocity[2])
        
        # Change the particle's position
        self.shape.x += new_position[0][3]
        self.shape.y += new_position[1][3]
        self.shape.z += new_position[2][3]


def on_update(delta: float):
    global camera

    # TODO: Proper camera movement. Janky rn
    movement_step = np.pi/2 * delta *3

    if key_handler[key.W]:
        camera.y += movement_step
    if key_handler[key.S]:
        camera.y -= movement_step
    if key_handler[key.D]:
        camera.x += movement_step
    if key_handler[key.A]:
        camera.x -= movement_step

    global particles
    for particle in particles:
        if(particle.lifetime <= 0):
            particles = np.delete(particles, np.where(particles == particle))
        else:
            particle.move(delta)
            particle.lifetime -= 1


# Creating particles
def particle_emitter(amount):
    spawnpoint = [random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)]

    global particles
    particles = np.append(particles, [Particle(particle_batch, spawnpoint) for _ in range(amount)])

def create_particles(dt):
    particle_emitter(random.randint(15, 20))


@window.event
def on_draw():
    window.clear()
    window.projection = camera.get_projection()
    window.view = camera.get_look_at()
    
    # spaceship_model.draw()

    particle_batch.draw()
    batch.draw()


pyglet.clock.schedule_interval(on_update, 1/FPS)
pyglet.clock.schedule_interval(create_particles, 1)
pyglet.app.run()