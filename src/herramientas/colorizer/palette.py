from .color import Color    
from .common import dict_as_colormap, plot_square, concat_images, pil_to_html
from IPython.display import display

class Palette(list[Color]):
    """
    Representación de una paleta de colores.
    Tiene utilidades para convertirlo a distintos formatos y mostrarlo,
    especialmente para ser exportado como cmap de matplotlib.
    """
    img = None
    name = None

    @classmethod
    def from_hex(cls, hexes: list[str]):
        """
        Toma una lista de strings hexadecimales y crea una paleta de colores.
        Uso:
        >>> Palette.from_hex(['#FF0000', '#00FF00', '#0000FF'])
        """
        return cls(Color.from_hex(hex) for hex in hexes)
    
    @classmethod
    def from_rgba(cls, rgbas: list[tuple[int]]):
        """
        Toma una lista de tuplas RGBA y crea una paleta de colores.
        Uso:
        >>> Palette.from_rgba([(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255)])
        """
        return cls(Color.from_rgba(rgba) for rgba in rgbas)
    
    @classmethod
    def from_rgb(cls, rgbs: list[tuple[int]]):
        """
        Toma una lista de tuplas RGB y crea una paleta de colores.
        Uso:
        >>> Palette.from_rgb([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
        """
        return cls(Color.from_rgb(rgb) for rgb in rgbs)
    
    @classmethod
    def from_float(cls, floats: list[tuple[float]]):
        """
        Toma una lista de tuplas de valores RGB en formato decimal y crea una paleta de colores.
        Uso:
        >>> Palette.from_float([(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)])
        """
        return cls(Color.from_float(*f) for f in floats)
    
    @classmethod
    def from_iterable(cls, iterables: list):
        """
        Toma una lista de objetos iterables y los convierte en una paleta de colores.
        Uso:
        >>> Palette.from_iterable([(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)])
        """
        return cls(Color.from_iterable(i) for i in iterables)

    @classmethod
    def from_dict(cls, d: dict):
        """
        Toma un diccionario de la forma
        {name: {name: hex, ...}}
        y crea una paleta de colores.

        Uso:
        >>> Palette.from_dict({'primary': {'red': '#FF0000', 'green': '#00FF00', 'blue': '#0000FF'}})
        """
        name = tuple(d.keys())[0]
        colors = [Color.from_dict({'value': v, 'name': k}) for k, v in d[name].items()]
        result = cls(colors)
        result.name = name
        return result
    
    def to_coolors(self):
        """
        Coolors es una página web para crear paletas de colores.
        Esta función convierte la paleta en un link para Coolors.
        Uso:
        >>> Palette.from_hex(['#FF0000', '#00FF00', '#0000FF']).to_coolors() # 'https://www.coolors.co/ff0000-00ff00-0000ff'
        """
        return "https://www.coolors.co/"+ "-".join(c.as_hex()[1:].lower() for c in self)
    
    @classmethod
    def from_coolors(cls, url):
        """
        Crea una paleta a partir de un link de Coolors.
        Uso:
        >>> Palette.from_coolors('https://www.coolors.co/ff0000-00ff00-0000ff') 
        >>> Palette(Color(255, 0, 0, 255), Color(0, 255, 0, 255), Color(0, 0, 255, 255))
        """
        if '/' in url:
            url = url.rsplit("/", 1)[-1]

        url = url.split("-")
        return cls.from_hex(x+"#" for x in url)
    
    def as_image(self, size=100):
        """
        Crea una imagen de la paleta.
        Ver `concat_images` y `plot_square`.
        """
        if self.img is None or self.img.size != (size * len(self), size):
            self.img = concat_images([c.as_image(size) for c in self])
        
        return self.img
    
    def as_dict(self, names: list[str]|bool = None) -> dict:
        """
        Crea un diccionario de la forma {name: hex} a partir de la paleta.
        Uso:
        >>> Palette.from_hex(['#FF0000', '#00FF00', '#0000FF']).as_dict()
        >>> {'0': '#FF0000', '1': '#00FF00', '2': '#0000FF'}
        """
        if not names:
            names = [str(i) for i,_ in enumerate(self)]

        if names is True:
            names = [c.name for c in self]
        
        return {name: color.as_hex() for name, color in zip(names, self)}

    def as_hexes(self) -> list[str]:
        """
        Convierte la paleta en una lista de strings hexadecimales.
        Uso:
        >>> Palette.from_hex(['#FF0000', '#00FF00', '#0000FF']).as_hexes()
        >>> ['#FF0000', '#00FF00', '#0000FF']
        """
        return [c.as_hex() for c in self]
    
    def to_cmap(self, names: list[str] = None):
        """
        Convierte la paleta en un colormap de matplotlib.
        """
        return dict_as_colormap(self.as_dict(names), name=self.name)        
    
    def show(self, size=100):
        """
        Muestra la paleta como una imagen.
        Diseñado para ser usado en un entorno IPython.
        """
        display(self.as_image(size))
    
    def _repr_html_(self):
        """
        Muestra la paleta como un tag HTML.
        """
        img = self.as_image()
        return pil_to_html(img)

    def __str__(self):
        """
        Representación en string de la paleta.
        """
        return "Palette({})".format(", ".join(str(c) for c in self))
    
    def __repr__(self):
        """
        Representación en string de la paleta.
        """
        return str(self)