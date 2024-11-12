from .interpolation import linear_interpolation
from numpy import linspace
from .common import identity
from typing import Callable, Generator, ParamSpec
from collections.abc import Iterable
from .color import Color
from .palette import Palette

P = ParamSpec("P")

class HashableRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __contains__(self, t):
        return self.start <= t <= self.end
    
    def __hash__(self):
        return hash((self.start, self.end))
    
    def __repr__(self):
        return f"HashableRange({self.start}, {self.end})"
    
    def __str__(self):
        return f"[{self.start}; {self.end}]"

ColorRGB = tuple[float, float, float]
class continuous_colorizer_t(Callable[[float], ColorRGB]): ...

def map_between(a, b, f) -> continuous_colorizer_t:
    return lambda t: linear_interpolation(a, b, f(t))

def map_between_n(xs, f=identity) -> continuous_colorizer_t:
    subdivisions = linspace(0, 1, len(xs))
    ranges = [
        HashableRange(subdivisions[i], subdivisions[i+1])
        for i in range(len(subdivisions) - 1)
    ]

    mapping = {
        x: map_between(xs[i], xs[i+1], f)
        for i, x in enumerate(ranges)
    }

    def _(t):
        selected_range = \
            next(range_ for range_ in ranges 
                 if t in range_)
    
        return mapping[selected_range](t)
    
    return _

class CallablePalette:
    def __init__(self, data: dict):
        self.data = data
    
    def __call__(self, t: float) -> Color:
        return self.data[t]
    
    def __getitem__(self, t: float) -> Color:
        return self.data[t]

class ContinuousColorizer:
    def __init__(self, f: continuous_colorizer_t):
        self.f = f

    @classmethod
    def from_colors(cls, colors: Iterable[ColorRGB], 
                    *more_colors: P.args, f=identity) -> 'ContinuousColorizer':
        
        is_color_rgb = (
            isinstance(colors, Iterable)
        and len(colors) == 3 
        and all(isinstance(c, (int, float)) for c in colors))

        if is_color_rgb:
            colors = [colors]

        colors = [*colors, *more_colors]

        return cls(map_between_n(colors, f))

    def _single_color(self, t: float) -> ColorRGB:
        return self.f(t)

    def _multiple_colors(self, ts: list[float]) -> list[ColorRGB]:
        return [self.f(t) for t in ts]
    
    def _lazy_multiple_colors(self, ts: list[float]) -> Generator[ColorRGB, None, None]:
        yield from (self.f(t) for t in ts)

    def get_color(self, t: float) -> Color:
        return Color.from_rgb(self.f(t))
    
    def get_palette(self, ts: list[float], normalize=True) -> Palette:
        if normalize:
            max_v = max(ts)
            min_v = min(ts)
            ts = [(t - min_v) / (max_v - min_v) for t in ts]

        return Palette([self.get_color(t) for t in ts])
    
    def get_discrete_palette(
            self,
            ts: list[float],
            normalize = True,
            as_callable = True):
        
        if normalize:
            max_v = max(ts)
            min_v = min(ts)
            ts_n = [(t - min_v) / (max_v - min_v) for t in ts]
            result = CallablePalette(dict(zip(ts, self.get_palette(ts_n, normalize=False))))
        else:
            result = CallablePalette(dict(zip(ts, self.get_palette(ts, normalize=False))))
        
        return result if as_callable else dict(result.data)
    
    def __call__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], Iterable):
                if not all(isinstance(t, float) for t in args[0]):
                    raise ValueError("All elements in the iterable must be floats.")
                
                return self._multiple_colors(args[0])
            else:
                if not isinstance(args[0], float):
                    raise ValueError("The argument must be a float.")
                
                return self._single_color(args[0])
        else:
            if not all(isinstance(t, float) for t in args):
                raise ValueError("All elements in the iterable must be floats.")
            
            return self._multiple_colors(args)

