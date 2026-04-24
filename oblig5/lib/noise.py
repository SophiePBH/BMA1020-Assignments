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
    # Actual perlin noise

    # repeat x, y, og z = for 'seamless' transition (high number)
    # base = noise/seed -- can be 0

    i = math.floor(x, repeatx) # check what fmodf is in temp.c
    j = math.floor(y, repeaty)
    k = math.floor(z, repeatz)
    ii = math.floor(i+1, repeatx)
    jj = math.floor(j+1, repeaty)
    kk = math.floor(k+1, repeatz)

    i = (i & 255) + base # check if '&' is correct in python
    j = (j & 255) + base
    k = (k & 255) + base
    ii = (ii & 255) + base
    jj = (jj & 255) + base
    kk = (kk & 255) + base

    x -= math.floor(x) # check floorf
    y -= math.floor(y)
    z -= math.floor(z)
    fx = x**3 * (x*(x*6-15) + 10)
    fy = y**3 * (y*(y*6-15) + 10)
    fz = z**3 * (z*(z*6-15) + 10)

    """ Need Permutation table for rest (I think), also need to find out what 'grad3' is """
    # A = PERM[i]
	# AA = PERM[A + j]
	# AB = PERM[A + jj]
	# B = PERM[ii]
	# BA = PERM[B + j]
	# BB = PERM[B + jj]

    # return lerp(fz, lerp(fy, lerp(fx, grad3(PERM[AA + k], x, y, z),
	# 								  grad3(PERM[BA + k], x - 1, y, z)),
	# 						 lerp(fx, grad3(PERM[AB + k], x, y - 1, z),
	# 								  grad3(PERM[BB + k], x - 1, y - 1, z))),
	# 				lerp(fy, lerp(fx, grad3(PERM[AA + kk], x, y, z - 1),
	# 								  grad3(PERM[BA + kk], x - 1, y, z - 1)),
	# 						 lerp(fx, grad3(PERM[AB + kk], x, y - 1, z - 1),
	# 								  grad3(PERM[BB + kk], x - 1, y - 1, z - 1))))

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
    # Fractal brownian thingy
    if(octaves == 1):
        return _perlin_noise3(x, y, z, repeatx, repeaty, repeatz, base)
    elif(octaves > 1):
        frequency, amplitude = 1
        max, total, i = 0

        for i in octaves:
            total += _perlin_noise3(x*frequency, y*frequency, z*frequency,
                                    repeatx*frequency, repeaty*frequency,
                                    repeatz*frequency, base) * amplitude
            max += amplitude
            frequency *= lacunarity
            amplitude *= persistence
            i += 1

        return total/max

    else:
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