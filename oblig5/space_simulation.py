"""
In this program, we simulate planet and terrain generation with interesting
patterns.

You can implement code in this script. You can use the template script
'space_simulation.py' from assignment 4 as a start.
"""

import numpy as np
import pyglet
from pyglet.window import key
import lib
from pyglet.gl import *
from icosphere import icosphere

# Window properties
# -----------------
window = pyglet.window.Window()
WIDTH = 1280
HEIGHT = 720
window.width = WIDTH
window.height = HEIGHT

glEnable(GL_DEPTH_TEST)

FPS = 60

# Global State
# ------------
# The global state ensures that the correct parameters and values are uploaded
# to the shader/GPU. We update the state in the draw function.
global_state = lib.GlobalState()


# Objects
# -------
# Batches
batch = pyglet.graphics.Batch()
planet_batch = pyglet.graphics.Batch()
widgets_batch = pyglet.graphics.Batch()
world_batch = pyglet.graphics.Batch()

# Spaceship
spaceship_model = lib.shapes.CustomModel(x=25, y=-10, z=0,
                                         scale=1.0)

# Lightsource
point_light = lib.shapes.Sphere(x=0, y=10, z=0, radius=2,
                               color=(255,255,255,255), batch=batch)

# The world grid helps us navigating the 3d world space
world_grid = lib.shapes.WorldGrid(world_batch)

# Camera
# ------
# We introduce the camera as a concept. It is our eyes into the 3d world.
camera = lib.Camera(width=WIDTH, height=HEIGHT,
                    fov=60,  # Measured in degrees
                    near=0.01, far=100.0)

# Camera position
camera.x = 24.5
camera.y = -1
camera.z = 0

# Input
# -----
key_handler = key.KeyStateHandler()
window.push_handlers(key_handler)

# Planet
# -----
subdivision_frequency = 60
vertices, indices = icosphere(subdivision_frequency)
indices = indices.flatten().tolist()
count = vertices.shape[0]
vertices = vertices.flatten().tolist()

planet = lib.shapes.Planet(x=0, y=0, z=0, vertices=vertices,
                           indices=indices, count=count,
                           noise=None, batch=planet_batch)

def on_update(delta: float):
    global camera

    movement_step = np.pi/2 * delta
    if key_handler[key.A]:
        camera_position = np.array([camera.x, camera.y, camera.z])
        new_position = camera_position @ rotate_y(movement_step)
        camera.x = new_position[0]
        camera.z = new_position[2]

        spaceship_position = np.array([spaceship_model.x, spaceship_model.y, spaceship_model.z])
        new_position = spaceship_position @ rotate_y(movement_step)
        spaceship_model.x = new_position[0]
        spaceship_model.z = new_position[2]
        
    if key_handler[key.D]:
        camera_position = np.array([camera.x, camera.y, camera.z])
        new_position = camera_position @ rotate_y(-movement_step)
        camera.x = new_position[0]
        camera.z = new_position[2]

        spaceship_position = np.array([spaceship_model.x, spaceship_model.y, spaceship_model.z])
        new_position = spaceship_position @ rotate_y(-movement_step)
        spaceship_model.x = new_position[0]
        spaceship_model.z = new_position[2]

def rotate_y(theta):
    return np.array([
        [ np.cos(theta), 0, np.sin(theta)],
        [ 0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)],
    ])


@window.event
def on_draw():
    window.clear()

    light_position = np.array([point_light.x, point_light.y, point_light.z])
    # The global state needs the camera and the light position
    global_state.update(camera.get_position(), light_position)

    widget_projection = window.projection
    widget_view = window.view

    window.projection = camera.get_projection()
    window.view = camera.get_look_at()
    

    spaceship_model.draw()
    planet_batch.draw()
    batch.draw()
    # world_batch.draw()

    window.projection = widget_projection
    window.view = widget_view
    widgets_batch.draw()

pyglet.clock.schedule_interval(on_update, 1/FPS)
pyglet.app.run()