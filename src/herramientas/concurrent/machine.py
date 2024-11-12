from .types import IMachine
from ..ollama import AsyncOllamaClient # type: ignore
from dataclasses import dataclass
from typing import assert_type
from fundar_llms.api.ollama import OllamaResponse # type: ignore
from ..ollama.types import OllamaArgs

class Machine(IMachine[OllamaArgs, OllamaResponse]):
    name: str
    client: AsyncOllamaClient
    busy: bool

    def __init__(self, name: str, ip: str):
        self.name = name
        self.client = AsyncOllamaClient(host=ip)
        self.busy = False
    
    def __str__(self):
        host = self.client._client.base_url
        host = f"{host.host}:{host.port}"
        return f'Machine({self.name}, {host}, is_busy={self.busy})'

    def __repr__(self):
        return str(self)

    async def execute(self, task_data: tuple[int, OllamaArgs]):
        assert isinstance(task_data, tuple)
        (task_index, task) = task_data 
        assert isinstance(task_index, int)

        # TODO: Check that 'task' satisfies PlainPromptInterface schema
        #assert isinstance(task, dict)

        self.busy = True
        result = await self.client.generate(**task)

        self.busy = False
        return task_index, result