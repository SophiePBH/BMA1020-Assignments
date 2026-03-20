""" 
    Window size: 1280x720.

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


# Input
# -----
key_handler = key.KeyStateHandler()
window.push_handlers(key_handler)


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


@window.event
def on_draw():
    window.clear()

    # Camera matrices
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    shader["u_projection"] = camera.get_projection()
    shader["u_view"] = camera.get_look_at()
    prism.draw()

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    world_grid.shader["u_projection"] = camera.get_projection()
    world_grid.shader["u_view"] = camera.get_look_at()
    batch.draw()



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
