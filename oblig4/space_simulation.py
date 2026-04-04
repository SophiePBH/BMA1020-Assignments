"""


MUST RUN PROGRAM THROUGH TERMINAL FOR SPACE SHIP TO LOAD PROPERLY!!!!!!!
CD INTO \oblig4 AND RUN COMMAND python space_simulation.py



In this program, we simulate the space. We introduce stars, a planet and a
spaceship to the simulation.

Particles are now spheres. A class Sphere has been added to the library provided.

Particles spawn from at least one point in Cartesian space.That means you can choose
to create and emit the particles from multiple, defined Cartesian coordinates.

Particles spawn with colors of your choice. Once an individual particle's
color is set, it must persist throughout its lifetime.

Particles spawn with a random velocity, radius, mass and charge.The charge can
be taken to be either 1 or −1 at random, the others should take positive values
within a range which gives visually satisfying results!

Particles die after a certain amount of time, e.g. 3 seconds.

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

# Window properties
# -----------------
window = pyglet.window.Window()
window.width = 1280
window.height = 720

glEnable(GL_DEPTH_TEST)

# Objects
# -------
batch = pyglet.graphics.Batch()
spheres_batch = pyglet.graphics.Batch()

sphere = lib.Sphere(x=-2, y=2, z=0, radius=1, color=(255,0,255,255), batch=spheres_batch)

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

# Camera position with spherical coordinates
camera.x = 3
camera.y = 2
camera.z = 3

# Input
# -----
key_handler = key.KeyStateHandler()
window.push_handlers(key_handler)

@window.event
def on_draw():
    window.clear()
    window.projection = camera.get_projection()
    window.view = camera.get_look_at()
    
    spaceship_model.draw()
    spheres_batch.draw()

    batch.draw()


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


pyglet.clock.schedule_interval(on_update, 1/60)
pyglet.app.run()