from fundar_llms.api.interface import PlainPromptInterface, BaseResponse # type: ignore
from fundar_llms.api.ollama import OllamaClient, OllamaResponse # type: ignore
from typing import Optional, List # type: ignore
from fundar_llms._types import Base64, Context # type: ignore
from tqdm.contrib.concurrent import thread_map # type: ignore
from concurrent.futures import ThreadPoolExecutor, as_completed # type: ignore
from tqdm import tqdm # type: ignore

# TODO: Incluir esto en
# fundar_llms.api.ollama

class OllamaArgs: ...

class RunnableInstance:
    """
    Wrapper de una función ejecutable.
    Está para poder compilar funciones
    y ser ejecutadas en otro thread.
    """
    def __init__(self, f, args, kwargs):
        self.f = f
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *_, **__):
        return self.f(*self.args, **self.kwargs)

def thread_apply(func_list, arg=None):
    """
    Función dual a 'thread_map'.
    Toma una lista de funciones y un solo argumento,
    y ejecuta todas las funciones con ese argumento.
    """    
    results = [None] * len(func_list)

    with ThreadPoolExecutor() as executor:
        futures = []

        for idx, func in enumerate(func_list):
            future = executor.submit(func, arg)
            future.idx = idx
            futures.append(future)

        for future in tqdm(as_completed(futures), total=len(futures)):
            idx = future.idx
            results[idx] = future.result()
    return results


def run_instances(f):
    """
    Decorador que busca la funcion de igual nombre
    en las instancias registradas en la unidad central.

    Devuelve una funcion que ejecuta la funcion encontrada
    en cada una de las instancias registradas, cada cómputo
    se ejecuta en un hilo distinto.
    """
    fname = f.__name__
    def _(self: 'DistributedOllamaClients', *args, **kwargs):
            functions = [RunnableInstance(getattr(x, fname), args, kwargs) for x in self.clients]
            return thread_apply(functions)
    
    return _

class DistributedOllamaClients(PlainPromptInterface):
    def __init__(self, uris: list[str]):
        self.uris = uris
        self.clients = [
            OllamaClient(host=uri)
            for uri in uris
        ]

    @run_instances
    def generate( # type: ignore
            self,
            model: str,
            prompt: str,
            raw: Optional[bool] = None,
            image: Optional[Base64] = None,
            suffix: Optional[str] = None,
            format: Optional[str] = None,
            system: Optional[str] = None,
            context: Optional[Context] = None,
            stream: Optional[bool] = None,
            num_ctx: Optional[int] = None,
            num_predict: Optional[int] = None,
            temperature: Optional[float] = None,
            top_k: Optional[int] = None,
            top_p: Optional[float] = None,
            *args,
            **kwargs
    ) -> list[BaseResponse]: ... # type: ignore
    
    @run_instances
    def list(self): ...

    def generates(
            self,
            args: List[OllamaArgs]
    ):
        """
        Espera una lista de argumentos, una por cada
        instancia de Ollama, y envia solicitudes
        usandon un hilo por instancia.

        Devuelve la acumulación de los resultados en orden.
        """
        assert len(args) == len(self.clients)
        zip_ = zip(self.clients, args)
        functions = [RunnableInstance(c.generate, (), a)
                     for c,a in zip_]
        
        return thread_apply(functions)