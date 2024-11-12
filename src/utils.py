import numpy
from safetensors.numpy import save_file, load_file
from tqdm.auto import tqdm
from dataclasses import dataclass
from typing import Iterable

def subdict(d, keys):
    return {k: d[k] for k in keys}

@dataclass
class TaggedVector:
    vector_id: str
    text: str
    vector: Iterable[float]
    distance_to: str
    distance: float

    @staticmethod
    def for_question(q: str):
        def _(x):
            (vector_id, text, distance, vector) = x
            return TaggedVector(
                vector_id=vector_id,
                text=text,
                vector=vector,
                distance_to=q,
                distance=distance
            )
        
        return _

    @classmethod
    def from_record(cls, data: dict):
        vector = numpy.zeros((768,))
        for i in range(768):
            vector[i] = data[str(i)]
        return cls(
            vector_id = data['vector_id'],
            text = data['text'],
            distance_to = data['distance_to'],
            distance = data['distance'],
            vector = vector
        )

    def as_record(self) -> dict:
        return (dict(
            vector_id = self.vector_id,
            text = self.text,
            distance_to = self.distance_to,
            distance = self.distance)
            | {str(i): x for i,x in enumerate(self.vector)})