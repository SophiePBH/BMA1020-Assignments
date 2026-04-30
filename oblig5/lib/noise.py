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

def grad3(hash, x, y, z):
    h = hash & 15
    u = x if h < 8 else y
    v = y if h < 4 else (x if h in (12, 14) else z)

    return ((u if(h & 1) == 0 else -u) +
            (v if(h & 2) == 0 else -v))

p = np.arange(256, dtype=int)
np.random.seed(0)
np.random.shuffle(p)
p = np.stack([p, p]).flatten()

def _perlin_noise3(x: float,
                   y: float,
                   z: float,
                   repeatx: int,
                   repeaty: int,
                   repeatz: int,
                   base: int):

    # Task 6a
    # Actual perlin noise

    # repeat x, y, og z = for 'seamless' transition (high number)
    # base = noise/seed -- can be 0

    xi = int(x) & 255
    yi = int(y) & 255
    zi = int(z) & 255

    xf = x - int(x)
    yf = y - int(y)
    zf = z - int(z)

    u = xf * xf * xf * (xf * (xf * 6 - 15) + 10)
    v = yf * yf * yf * (yf * (yf * 6 - 15) + 10)
    w = zf * zf * zf * (zf * (zf * 6 - 15) + 10)

    aaa = p[p[p[xi] + yi] + zi]
    aba = p[p[p[xi] + yi + 1] + zi]
    aab = p[p[p[xi] + yi] + zi + 1]
    abb = p[p[p[xi] + yi + 1] + zi + 1]
    baa = p[p[p[xi + 1] + yi] + zi]
    bba = p[p[p[xi + 1] + yi + 1] + zi]
    bab = p[p[p[xi + 1] + yi] + zi +1]
    bbb = p[p[p[xi + 1] + yi + 1] + zi + 1]

    x1 = lerp(grad3(aaa, xf, yf, zf),
              grad3(baa, xf - 1, yf, zf), u)
    x2 = lerp(grad3(aba, xf, yf - 1, zf),
              grad3(bba, xf -1, yf - 1, zf), u)
    y1 = lerp(x1, x2, v)

    x1 = lerp(grad3(aab, xf, yf, zf - 1),
              grad3(bab, xf - 1, yf, zf -1), u)
    x2 = lerp(grad3(abb, xf, yf - 1, zf - 1),
              grad3(bbb, xf - 1, yf - 1, zf - 1), u)
    y2 = lerp(x1, x2, v)

    return (lerp(y1, y2, w) + 1) / 2


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
    # Fractal brownian thingy
    total = 0
    frequency = 1
    amplitude = 1
    max_value = 0

    for _ in range(octaves):
        total += _perlin_noise3(
            x * frequency,
            y * frequency,
            z * frequency,
            repeatx,
            repeaty,
            repeatz,
            base
        ) * amplitude

        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    return total / max_value if max_value != 0 else 0

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