from langchain import HuggingFacePipeline
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index import ComposableGraph, GPTListIndex, LLMPredictor, GPTVectorStoreIndex, ServiceContext, \
    SimpleDirectoryReader, LangchainEmbedding

from file import check_index_file_exists, get_index_filepath, get_name_with_json_extension

MODEL_NAME = "IlyaGusev/fred_t5_ru_turbo_alpaca"

llm_predictor = LLMPredictor(
    llm=HuggingFacePipeline.from_model_id(
        model_id=MODEL_NAME,
        task="text2text-generation",
        model_kwargs={"temperature":0.1, "max_length":1500},
        device=1
    )
)

embed_model = LangchainEmbedding(HuggingFaceEmbeddings(model_name="ai-forever/sbert_large_mt_nlu_ru"))

service_context = ServiceContext.from_defaults(chunk_size_limit=512, llm_predictor=llm_predictor, embed_model=embed_model)


def create_index(filepath, index_name):
    index = get_index_by_index_name(index_name)
    if index is not None:
        return index

    index_name = get_name_with_json_extension(index_name)
    documents = SimpleDirectoryReader(input_files=[filepath]).load_data()
    index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)
    index.save_to_disk(get_index_filepath(index_name))
    return index


def get_index_by_index_name(index_name):
    index_name = get_name_with_json_extension(index_name)
    if check_index_file_exists(index_name) is False:
        return None
    index_filepath = get_index_filepath(index_name)
    index = GPTVectorStoreIndex.load_from_disk(index_filepath, service_context=service_context)
    return index


def create_graph(index_sets, graph_name):
    graph_name = get_name_with_json_extension(graph_name)
    graph = ComposableGraph.from_indices(GPTListIndex,
                                         [index for _, index in index_sets.items()],
                                         index_summaries=[f"This index contains {indexName}" for indexName, _ in index_sets.items()],
                                         service_context=service_context)
    graph.save_to_disk(get_index_filepath(graph_name))
    return graph


def get_graph_by_graph_name(graph_name):
    graph_name = get_name_with_json_extension(graph_name)
    graph_path = get_index_filepath(graph_name)
    graph = ComposableGraph.load_from_disk(graph_path, service_context=service_context)
    return graph