from IPython.display import display
from PIL import Image

class Color:
    """
    Representación de un color.
    Tiene utilidades para convertirlo a distintos formatos y mostrarlo.
    """
    img = None
    name = None

    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @classmethod
    def from_hex(cls, hex: str):
        """
        Crea un color a partir de un string hexadecimal.
        Uso:
        >>> Color.from_hex("#FF0000")
        """
        hex = hex.lstrip("#")
        return cls(*[int(hex[i:i+2], 16) for i in (0, 2, 4)])
    
    @classmethod
    def from_rgba(cls, rgba: tuple[int]):
        """
        Crea un color a partir de una tupla de valores RGBA.
        Uso:
        >>> Color.from_rgba((255, 0, 0, 255))
        """
        return cls(*rgba)

    @classmethod
    def from_rgb(cls, rgb: tuple[int]):
        """
        Crea un color a partir de una tupla de valores RGB.
        Uso:
        >>> Color.from_rgb((255, 0, 0))
        """
        return cls(*rgb, 255)
    
    @classmethod
    def from_float(cls, r: float, g: float, b: float, a: float = 1.0):
        """
        Crea un color a partir de valores RGB en formato decimal.
        Uso:
        >>> Color.from_float(1.0, 0.0, 0.0)
        """
        return cls(*[int(255 * c) for c in (r, g, b, a)])
    
    @classmethod
    def from_iterable(cls, iterable):
        """
        Toma un objeto iterable (a.k.a que tenga '__iter__') y lo convierte en un color.
        Uso:
        >>> Color.from_iterable((1.0, 0.0, 0.0))
        >>> Color.from_iterable([1.0, 0.0, 0.0])
        >>> Color.from_iterable((x for x in range(0,1,0.1)))
        """
        if all(isinstance(i, float) for i in iterable):
            return cls.from_float(*iterable)
        return cls(*iterable)
    
    @classmethod
    def from_dict(cls, d):
        """
        Toma un diccionario de la forma:
        {'value': hex, 'name': str}

        Uso:
        >>> Color.from_dict({'value': '#FF0000', 'name': 'red'})
        """
        result = cls.from_hex(d['value'])
        result.name = d.get('name')
        return result


    @classmethod
    def from_records(cls, d, **kwargs):
        """
        Toma un diccionario y usa los kwargs para acceder a los
        contenidos.

        Uso:
        >>> Color.from_records({'color': '#FF0000', 'title': 'red'}, value='color', name='title')
        """
        return cls.from_dict({'value': d[kwargs['value']], 'name': d.get(kwargs.get('name'))})
    
    def as_hex(self):
        """
        Convierte el color a un string hexadecimal.
        Uso:
        >>> Color(255, 0, 0).as_hex() # '#FF0000'
        """
        return "#{:02x}{:02x}{:02x}".format(self.r, self.g, self.b).upper()

    def as_rgba(self):
        """
        Convierte el color a una tupla de valores RGBA.
        Uso:
        >>> Color(255, 0, 0).as_rgba() # (255, 0, 0, 255)
        """
        return (self.r, self.g, self.b, self.a)
    
    def as_rgb(self):
        """
        Convierte el color a una tupla de valores RGB.
        Uso:
        >>> Color(255, 0, 0).as_rgb() # (255, 0, 0)
        """
        return (self.r, self.g, self.b)
    
    def __str__(self):
        """
        Representación en string del color.
        >>> str(Color(255, 0, 0)) # "Color(255, 0, 0, 255)"
        """
        return "Color({}, {}, {}, {})".format(self.r, self.g, self.b, self.a)

    def as_image(self, size=100):
        """
        Crea una imagen de un cuadrado del color.
        """
        if self.img is None or self.img.size != (size, size):
            self.img = Image.new('RGB', (size, size), self.as_rgb())
        
        return self.img
    
    def show(self, size=100):
        """
        Muestra el color como una imagen.
        Diseñado para ser usado en un entorno IPython.
        """
        display(self.as_image(size))

    def _repr_html_(self):
        """
        Muestra el color como un tag HTML.
        """
        img = self.as_image()
        return f'<div style="background-color: {self.as_hex()}; width: {img.size[0]}px; height: {img.size[1]}px;"></div>'