# Assignment 4

In the fourth assignment, we will achieve the following (in 3D):

*Part A*:
- Create a particle system with collisions.

*Part B*:
- To be announced

<!-- Create a spaceship.
- Introduce lighting to lit the spaceship's interior. -->



## Deadline
Please visit [Moodle](https://capquiz.math.ntnu.no/) to see the deadline.

## Table of Content
- [Task 1: Initialising the program](#1-initialising-the-program)
- [Task 2: Re-introducing the particle system](#2-re-introducing-the-particle-system)
- [Additional Library](#additional-library)

## 1. Initialising the Program
a) In [space_simulation.py](./space_simulation.py), create a default Pyglet application. The window size should be 1280x720
- If you use MacOS and have a Retina screen, setting this may lead to unexpected results. In this case, do not set the window size. The operating system will do this for you.


b) Enable occlusion culling with `glEnable(GL_DEPTH_TEST)`. This ensures that objects blocked by other objects closer to the camera do not render.

```py
from pyglet.gl import glEnable, GL_DEPTH_TEST

# On initialising the program
glEnable(GL_DEPTH_TEST)
```

## 2. Re-introducing the Particle System
In assignment 3, we introduced and created a particle system in 3D. We will do it a little differently this time, according to the following specifications:

- Particles are now spheres. A class [`Sphere`](#feature-7-sphere) has been added to the library provided.
- Particles spawn from at least one point in Cartesian space. That means you can choose to create and emit the particles from multiple, defined Cartesian coordinates.
- Particles spawn with colors of your choice. Once an individual particle's color is set, it must persist throughout its lifetime.
- Particles spawn with a random velocity, radius, mass and charge. The charge can be taken to be either $1$ or $-1$ at random, the others should take positive values within a range which gives visually satisfying results!
- Particles die after a certain amount of time, e.g. $3$ second.
- Particles collide with each other with sphere-to-sphere collision. Allow the user to adjust the coefficient of restitution $e$, taking $e=0.8$ as a default.
- Particles are subject to mutual gravitational and electromagnetic forces. You should be able to toggle each force on/off with a keystroke.

### Electromagnetic forces

Particles of charge $q$ moving at velocity $\vec{v}$ should experience a Lorentz force

$$\vec{F} = q(\vec{E} + \vec{v}\times\vec{B})$$

The electric field $\vec{E}$ and magnetic field $\vec{B}$ can vary with time and position, but for simplicity, try taking them to be of constant strength, and pointing in a fixed direction. They should not point in the same direction. You can try varying them later, but this is not necessary.

### Gravity

Particles of mass $m_1, m_2$ exert a mutual gravitational force

$$\vec{F} = \frac{G m_1 m_2 (\vec{x}_1 - \vec{x}_2)}{| (\vec{x}_1 - \vec{x}_2)|^3}$$

Choose a gravitational constant $G$ that is much higher than the real one, so the forces are not negligible. Alternatively work with masses of astronomical size!

## Additional Library
Equally to the last assignment, we introduce the additional library [`lib`](./lib/). New additions for this iteration include:
- [`Sphere`](#feature-7-sphere)
- [`CustomModel`](#feature-8-custom-model)

Changes:
- A shader must no longer be provided to create 3D shapes. This is now handled internally. Please see [Feature 1: Camera](#feature-1-camera) for more details.
- Some class parameters that were obsolete are removed. These include:
    - `group`
    - `program`
    - `blend_src`
    - `blend_dest`
- Camera position is now defined by Cartesian coordinates $[x, y, z]$. Previously it was defined by $[r, \theta, \phi]$. This should help positioning the camera correctly in *Part B*. You can reverse this change if you choose so.

Other:
- To include widgets, `lerp()` must be implemented in [lib/linalg.py](./lib/linalg.py).

### Features
The library is unique to our course and there exists no documentation online about it. Therefore, we will include some documentation about how to use some of its features.

#### Feature 1: Camera
In the real life, we see the world through our eyes. To capture what we see, we can use cameras. Similarly, we can see virtual 2D and 3D worlds through the camera. For instance, while you are watching films, you watch the scenes captured by a camera.

In computer graphics, the camera does not exist because merely represent content as pixels on a 2D screen. To solve this problem, we introduce the `Camera` class. It consists of two important components:

- The *projection matrix*
- The *view matrix*

Example code:
```py
camera = lib.Camera(width=1280, height=720,
                    fov=60,  # Measured in degrees
                    near=0.01, far=100.0)

# You can get the camera's projection and view matrix as follow:
projection = camera.get_projection()
view = camera.get_look_at()
```

Camera position is defined with Cartesian coordinates. You can do this by setting the following values:
```py
camera.x = 0
camera.y = 0
camera.z = 0
```

*New*: Due to a recent change, the projection and view matrices are uploaded as follow:

```py
@window.event
def on_draw():
    window.projection = camera.get_projection()
    window.view = camera.get_look_at()
```

If you are using an application class that inherits from `pyglet.window.Window`, the following will instead apply:
```py
def on_draw(self):
    self.projection = camera.get_projection()
    self.view = camera.get_look_at()
```

Arguments:
| Name | Type | Description |
|---|---|---|
| `width` | `int` | Used to calculate the aspect ratio. For our purpose, it should always be the window width. |
| `height` | `int` | Used to calculate the aspect ratio. For our purpose, it should always be the window height. |
| `fov` | `float` | Field of view. Describes how much of the scene in front of the camera is visible. The value is in degrees. |
| `near` | `float` | Near clip plane. Used to compute the viewing frustum. Anything between the near clip plane and the camera is *not* visible. Too small value or `0.0` cause undefined behaviours. |
| `far` | `float` | Far clip plane. Used to compute the viewing frustum and represents the farthest distance from a camera that a visible object can be. Useful to obscure non-important objects in the distance. |


#### Feature 2: Prism3D Shape
`Prism3D` represents a 4-sided prism and extends Pyglet's [`Rectangle`](https://pyglet.readthedocs.io/en/latest/modules/shapes.html#pyglet.shapes.Rectangle) class to represent a cuboid. You can use it to represent a particle in a particle system.

Example code:
```python
import lib
import pyglet

# Optional: You can add the prism to a batch
batch = pyglet.graphics.Batch()

prism = lib.shapes.Prism3D(
    # Position
    x=0.0, y=0.0, z=0.0,

    # Dimension
    width=10.0, height=12.0, depth=8.0,

    color=(190, 30, 160, 255),
    batch=batch
)
```

Arguments:
| Name | Type | Description |
|---|---|---|
| x | `float` | x-position in 3D space. |
| y | `float` | y-position in 3D space. |
| z | `float` | z-position in 3D space. |
| width | `float` | Specifies the prism's size along the x-axis. |
| height | `float` | Specifies the prism's size along the y-axis. |
| depth | `float` | Specifies the prism's size along the z-axis. |
| color | `tuple` | Specifies the prism's color. |
| batch | `pyglet.graphics.Batch` | [Optional] Include the shape in a batch. It will then be draw together with any other shapes in the batch. |


#### Feature 3: Line3D Shape
``` Python
import lib
import pyglet

batch = pyglet.graphics.Batch()

line = lib.shapes.Line3D(
    x0=0, y0=0, z0=0,
    x1=3, y1=2, z1=1,
    thickness=0.1,
    color=(80, 180, 230, 255),
    batch=batch)

line1 = lib.shapes.Line3D(
    x0=2, y0=3, z0=0,
    x1=3, y1=-4, z1=1,
    thickness=0.2,
    color=(255, 180, 230, 255),
    batch=batch)

```

Arguments:
| Name | Type | Description |
|---|---|---|
| x0 | `float` | x0-position in 3D space. |
| y0 | `float` | y0-position in 3D space. |
| z0 | `float` | z0-position in 3D space. |
| x1 | `float` | x1-position in 3D space. |
| y1 | `float` | y1-position in 3D space. |
| z1 | `float` | z1-position in 3D space. |
| thickness | `float` | Specifies the line's thickness |
| color | `tuple` | Specifies the line's color. |
| batch | `pyglet.graphics.Batch` | [Optional] Include the shape in a batch. It will then be draw together with any other shapes in the batch. |


#### Feature 4: Circle3D Shape
```Python
import lib
import pyglet

shader = lib.create3DShader()

batch = pyglet.graphics.Batch()

circle = lib.shapes.Circle3D(
    x=0,
    y=5,
    z=0,
    radius=20,
    color=(255, 0, 0),
    batch=batch)

```
Arguments:
| Name | Type | Description |
|---|---|---|
| x | `float` | x-position in 3D space. |
| y | `float` | y-position in 3D space. |
| z | `float` | z-position in 3D space. |
| radius | `float` | Specifies the circle's radius |
| color | `tuple` | Specifies the circles's color. |
| batch | `pyglet.graphics.Batch` | [Optional] Include the shape in a batch. It will then be draw together with any other shapes in the batch. |


#### Feature 5: WorldGrid Shape
The `WorldGrid` shape inherits from a custom `Rectangle3D` shape. It creates an infinite world grid that helps navigating the 3D world. Internally, it creates its own special shader, so including the WorldGrid is simple.

Example code:
```py
import lib
import pyglet

# It is recommended to add the world grid to a batch
batch = pyglet.graphics.Batch()

# Create the world grid
world_grid = lib.shapes.WorldGrid(batch)

def on_draw():
    # Remember to update the world grid's internal shader.
    world_grid.shader["u_projection"] = projection matrix
    world_grid.shader["u_view"] = view matrix

    # To draw the world grid, simply draw the the batch. Otherwise, you can draw the
    # world grid directly.
    #
    # world_grid.draw()
    # OR
    # batch.draw()
```

#### Feature 6: Widgets
Pyglet does not provide widgets out-of-the-box. Although it supports labels, we must manually create our own widgets using primitive shapes like rectangles. Whilst widgets are not mandatory for the course, they can be useful to quickly testing or changing parameters, observing changes in real-time and debugging.

You can create a label using Pyglet's built-in features:
```python
import pyglet

font_size = 18
font_type = 'Times New Roman'

# You can add labels to batches.
label = pyglet.text.Label("My label",
                          font_name=font_type,
                          font_size=font_size,
                          x=30.0,
                          y=600,
                          anchor_x='left', anchor_y='center')
```

We have created a slider, provided in *lib*.
```py
# The slider also supports batches.
slider = lib.widgets.Slider(
    x=150,
    y=660.0,
    width=300.0,
    height=20.0,
    knob_width=60,
    knob_height=40,
    color=(249, 166, 253, 255),
    knob_color=(90, 90, 90, 255),
    starting_value=0.0
)
```

When drawing widgets, we use the original projection and view matrices to prevent the billboard effect. Declare the following after initialising the window:
```py
widget_projection = window.projection
widget_view = window.view
```

| Name | Type | Description |
|--|--|--|
|x|`float`|x-position on the screen|
|y|`float`|y-position on the screen|
|width|`float`|Length of the track|
|height|`float`|Height of the track|
|knob_width|`float`|Length of the knob|
|knob_height|`float`|Height of the knob|
|color|`tuple`|Color of the track|
|knob_color|`tuple`|Color of the knob|
|starting_value|`float`|The slider's value range between $0.0$ and $1.0$. The starting value dictates the initial value.|

> NB! To use the slider, you must implement the linear interpolation function of `lerp()` in [lib/linalg.py](./lib/linalg.py).

To change the value of the slide with the mouse, you must update it using an event, e.g. a mouse drag event.

```py
@window.event
def on_mouse_drag(x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
    if buttons & pyglet.window.mouse.LEFT:
        slider.update_clicked(x, y)
        print(slider.value)
```

With the widgets, you can create a useful and powerful user interface. For example, to display the slider's value, you can display it with a label.

```py
label = pyglet.text.Label("Slider value: 0.0",
                          font_name=font_type,
                          font_size=font_size,
                          x=30.0,
                          y=600,
                          anchor_x='left', anchor_y='center')

slider = lib.widgets.Slider(x=150,
                            y=660.0,
                            width=300.0,
                            height=20.0,
                            knob_width=60,
                            knob_height=40,
                            color=(249, 166, 253, 255),
                            knob_color=(90, 90, 90, 255),
                            starting_value=0.0)

@window.event
def on_mouse_drag(x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
    if buttons & pyglet.window.mouse.LEFT:
        slider.update_clicked(x, y)
        label.text = str(slider.value)

@window.event
def on_draw():
    window.projection = widget_projection
    window.view = widget.view
```

You can also move objects in 3d space with the slider, change the particle spawn rate, and more.

#### Feature 7: Sphere
The `Sphere` is implemented as a [geodesic polyhedron](https://en.wikipedia.org/wiki/Geodesic_polyhedron), also known as an icosphere.

Example code:
```python
import lib
import pyglet

# Optional: You can add the prism to a batch
batch = pyglet.graphics.Batch()

prism = lib.shapes.Prism3D(
    # Position
    x=0.0, y=0.0, z=0.0,

    # Size
    radius=30

    color=(190, 30, 160, 255),
    batch=batch
)
```

Arguments:
| Name | Type | Description |
|---|---|---|
| x | `float` | x-position in 3D space. |
| y | `float` | y-position in 3D space. |
| z | `float` | z-position in 3D space. |
| radius | `float` | Specifies the sphere's radius. |
| color | `tuple` | Specifies the sphere's color. |
| batch | `pyglet.graphics.Batch` | [Optional] Include the shape in a batch. It will then be draw together with any other shapes in the batch. |

#### Feature 8: Custom Model
The `CustomModel` enables importing and rendering 3D models. A spaceship model is provided in [data/spaceship.obj](./data/spaceship.obj).

Example code:
```python
import lib
import pyglet

# Optional: You can add the prism to a batch
batch = pyglet.graphics.Batch()

spaceship_model = lib.shapes.CustomModel(filepath="data/spaceship.obj",
                                         x=0.0, y=0.0, z=0.0,
                                         size=1,
                                         batch=batch)
```

Arguments:
| Name | Type | Description |
|---|---|---|
| x | `float` | x-position in 3D space. |
| y | `float` | y-position in 3D space. |
| z | `float` | z-position in 3D space. |
| size | `float` | Specify the size of the model. The model's vertex positions are scaled accordingly. |
| color | `tuple` | Specifies the sphere's color. |
| batch | `pyglet.graphics.Batch` | [Optional] Include the shape in a batch. It will then be draw together with any other shapes in the batch. |
