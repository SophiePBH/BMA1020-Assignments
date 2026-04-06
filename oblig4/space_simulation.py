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
within a range which gives visually satisfying results! ☑️

Particles die after a certain amount of time, e.g. 3 seconds. ☑️

Particles collide with each other with sphere-to-sphere collision.

Allow the user to adjust the coefficient of restitution e, taking e=0.8 as a default. ☑️

Particles are subject to mutual gravitational and electromagnetic forces.
You should be able to toggle each force on/off with a keystroke. ☑️
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
WIDTH = 1280
HEIGHT = 720
window.width = WIDTH
window.height = HEIGHT

glEnable(GL_DEPTH_TEST)

FPS = 60


# Gravity
has_em_force = True
has_gravity = False
electric_field = np.array([-1, -1, 0])
magnetic_field = np.array([0, 1, 1])
gravitational_constant = -250
# Coefficient of restitution (COR)
e = 0.8

# Objects
# -------
# Batches
batch = pyglet.graphics.Batch()
spheres_batch = pyglet.graphics.Batch()
particles_batch = pyglet.graphics.Batch()
widgets_batch = pyglet.graphics.Batch()

# Particles
particles = np.array([])
charge = np.array([-1, 1])
spawnpoint = np.array([0, 0, 0])

# Spaceship
spaceship_model = lib.shapes.CustomModel(filepath="data/spaceship.obj",
                                         x=0.0, y=0.0, z=0.0,
                                         size=1)

# The world grid helps us navigating the 3d world space
world_grid = lib.shapes.WorldGrid(batch)

# Widgets
# -------
font_size = 18
font_type = 'Arial'

# You can add labels to batches.
e_label = pyglet.text.Label("e = 0.8", font_name=font_type, font_size=font_size,
                          x=30.0, y=HEIGHT-50, anchor_x='left', anchor_y='center', 
                          batch=widgets_batch)

e_slider = lib.widgets.Slider(x=30, y=HEIGHT-100, width=200, height=10,
                          knob_width=15, knob_height=15,
                          color=(255,255,255,125), knob_color=(255,255,255,255),
                          batch=widgets_batch, starting_value=e)


spawnX_label = pyglet.text.Label("Spawnpoint X: 0", font_name=font_type, font_size=font_size,
                                 x=30.0, y=HEIGHT-150, anchor_x='left', anchor_y='center', 
                                 batch=widgets_batch)

spawnX_slider = lib.widgets.Slider(x=30, y=HEIGHT-200, width=200, height=10,
                                  knob_width=15, knob_height=15,
                                  color=(255,0,0,125), knob_color=(255,0,0,255),
                                  batch=widgets_batch, starting_value=0.5)

spawnY_label = pyglet.text.Label("Spawnpoint Y: 0", font_name=font_type, font_size=font_size,
                                 x=30, y=HEIGHT-250, anchor_x='left', anchor_y='center', 
                                 batch=widgets_batch)

spawnY_slider = lib.widgets.Slider(x=30, y=HEIGHT-300, width=200, height=10,
                                  knob_width=15, knob_height=15,
                                  color=(0,255,0,125), knob_color=(0,255,0,255),
                                  batch=widgets_batch, starting_value=0.5)

spawnZ_label = pyglet.text.Label("Spawnpoint Z: 0", font_name=font_type, font_size=font_size,
                                 x=30, y=HEIGHT-350, anchor_x='left', anchor_y='center', 
                                 batch=widgets_batch)

spawnZ_slider = lib.widgets.Slider(x=30, y=HEIGHT-400, width=200, height=10,
                                  knob_width=15, knob_height=15,
                                  color=(0,0,255,125), knob_color=(0,0,255,255),
                                  batch=widgets_batch, starting_value=0.5)

controls_label = pyglet.text.Label("Mutual gravitational force:\nElectromagnetic force:",
                                    font_name=font_type, font_size=font_size,
                                    x=WIDTH-60, y=HEIGHT-50, anchor_x='right',
                                    anchor_y='center', multiline=True, width=325,
                                    batch=widgets_batch)
gravity_label = pyglet.text.Label("Off", font_name=font_type, font_size=font_size,
                                    x=WIDTH-30, y=HEIGHT-37, anchor_x='right',
                                    anchor_y='center', color=(255,0,0,255),
                                    batch=widgets_batch)
em_label = pyglet.text.Label("On", font_name=font_type, font_size=font_size,
                                    x=WIDTH-30, y=HEIGHT-65, anchor_x='right',
                                    anchor_y='center', color=(0,255,0,255),
                                    batch=widgets_batch)

# Camera
# ------
# We introduce the camera as a concept. It is our eyes into the 3d world.
camera = lib.Camera(width=WIDTH, height=HEIGHT,
                    fov=60,  # Measured in degrees
                    near=0.01, far=100.0)

# Camera position
camera.x = -8
camera.y = 2
camera.z = 8

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
        self.y = spawnpoint[1]
        self.z = spawnpoint[2]

        # Mass and charge
        self.mass = random.uniform(0.1, 1)
        self.charge = charge[random.randint(0, 1)]

        # Angle
        self.theta = random.uniform(-np.pi, np.pi)
        self.phi = random.uniform(-np.pi, np.pi)

        # Speed and velocity
        self.speed = random.randint(1, 5)
        self.velocity = np.array([self.speed * np.sin(self.phi) * np.cos(self.theta),
                                  self.speed * np.sin(self.phi) * np.sin(self.theta),
                                  self.speed * np.cos(self.phi)])

        # Size of sphere
        self.radius = random.uniform(0.1, 0.3)

        # Colour
        self.R = np.array([193, 154, 116, 77, 0])
        self.G = np.array([193, 154, 116, 77, 0])
        self.B = 255

        # The particles shape
        self.shape = lib.Sphere(x=self.x, y=self.y, z=self.z,
                                radius=self.radius,
                                color=(self.R[random.randint(0, 4)],
                                    self.G[random.randint(0, 4)],
                                    self.B, 255),
                                batch=batch)
        
    def move(self, dt):
        # Calculate and add gravitational effectS
        if(has_em_force):
            self.velocity += dt * electromagnetic_force(self.charge, self.velocity)
        if(has_gravity and len(particles) > 1):
            # TODO: Think i need to implement collision to stop error?
            self.velocity += dt * gravity(self, particles)
        
        # Calculate new position of particle
        new_position = dt * lib.transformations.translate(self.velocity[0],
                                                          self.velocity[1],
                                                          self.velocity[2])
        
        # Change the particle's position
        self.shape.x += new_position[0][3]
        self.shape.y += new_position[1][3]
        self.shape.z += new_position[2][3]


def electromagnetic_force(q, v):
    # F = q * (E + v x B)
    # q = charge, E = electric field, v = velocity, B = magnetic field
    force = q * (electric_field + np.cross(v, magnetic_field))
    
    return force

def gravity(self, particles):
    # F = (G * m_1 * m_2 * (x_1 - x_2)) / (|(x_1 - x_2)|**3)
    # G = gravitational constant, m_1 = mass 1, m_2 = mass 2,
    # x_1 = centre of sphere 1, x_2 = centre of sphere 2
    for particle in particles:
        if self is not particle:
            x_1 = np.array([self.shape.x, self.shape.y, self.shape.z])
            x_2 = np.array([particle.shape.x, particle.shape.y, particle.shape.z])
            
            force = (gravitational_constant * self.mass * particle.mass * (x_1 - x_2)) / (np.linalg.norm(x_1 - x_2)**3)
            return force

def collision_detection(self, particles, dt):
    for particle in particles:
        if self is not particle:
            x_1 = np.array([self.shape.x, self.shape.y, self.shape.z])
            x_2 = np.array([particle.shape.x, particle.shape.y, particle.shape.z])

            distance = np.linalg.norm(x_1 - x_2)
            if(distance <= self.radius + particle.radius):
                I = (self.mass * particle.mass) / (self.mass + particle.mass) * (1 + e) * (particle.velocity - self.velocity)
                self.velocity += dt * I/self.mass
                particle.velocity += dt * I/particle.mass
                return True
            else:
                return False

# Creating particles
def particle_emitter(amount):
    global particles
    particles = np.append(particles, [Particle(particles_batch, spawnpoint) for _ in range(amount)])

def create_particles(dt):
    particle_emitter(random.randint(15, 20))

def start():
    particle_emitter(15)

@window.event
def on_key_press(symbol, modifiers):
    global has_em_force
    global has_gravity

    # Enable/Disable electromagnetic force and gravity
    if symbol == key.O:
        has_em_force = not has_em_force
        if(has_em_force):
            em_label.color = (0,255,0,255)
            em_label.text = "On"
        else:
            em_label.color = (255,0,0,255)
            em_label.text = "Off"
    elif symbol == key.P:
        has_gravity = not has_gravity
        if(has_gravity):
            gravity_label.color = (0,255,0,255)
            gravity_label.text = "On"
        else:
            gravity_label.color = (255,0,0,255)
            gravity_label.text = "Off"

    # Quit program
    elif symbol == key.ESCAPE:
        window.close()

def on_update(delta: float):
    global camera
    global particles

    # Move or kill particle
    for particle in particles:
        if(particle.lifetime <= 0):
            particles = np.delete(particles, np.where(particles == particle))
        else:
            collision_detection(particle, particles, delta)
            particle.move(delta)
            particle.lifetime -= 1

    # TODO: Proper camera movement. Janky rn
    movement_step = np.pi/2 * delta *3

    # I think the key_handler is being overridden by on_key_press() 🤔
    if key_handler[key.W]:
        camera.y += movement_step
    if key_handler[key.S]:
        camera.y -= movement_step
    if key_handler[key.D]:
        camera.x += movement_step
    if key_handler[key.A]:
        camera.x -= movement_step
    if key_handler[key.E]:
        camera.z += movement_step
    if key_handler[key.Q]:
        camera.z -= movement_step

@window.event
def on_mouse_drag(x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
    if buttons & pyglet.window.mouse.LEFT:
        global e

        e_slider.update_clicked(x, y)
        e_label.text = "e = " + str(e_slider.value)
        e = e_slider.value

        spawnX_slider.update_clicked(x, y)
        spawnX_label.text = "Spawnpoint X: "+ str(np.round(spawnX_slider.value * 10 - 5, decimals=2))
        spawnpoint[0] = spawnX_slider.value * 10 - 5

        spawnY_slider.update_clicked(x, y)
        spawnY_label.text = "Spawnpoint Y: " + str(np.round(spawnY_slider.value * 10 - 5, decimals=2))
        spawnpoint[1] = spawnY_slider.value * 10 - 5

        spawnZ_slider.update_clicked(x, y)
        spawnZ_label.text = "Spawnpoint Z: " + str(np.round(spawnZ_slider.value * 10 - 5, decimals=2))
        spawnpoint[2] = spawnZ_slider.value * 10 - 5

@window.event
def on_draw():
    window.clear()
    widget_projection = window.projection
    widget_view = window.view

    window.projection = camera.get_projection()
    window.view = camera.get_look_at()
    
    # spaceship_model.draw()

    particles_batch.draw()
    batch.draw()

    window.projection = widget_projection
    window.view = widget_view
    widgets_batch.draw()

start()
pyglet.clock.schedule_interval(on_update, 1/FPS)
pyglet.clock.schedule_interval(create_particles, 3)
pyglet.app.run()