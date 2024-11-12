from abc import ABC as AbstractBaseClass, abstractmethod
from fundar_llms.api.interface import PlainPromptInterface # type: ignore
from typing import Tuple, TypeVar, Generic, Sequence

T = TypeVar('T') # tipo de la Task
R = TypeVar('R') # tipo de la Respuesta

class IMachine(Generic[T, R], AbstractBaseClass):
    name: str
    client: PlainPromptInterface
    busy: bool

    @abstractmethod
    async def execute(
        self, 
        task_data: Tuple[int, T]
        ) -> Tuple[int, R]: ...

class IOrchestrator(Generic[T, R], AbstractBaseClass):
    machines: Sequence[IMachine[T, R]]

    @abstractmethod
    async def run_tasks(
        self, 
        tasks_p: Sequence[T]
        ) -> Sequence[R]: ...