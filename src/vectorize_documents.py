# Usage:
# python vectorize_documents.py -t ARG UKR -p ./persist -h multiprocess

from tqdm.contrib.concurrent import process_map
from langchain_core.documents import Document
from glob import glob
from os.path import join as join_paths
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from multiprocessing import cpu_count
from collections.abc import Iterable
from typing import TypeVar
from functools import reduce
from tqdm.auto import tqdm
# from uuid import uuid4 as get_uuid
from uuid import uuid4, uuid5, NAMESPACE_OID, UUID
import chromadb
import argparse
import sys

def get_id(x: str, cast_str=True) -> str | UUID:
    # uid = uuid5(NAMESPACE_OID, x)
    uid = uuid4()
    return str(uid) if cast_str else uid

T = TypeVar('T')

is_verbose = False
def debug_print(*args, **kwargs):
    global is_verbose
    if is_verbose:
        print(*args, **kwargs)

def flatten(nested_list: list[list[T]], max_level=5) -> list[T]:
    return _flatten(nested_list, max_level)

def _flatten(nested_list: list[T | list[T]], current_level) -> list[T]:
    if current_level == 0:
        return nested_list
    else:
        return _flatten([item for sublist in nested_list for item in sublist if isinstance(item, Iterable)], current_level-1)

def split_list_into_chunks(lst, chunk_size):
    return [lst[i:j] for i, j in 
            ((i, i + chunk_size) 
                for i in range(0, len(lst), chunk_size))]

def load_and_split_pdf(file_path: str, loader = None, splitter = None) -> list[str]:
    loader = loader or PyPDFLoader
    splitter = splitter or DEFAULT_RCT_SPLITTER

    return splitter.split_documents(loader(file_path).load())

def load_country_publications(country: str, docs_path='../docs/', how='multiprocess') -> list[list[Document]]:

    options = {
        'multiprocess': lambda x: process_map(load_and_split_pdf, x, max_workers=cpu_count()),
        'singleprocess': lambda x: list(map(load_and_split_pdf, x))
    }

    if how not in options:
        raise ValueError(f"Invalid value for 'how' argument. Expected one of {options.keys()}")

    files = glob(join_paths(docs_path, country.upper() + '*.pdf'))
    load_publications = options[how]

    return load_publications(files)

DEFAULT_RCT_SPLITTER = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", "(?<=\. )", " ", "", "-\n"],
        chunk_size=1000,
        chunk_overlap=0,
        add_start_index=True
)

embedding_model_name = 'sentence-transformers/all-mpnet-base-v2'

def set_model(device: str):
    from sentence_transformers import SentenceTransformer
    global model, embedding_model_name
    model = SentenceTransformer(embedding_model_name, device=device)
    debug_print(f"Model loaded successfully on device: {device}")

# =======================================================================================================================

def main(target: str | list[str], 
         persist_folder: str,
         how: str,
         device: str):
    
    valid_countries = ['ARG', 'TUR', 'UKR', 'EGY']

    if isinstance(target, str):
        target = [target]

    for country in target:
        debug_print(f"Processing country: {country}")

        if country not in valid_countries:
            raise ValueError(f"Invalid country name. Expected one of {valid_countries}")
        
        debug_print('Loading publications...')
        publications = load_country_publications(country.upper(), how=how)
        publications = flatten(publications, 1)

        all_docs, metadatas = zip(*((doc.page_content, doc.metadata) for doc in publications))

        debug_print('Vectorizing documents...')
        embeddings = model.encode(all_docs, show_progress_bar=True, device=device).tolist() # 1.35 it/s @ 1.5 GHz

        # ids = [str(get_uuid()) for _ in range(len(embeddings))]
        ids = map(get_id, all_docs)
        ids = list(ids)

        client = chromadb.PersistentClient(path=persist_folder)

        collection_name = 'imf_publications_'+country.lower()
        try: 
            client.get_collection(collection_name)
            client.delete_collection(collection_name)
        except ValueError:
            pass

        client.create_collection(collection_name, 
                                 embedding_function=None, 
                                 metadata={'hnsw:space': 'cosine'})
        max_batch_size = client.get_max_batch_size()

        same_length = len(embeddings) == len(ids) == len(metadatas) == len(all_docs)
        embeddings_less_than_max_batch_size =  len(embeddings) < max_batch_size

        debug_print(f"All lists have same length: {same_length}")

        debug_print(f"Embeddings less than max batch size: {embeddings_less_than_max_batch_size}")

        # f = (lambda x: split_list_into_chunks(x, max_batch_size)) if not embeddings_less_than_max_batch_size else (lambda x: x)

        collection = client.get_collection(collection_name)

        if embeddings_less_than_max_batch_size:
            collection.add(
                documents  = (list(all_docs)),
                metadatas  = (list(metadatas)),
                ids        = (list(ids)),
                embeddings = (list(embeddings))
            )
        else:
            chunked_documents  = split_list_into_chunks(list(all_docs), max_batch_size)
            chunked_metadatas  = split_list_into_chunks(list(metadatas), max_batch_size)
            chunked_ids        = split_list_into_chunks(list(ids), max_batch_size)
            chunked_embeddings = split_list_into_chunks(list(embeddings), max_batch_size)

            for i in range(len(chunked_documents)):
                collection.add(
                    documents  = chunked_documents[i],
                    metadatas  = chunked_metadatas[i],
                    ids        = chunked_ids[i],
                    embeddings = chunked_embeddings[i]
                )

        debug_print(f"Collection stored successfully. It contains {len(embeddings)} embeddings.")

# =======================================================================================================================

class Parser(argparse.ArgumentParser):
    def __init__(self):
        super(Parser, self).__init__()
        self.add_argument('-t','--target', type=str, nargs='+', required=True, help='Country code of the publications to vectorize')
        self.add_argument('-p','--persist_folder', type=str, default='./persist', help='Folder to store the embeddings')
        self.add_argument('-m','--mode', type=str, default='multiprocess', help='How to load the publications')
        self.add_argument('-d','--device', type=str, default='auto', help='Device to use for vectorization')
        self.add_argument('-v','--verbose', action='store_true', help='Prints more information')

    def parse_args(self):
        self.args = super(Parser, self).parse_args().__dict__
        self.args['how'] = self.args.pop('mode')
        return self


if __name__ == '__main__':
    parser = Parser().parse_args()
    is_verbose = parser.args.pop('verbose', False)

    if not parser.args['target']:
        print("No country code provided. Use -t or --target argument to specify the country code.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    args_str = ' '.join([f"{k}={v}" for k, v in parser.args.items()])
    debug_print(f"Arguments: {args_str}")

    try:
        device = parser.args['device']

        if parser.args['how'] == 'multiprocess':
            from os import environ as environment
            environment['TOKENIZERS_PARALLELISM'] = 'true'

        match device:
            case 'auto':
                from torch import cuda
                device = 'cuda' if cuda.is_available() else 'cpu'
            case 'cuda':
                from torch import cuda
                if not cuda.is_available():
                    raise ValueError("CUDA is not available. Use 'cpu' instead.")
            case 'cpu':
                pass
            case _:
                raise ValueError("Invalid value for 'device' argument. Expected one of ['auto', 'cpu', 'cuda']")

        set_model(device)
        parser.args['device'] = device
        main(**parser.args)
        sys.exit(0)
    except Exception as e:
        raise e
        print(e, file=sys.stderr)
        sys.exit(1)