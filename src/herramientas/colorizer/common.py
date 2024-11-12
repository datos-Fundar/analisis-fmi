import numpy as np
from io import BytesIO
from base64 import b64encode
import matplotlib.colors as mcolors
from PIL import Image
import pickle
from collections.abc import Iterable

def dict_as_colormap(color_dict, name=None):
    """
    Convierte un diccionario de colores en un colormap de matplotlib.
    Está hecho para ser usado por Color.to_cmap.
    """
    if not name:
        name = '-'.join(x for x in color_dict.values())
    
    keys = sorted(color_dict.keys())
    keys_nums = [i for i,_ in enumerate(keys)]


    colors = [color_dict[key] for key in keys]
    cmap = mcolors.ListedColormap(colors, name)
    
    
    bounds = np.array(keys_nums + [max(keys_nums)+1])
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    return cmap, norm


def plot_square(l: int, color: tuple[np.floating]) -> Image:
    """
    Dado un color, muestra un cuadrado de ese color.

    Uso:
    >>> plot_square(100, (1, 0, 0))
    """
    if isinstance(color, str):
        return Image.new('RGB', (l,l), color)
    return Image.new('RGB', (l, l), tuple(int(255 * c) for c in color[:3]))

def concat_images(images) -> Image:
    """
    Concatena varias imágenes en una sola.
    Está hecha para ser usada en conjunto con 'plot_square'.
    """
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    return new_im

def plot_squares(l, colors):
    """
    Dada una serie de colores, los muestra como una tira de cuadrados coloreados.
    Ejemplo en: https://gist.github.com/joangq/b43e71b3b7cb2af077908702a1436c2f#file-zzz-plot-colors-ipynb
    """
    squares = [plot_square(l, c) for c in colors]
    return concat_images(squares)

def pil_to_base64(image: Image) -> str:
    """
    Codifica una imagen en Base64.
    Útil para graficarlo con HTML.
    """
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    img_base64 = b64encode(img_bytes)
    img_base64_str = img_base64.decode('utf-8')
    return img_base64_str

def pil_to_html(image: Image) -> str:
    """
    Toma una imagen y la convierte en un tag HTML para mostrarla.
    """
    img_base64_str = pil_to_base64(image)
    return f'<div><img src="data:image/png;base64,{img_base64_str}"></div>'

def cmap_norm_to_pickle(cmap, norm, filename):
    """
    Guarda un colormap y una normalización en un archivo pickle.
    """
    with open(filename, 'wb') as f:
        pickle.dump((cmap, norm), f)

def pickle_to_cmap_norm(filename) -> tuple:
    """
    Carga un colormap y una normalización desde un archivo pickle.
    """
    with open(filename, 'rb') as f:
        return pickle.load(f)
    
def iterable_as_hex(iterable, prefix='#'):
    return prefix+''.join(hex(t)[2:] for t in iterable)

def pairwise(xs):
    return zip(xs[::1], xs[1::1])

def flatten(iterable, level=None):
    for item in iterable:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            if level is None or level > 0:
                yield from flatten(item, level=None if level is None else level - 1)
            else:
                yield item
        else:
            yield item

def identity(x):
    return x