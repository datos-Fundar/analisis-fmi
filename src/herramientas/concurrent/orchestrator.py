from .types import IOrchestrator
from .machine import Machine
import asyncio
from tqdm import tqdm # type: ignore
from typing import MutableSequence, List, Sequence, Optional
from typing import cast, assert_type
from fundar_llms.api.ollama import OllamaResponse # type: ignore
from ..ollama.types import OllamaArgs
from fundar import json

class Orchestrator(IOrchestrator):
    machines: List[Machine]

    def __init__(self, machines: List[Machine]):
        self.machines = machines

    async def run_tasks(self, tasks_p: Sequence[OllamaArgs]):
        task_queue: asyncio.Queue[Optional[tuple[int, OllamaArgs]]] = asyncio.Queue()

        for index, task in enumerate(tasks_p):
            await task_queue.put((index, task))

        total_tasks = len(tasks_p)
        results: List[Optional[OllamaResponse]] = [None] * total_tasks
        
        pbar = tqdm(total=total_tasks)

        workers = [
            asyncio.create_task(self.worker(machine, results, task_queue, pbar))
            for machine in self.machines
        ]

        await task_queue.join()

        for _ in self.machines:
            await task_queue.put(None)

        await asyncio.gather(*workers)
        pbar.close()
        
        return cast(List[OllamaResponse], results)

    async def worker(self, 
                     machine: Machine, 
                     results: MutableSequence[OllamaResponse], 
                     task_queue: asyncio.Queue, 
                     pbar: tqdm):
        while True:
            task_data: Optional[tuple[int, OllamaArgs]] = await task_queue.get()

            if task_data is None:
                task_queue.task_done()
                break

            assert_type(task_data, tuple[int, OllamaArgs])

            task_index, result = await machine.execute(task_data)
            results[task_index] = result

            ### MODIFICACION AD-HOC

            result.extra['run_on'] = machine.name
            extra = result.extra
            
            try:
                qid = extra['qid']
            except Exception as ex:
                qid = ''

            try:
                presidente = extra['presidente']
            except Exception as ex:
                presidente = ''
            
            timestamp = result.created_at.replace(':', '_').replace('.', '__')
            name = f'../data/{qid}-{presidente}_{timestamp}.json'
            json.dump(
                result.to_dict(),
                name
            )

            ### ====================

            task_queue.task_done()
            pbar.update(1)