"""
This script implements the classic (1980) Perlin noise, developed by Ken Perlin.
It extends the noise into the fractal Brownian motion to include octaves,
lacunarity and persistence to create a more natural landscape.

The original implementation was introduced by Casey Duncan, and this script re-
implements it in pure Python. https://github.com/caseman/noise
"""

import numpy as np
import math
from .linalg import *

def _perlin_noise3(x: float,
                   y: float,
                   z: float,
                   repeatx: int,
                   repeaty: int,
                   repeatz: int,
                   base: int):

    # Task 6a
    # TODO complete the implementation here
    return 0.0


def perlin(x: float,
           y: float,
           z: float,
           octaves: int,
           persistence: float,
           lacunarity: float,
           repeatx: int,
           repeaty: int,
           repeatz: int,
           base: int) -> float:
    """
    An implementation of the fractal Brownian motion (fbm).

    We use this to create more varity and greater details to our landscapes.

    Parameters
    ----------
    octaves: An octave is an iteration of the perlin noise. The more octaves,
             the more layers of noise.

    persistence: The amplitude of an octave. It changes how rough or smooth
                 mountain peaks are. Higher persistence leads to smaller peaks
                 and sharper cliffs. Recommended values: [0, 1]

    lacunarity: Describes the frequency of higher octaves. Example values:
                - 1.5: Spread out peaks, smoother hills
                - 2.0: Realistic terrain
                - 3-4: jagged, highly detailed terrain. Many small ridges

    """

    # Task 6b
    # TODO complete the implementation here
    
    return 0.0

if "__main__" == __name__:
    # Plot the noise
    import matplotlib.pyplot as plt

    width = 200
    height = 200
    scale = 50.0

    noise_map = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            noise_map[y, x] = perlin(
                x / scale,
                y / scale,
                0.0,          # z slice
                octaves=4,
                persistence=0.5,
                lacunarity=2.0,
                repeatx=1024,
                repeaty=1024,
                repeatz=1024,
                base=0
            )

    plt.imshow(noise_map, cmap="gray", origin="lower")
    plt.colorbar()
    plt.title("Perlin Noise (2D slice)")
    plt.show()