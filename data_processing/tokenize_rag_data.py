from tokenize_utils import *

def create_vectorstore(chunks, embedding_model_name, chroma_dir):
    """
    Given a list of text chunks, this function:
    1) Creates embeddings for each chunk using a language model.
    2) Stores them in a Chroma DB local instance.

    :param chunks: A list of text chunks.
    :param embedding_model_name: A language model name or path.
    :param chroma_dir: Where to store the Chroma index on disk.
    :return: The Chroma collection (you can later query it for retrieval).
    """
    client = chromadb.PersistentClient(chroma_dir)

    try:
        client.delete_collection("french_ryzom_wiki")
    except:
        pass

    collection = client.get_or_create_collection("french_ryzom_wiki")

    print(f"Loading the {embedding_model_name} embedding model...")
    embedder = SentenceTransformer(embedding_model_name)

    documents = []
    embeddings = []
    ids = []
    metadatas = []

    for idx, (chunk_text, file_name) in enumerate(chunks):
        documents.append(chunk_text)
        ids.append(f"doc_{idx}")
        embeddings.append(embedder.encode(chunk_text))
        file_name = file_name.removesuffix(".txt").removesuffix(".csv").replace("_", " ")
        file_name_keywords =  ", ".join(extract_keywords(file_name, nlp_model))
        metadatas.append({"file_name_keywords": file_name_keywords})

    print("Adding embeddings to Chroma collection...")

    collection.add(
        documents = documents,
        embeddings = embeddings,
        ids = ids,
        metadatas = metadatas
    )

    return collection


if __name__  ==  "__main__":

    data_to_be_tokenized = "../data/raw_data/raw_data_for_RAG"

    hf_tokenizer_model_name  = "meta-llama/Llama-2-7b-chat-hf"
    embedding_model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    spacy_model_name = "fr_core_news_lg"

    chunk_max_length = 256
    chunk_overlap_ratio = 0.1

    chroma_dir = "../data/tokenized_data/chroma_db_for_RAG"

    print(f"Loading the {spacy_model_name} spaCy model...")
    nlp_model  = spacy.load(spacy_model_name)

    print(f"Loading the {hf_tokenizer_model_name} HF tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(hf_tokenizer_model_name)

    print("Building the corpus chunks...")
    corpus_chunks = build_corpus(data_to_be_tokenized, nlp_model, tokenizer, chunk_max_length, chunk_overlap_ratio, True)

    collection = create_vectorstore(corpus_chunks, embedding_model_name, chroma_dir)

    print("Done ! You can now query your Chroma collection for RAG.")
