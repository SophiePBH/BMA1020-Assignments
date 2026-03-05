# Assignment 3

This assignment is a continuation of *assignment 3*, and we will take the simulations a step further into 3-dimensional space. Whilst the task descriptions are similar to the previous assignment, there are some changes. Please read them carefully to not miss important details.

- [Part 1: Particle Systems](#part-1-particle-systems)
- Part 2: TBA
- [Additional Library](#additional-library)

## Deadline
| Action | Time |
|---|---|
|Opened| 27.02.2026|
|Deadline|17.03.2026|

## Part 1: Particle Systems
In this task, we will create a particle system in 3D space. In it, a particle is a point in Cartesian space with a set of properties. We will use Pyglet to visualise them, i.e. providing a shape to each particle.

### Specifications
  - Window size: 1280x720.
    - If you use MacOS and have a Retina screen, setting this may lead to unexpected results. In this case, do not set the window size. The operating system will do this for you.
  - Particles spawn with a random size. You are free to choose a reasonable size.
  - All particles spawn from the same Cartesian coordinate (it's okay to move the spawning point with keyboard or mouse inputs during runtime).
  - Particles spawn with colors of your choice. Once an invididual particle's color is set, it must persist throughout its lifetime.
  - Particles spawn with a random velocity.
  - Particles are affected by gravitational force.
  - Particles spawn at a fixed rate.
  - There is a boundary box that particles can only live in. Once a particle steps outside the boundary, it dies.

Additional requirements:
  - To create an interactive simulation, we will introduce the camera to our the simulation.
  - Enable the camera to orbit around the simulation, so it can be viewed from different angles.

We have provided an additional library for the camera and the shapes that extend Pyglet. More about this in [Additional Library](#additional-library).

### Part 2: Geometric Optics
TBA

## Additional Library
[`lib`](./lib/) is our own internal library which extends Pyglet's capabilities. Even though Pyglet uses modern graphics technologies, it is implemented as a 2D library. `lib` extends Pyglet to support 3D. Whilst we have done most of the work, as part of the assignment you will contribute to a portion of the library [see here](#additional-library---tasks).


### Additional Library - Tasks
To complete the library, you will do the following:

Task 1: Implement function `translate(...)` function in [lib/transformations.py](./lib/transformations.py).

Task 2: Implement function `scale(...)` in [lib/transformations.py](./lib/transformations.py).

Task 3: Implement rotation function(s). We have already provided `rotate_z(...)`, `rotate_y(...)` and `rotate_x(...)`, but you can a different function, e.g. using quaternions or rotating around an arbitrary axis.

Task 4: In [lib/Camera.py](./lib/Camera.py), complete method `get_projection()`. This returns the camera's projection matrix.

Task 5: In [lib/Camera.py](./lib/Camera.py), complete method `get_look_at()`. This returns a matrix that describes the camera's orientation, position and the up vector.

### Optional Tasks
World grids can be useful while working with 3D graphics to help navigating the world. It is optional to use the world grid and the template that the [world grid demo](./world_grid_demo.py) provides.

To make the demo work, you need to complete the following tasks:
- *Task 4*: [See above](#additional-library---tasks)
- *Task 5*: [See above](#additional-library---tasks)
- *Task 6*: In [lib/transformations.py](./lib/transformations.py), complete the `perspective(...)` method
- *Task 7*: In [lib/transformations.py](./lib/transformations.py), complete the `look_at(...)` method

### Features
The library is unique to our course and there exists no documentation online about it. Therefore, we will include some documentation about how to use some of its features.

#### Feature 1: Shader
A shader is a program executed by the GPU. Unfortunately, Pyglet provides a shader that supports 2D only. We have therefore extended it and provide a 3D compatible shader. You should not do anything with it besides instantiating the shader and updating it, as shown in the example code below:

```py
import lib

# Create a new shader instance
shader = lib.create3DShader()

# Before drawing 3D shapes, remember to update the shader. You can find the
# projection and view matrices under the Camera section.
def on_draw():
    shader["u_projection"] = projection_matrix
    shader["u_view"] = view_matrix
```

Note: We need only to do this with our own custom shapes. If you work with Pyglet's 2D shapes, this is not necessary.

See [world_grid_demo.py](./world_grid_demo.py) for a full demonstration.

#### Feature 2: Camera
In the real life, we see the world through our eyes. To capture what we see, we can use cameras. Similarly, we can see virtual 2D and 3D worlds through the camera. For instance, while you are watching films, you watch the scenes captured by a camera.

In computer graphics, the camera does not exist because merely represent content as pixels on a 2D screen. To solve this problem, we introduce the `Camera` class. It consists of two important components:

- The *projection matrix*
- The *view matrix*

These are the two matrices that we pass to the shader, as mentioned in [Feature 1: Shader](#feature-1-shader).

Example code:
```py
camera = lib.Camera(width=1280, height=720,
                    fov=60,  # Measured in degrees
                    near=0.01, far=100.0)

# You can get the camera's projection and view matrix as follow:
projection = camera.get_projection()
view = camera.get_look_at()
```

The camera is programmed to orbit around the origin. You can do this by setting the following values:
```py
# Describes the camera's distance from origin.
camera.distance = 10

# Describes the camera's spherical coordinates (polar and azimuthal angles)
# in radians.
camera.phi = np.pi/6
camera.theta = np.pi / 4
```

Arguments:
| Name | Type | Description |
|---|---|---|
| `width` | `int` | Used to calculate the aspect ratio. For our purpose, it should always be the window width. |
| `height` | `int` | Used to calculate the aspect ratio. For our purpose, it should always be the window height. |
| `fov` | `float` | Field of view. Describes how much of the scene in front of the camera is visible. The value is in degrees. |
| `near` | `float` | Near clip plane. Used to compute the viewing frustum. Anything between the near clip plane and the camera is *not* visible. Too small value or `0.0` cause undefined behaviours. |
| `far` | `float` | Far clip plane. Used to compute the viewing frustum and represents the farthest distance from a camera that a visible object can be. Useful to obscure non-important objects in the distance. |

See [world_grid_demo.py](./world_grid_demo.py) for a full demonstration.


#### Feature 3: Prism3D Shape
`Prism3D` represents a 4-sided prism and extends Pyglet's [`Rectangle`](https://pyglet.readthedocs.io/en/latest/modules/shapes.html#pyglet.shapes.Rectangle) class to represent a cuboid. You can use it to represent a particle in a particle system.

Example code:
```python
import lib
import pyglet

# We need to provide our own 3D compatible shader.
shader = lib.create3DShader()

# Optional: You can add the prism to a batch
batch = pyglet.graphics.Batch()

prism = lib.shapes.Prism3D(
    # Position
    x=0.0, y=0.0, z=0.0,

    # Dimension
    width=10.0, height=12.0, depth=8.0,

    color=(190, 30, 160, 255),
    batch=batch,

    # Mandatory: pass the shader to the prism
    program=shader
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
| program | `pyglet.graphics.Shader` | [Mandatory] Pass a reference to our custom shader. |

See [world_grid_demo.py](./world_grid_demo.py) for a full demonstration.


#### Feature 4: WorldGrid Shape
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

See [world_grid_demo.py](./world_grid_demo.py) for a full demonstration.


## Demo - Particle systems (Part 1)
<video width="320" height="240" controls>
  <source src="./videos/particles.mp4" type="video/mp4">
</video>

## Submission
TBA
