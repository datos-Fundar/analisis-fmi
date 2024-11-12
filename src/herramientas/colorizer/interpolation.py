import numpy as np
from .common import pairwise, flatten, identity
from .color import Color
from .palette import Palette

def linear_interpolation(point1, point2, t):
    """
    Perform linear interpolation between two points in N dimensions.
    
    Parameters:
    point1 (array-like): The first point in N dimensions.
    point2 (array-like): The second point in N dimensions.
    t (float): The interpolation factor between 0 and 1.
    
    Returns:
    numpy.ndarray: The interpolated point in N dimensions.
    """
    if not (0 <= t <= 1):
        raise ValueError("The interpolation index t must be between 0 and 1.")
    
    point1 = np.array(point1)
    point2 = np.array(point2)
    
    if point1.shape != point2.shape:
        raise ValueError("Both points must have the same dimensions.")
    
    interpolated_point = (1 - t) * point1 + t * point2
    return np.array(interpolated_point, dtype=int)

def interpolate_n(a,b, n, f):
    yield from (linear_interpolation(a,b,f(t)) for t in np.linspace(0,1, n))

def lerps(cs, n, f):
    yield from (interpolate_n(a,b,n,f) for a,b in pairwise(cs))

def interpolations_n(xss, n, f):
    yield from flatten(lerps(xss, n, f), 1)

def colors_from_interpolations(cs, n, f):
    yield from map(Color.from_rgb, interpolations_n(cs, n, f))

def palette_from_interpolations(cs, n, f=identity):
    return Palette(colors_from_interpolations(cs, n, f))

def smoothstep_generator(p: float, s: float):
    """
    Familia de funciones de interpolación suave.
    Devuelve una función de interpolación entre 0 y 1.

    Casos especiales:
    - s = 0: función lineal
    - s = 1: función step centrada en p
    - s = 1, p = 0: constante 1
    - s = 1, p = 1: constante 0

    Parámetros:
    p: Punto de inflexion
    s: Steepness
    """
    if not (0 <= p <= 1) or not (0 <= s <= 1):
        raise ValueError("p and s must be in the range [0,1]")

    if s == 0: # id
        return lambda x: x

    if s == 1: # step
        slope = lambda x: float('inf')
        match float(p):
            case 1.0: return lambda x: 0
            case 0.0: return lambda x: 1
            case _: return lambda x: 1 if x > p else 0

    c = (2 / (1-s)) - 1

    f = lambda x,n: (x**c) / (n**(c-1))
    g = lambda x,n: (c*x**(c-1)) / (n**(c-1))

    f1 = lambda x: f(x, p)
    f2 = lambda x: 1 - f(1-x, 1-p)
    # slope = lambda x: (g(p,p) * (x-p)) + p

    match float(p):
        case 0.0: return f1
        case 1.0: return f2
        case _: return lambda x: (f1 if x <= p else f2)(x)