"""
This is an in-class demo. Move it to Oblig3's root directory to try it out.
"""

import numpy as np
import pyglet
from pyglet.window import key # For the mouse-on-drag event
import lib
from pyglet.gl import *


# Window properties
# -----------------
window = pyglet.window.Window()
window.width = 1200
window.height = 720

# Other attributes
# ----------------
glEnable(GL_DEPTH_TEST)

# Create objects
# --------------
shader = lib.create3DShader()
size = 3

wireframe_batch = pyglet.graphics.Batch()
boundary_box = lib.shapes.Prism3D(x=0, y=-size/2, z=0,
                           width=size, height=size, depth=size,
                           batch=wireframe_batch, program=shader)

solid_batch = pyglet.graphics.Batch()
particle = lib.shapes.Prism3D(x=3, y=3, z=0,
                              width=1, height=1, depth=1,
                              color=(255, 0, 0, 255),
                              batch=solid_batch, program=shader)

world = lib.WorldGrid(solid_batch)

# Create camera
# -------------
camera = lib.Camera(width=window.width, height=window.height,
                    fov=60,
                    near=0.01, far=1000.0)

camera.distance = 10
camera.phi = np.pi/6
camera.theta = np.pi/4


@window.event
def on_draw():
    window.clear()

    world.shader["u_projection"] = camera.get_projection()
    world.shader["u_view"] = camera.get_look_at()

    shader["u_projection"] = camera.get_projection()
    shader["u_view"] = camera.get_look_at()

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    wireframe_batch.draw()


    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    solid_batch.draw()


pyglet.app.run()