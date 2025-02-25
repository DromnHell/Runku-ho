import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from stopping_criteria import *
import spacy
import re
import sys

def generate_text_without_RAG(model, tokenizer, prompt, max_new_tokens, temperature):
    """
    Generate a text from a prompt.
    """
    input_ids = tokenizer(prompt, return_tensors = "pt").input_ids.to(model.device)

    # Create a stop criteria.
    stop_criteria = StoppingCriteriaList([EndOfSentenceStoppingCriteria(tokenizer)])

    # Generate an attention mask to indicate valid tokens (avoid unexpected behavior)
    attention_mask = torch.ones_like(input_ids)

    # No need to compute and stock the gradients in inference.
    with torch.no_grad():
        output = model.generate(
            input_ids,
            attention_mask = attention_mask,  # Ensures the model correctly processes padded sequences.
            max_new_tokens = max_new_tokens,
            temperature = temperature, # Low (~0.3) → + consistent answers, High (~1.0) → + creative and varied.
            top_p = 0.9, # Selects first tokens whose cumulative probability exceeds top_p. So favors probable tokens.
            pad_token_id = tokenizer.eos_token_id # Prevents errors due to missing tokens [PAD].
            #stopping_criteria = stop_criteria
    )

    generated_text = tokenizer.decode(output[0], skip_special_tokens = True)

    return {"result": generated_text}


def extract_keywords(text, nlp_model):
    """
    Extract the keywords of a text using spaCy.

    :param text: The text from which we want to extract the keywords.
    :param nlp_model : The nlp model used to extract the keywords.

    :return: List of keyword.
    """
    doc = nlp_model(text)
    keywords = [ent.text for ent in doc.ents]
    # Handle manually the date.
    date_pattern = re.compile(r'\b(1[0-9]{3}|2[0-9]{3})\b')
    dates = date_pattern.findall(text)
    for d in dates:
        if d not in keywords:
            keywords.append(d)
    return keywords


def build_keywords_filter_from_prompt(prompt, nlp_model, field = "file_name_keywords"):
    """
    Extracts keywords from the prompt using the provided NLP model and builds a filter
    that matches documents whose 'file_name_keywords' field contains any of these keywords.

    :param prompt: The text from which we want to extract the keywords.
    :param nlp_model : The nlp model used to extract the keywords.
    :field: The field where to do the keywords search.

    :return: List of keywords.
    """
    keywords = extract_keywords(prompt, nlp_model)
    if keywords:
        return {field: {"$in": keywords}}
    else:
        return None

def initialize_llm_and_retriever(model, tokenizer, chroma_db_path, nlp_model, prompt, max_new_tokens, temperature):
    """
    This function creates the LangChain LLM wrapper and sets up the vector store retriever.
    It now uses a hybrid search approach combining semantic similarity and BM25 (lexical) search.

    Parameters:
    - model, tokenizer: Loaded HF model and tokenizer.
    - chroma_db_path: The path to the persistent Chroma vector store.
    - nlp_model: The nlm model used for the filtering.
    - prompt: The prompt used for the filtering.
    - max_new_tokens: Maximum tokens for generation.
    - temperature: Temperature for generation.

    Returns:
    - langchain_llm: The LangChain LLM wrapped around the HF pipeline.
    - retriever: A retriever built from the Chroma vector store with hybrid search.
    """
    stop_criteria = StoppingCriteriaList([EndOfSentenceStoppingCriteria(tokenizer)])

    generation_HF_pipeline = pipeline(
        "text-generation",
        model = model,
        tokenizer = tokenizer,
        max_new_tokens = max_new_tokens,
        temperature = temperature,
        top_p = 0.9,
        pad_token_id = tokenizer.eos_token_id,
        stopping_criteria = stop_criteria
    )

    langchain_llm = HuggingFacePipeline(pipeline = generation_HF_pipeline)

    embedding_function = HuggingFaceEmbeddings(
        model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    vectorstore = Chroma(
        collection_name = "french_ryzom_wiki",
        persist_directory = chroma_db_path,
        embedding_function = embedding_function
    )

    collection_data = vectorstore.get()
    documents = [
        Document(
            page_content = text,
            id = id,
            metadata = {"file_name_keywords": metadata["file_name_keywords"]}
        )
        for text, metadata, id in zip(collection_data["documents"], collection_data["metadatas"], collection_data["ids"])
    ]

    # Standard retriever using vector similarity.
    vector_retriever = vectorstore.as_retriever(search_kwargs = {"k": 2})

    search_kwargs = {"k": 1}
    # Filter the chunk by the common keywords between the prompt and their title.
    filter_criteria = build_keywords_filter_from_prompt(prompt, nlp_model)
    if filter_criteria is not None:
        search_kwargs["filter"] = filter_criteria

    # Standard retriever using vector similarity, but with filtering.
    vector_retriever_with_filtering = vectorstore.as_retriever(search_kwargs = search_kwargs)

    # Keyword-based retriever using BM25.
    keyword_retriever = BM25Retriever.from_documents(
        documents = documents,
        kwargs = {"k": 1}
    )

    # Ensemble retriever: combine vector et BM25 retrievers.
    ensemble_retriever = EnsembleRetriever(
        retrievers = [vector_retriever, vector_retriever_with_filtering, keyword_retriever],
    )

    return langchain_llm, ensemble_retriever

def initialize_rag_pipeline_for_writer_mode(model, tokenizer, chroma_db_path, nlp_model, prompt):
    """
    CURRENTLY NOT USED.
    Builds a RAG pipeline using 'refine' chain type.
    This mode (Writer mode) aims for more creative, iterative answers.
    """
    langchain_llm, retriever = initialize_llm_and_retriever(model, tokenizer, chroma_db_path, nlp_model, prompt,
                                                            500, 0.7)

    CUSTOM_PROMPT_TEMPLATE = """Tu disposes d'un certain contexte concernant un univers fictif. Utilise-le pour répondre
     à l'instruction de manière **créative et immersive**. Ta réponse doit être **fluide, détaillée et cohérente avec le
     contexte fourni**. Si le contexte ne permet pas d'apporter une réponse crédible, écris simplement : "Je ne sais pas."
     
     Contexte :
     {context}
     
     Instruction :
     {question}
     
     Texte généré (sois créatif et descriptif) :
    """

    question_prompt = PromptTemplate(
        input_variables = ["context", "question"],
        template = CUSTOM_PROMPT_TEMPLATE
    )

    REFINE_PROMPT_TEMPLATE = """Tu dois **améliorer** le texte généré précédemment en intégrant de 
    **nouvelles informations** issues du **contexte supplémentaire**.  ** Ne répète pas** simplement le texte existant,
     mais **enrichis-le** en ajoutant :  
     - **Des détails pertinents**,  
     - **Des précisions immersives**,  
     - **Une meilleure fluidité stylistique**.

    Contexte supplémentaire :
    {context}

    Texte généré précédement :
    {existing_answer}

    Instruction :
    {question}
     
    Texte généré amélioré (plus riche, précis et fluide) :
    """

    refine_prompt = PromptTemplate(
        input_variables = ["context", "existing_answer", "question"],
        template = REFINE_PROMPT_TEMPLATE
    )

    rag_chain = RetrievalQA.from_chain_type(
        llm = langchain_llm,
        chain_type = "refine",
        chain_type_kwargs = {
            "question_prompt": question_prompt,
            "refine_prompt": refine_prompt,
            "document_variable_name": "context"
    },
        return_source_documents = True,
        retriever = retriever
    )

    return rag_chain

def initialize_rag_pipeline_for_archivist_mode(model, tokenizer, chroma_db_path, nlp_model, prompt):
    """
    Builds a RAG pipeline using 'map_reduce' chain type.
    This mode (Archivist mode) targets concise, fact-oriented answers.
    """
    langchain_llm, retriever = initialize_llm_and_retriever(model, tokenizer, chroma_db_path, nlp_model, prompt, 200, 0.3)

    MAP_PROMPT_TEMPLATE  = """Tu disposes d'un **contexte** contenant des informations sur un **univers fictif**.  
    Résume ce contexte de manière concise et factuelle.  
    **Ne copie pas mot pour mot**, mais reformule les informations essentielles.  

    Contexte :
    {context}

    Résumé du contexte : 
    """

    map_prompt = PromptTemplate(
        input_variables = ["context"],
        template = MAP_PROMPT_TEMPLATE
    )

    REDUCE_PROMPT_TEMPLATE  = """Tu disposes d'un ensemble de **résumés** d'un contexte sur un **univers fictif**.  
    Utilise ces résumés pour répondre à la question suivante de manière **précise et concise**.  
    **Ne copie pas mot pour mot**, mais synthétise la réponse de manière claire et compréhensible.  
    Si les résumés **ne permettent pas** de répondre, écris simplement : **"Je ne sais pas."**
    
    Résumés disponibles : 
    {summaries}
    
    Question :
    {question}
    
    Réponse (courte et factuelle) :
    """

    reduce_prompt = PromptTemplate(
        input_variables=["summaries", "question"],
        template = REDUCE_PROMPT_TEMPLATE
    )

    rag_chain = RetrievalQA.from_chain_type(
        llm = langchain_llm,
        chain_type = "map_reduce",
        chain_type_kwargs = {
            "question_prompt": map_prompt,
            "combine_prompt": reduce_prompt,
        },
        return_source_documents = True,
        retriever = retriever
    )

    return rag_chain


def load_model(fused_model_path):
    """
    Loads the fine-tuned model with 4-bit quantization.
    """
    bnb_config = BitsAndBytesConfig(
        load_in_4bit = True,  # Stores the model weights in 4-bit quantized format to significantly reduce VRAM usage.
        # This applies quantization to the model parameters, but during computation, they will be dequantized to a
        # higher precision format.

        bnb_4bit_compute_dtype = torch.float16,  # Specifies the internal computation data type after dequantization.
        # Although weights are stored in 4-bit format, they are converted back (dequantized) to float16 before matrix
        # multiplications. float16 is chosen because it balances computation speed and numerical precision, while
        # also being supported by most GPUs.

        bnb_4bit_use_double_quant = True  # Enables second-level quantization, also known as "double quantization."
        # In addition to storing weights in 4-bit, this applies quantization to the scaling factors used for
        # dequantization. Instead of keeping scale factors in float32 (which consumes memory), they are quantized as
        # well, further reducing VRAM usage. This technique allows even more compact storage without significantly
        # impacting model accuracy.
    )

    tokenizer = AutoTokenizer.from_pretrained(fused_model_path)

    # Set a padding token (since LLaMA-2 does not have one by default)
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})

    fused_model = AutoModelForCausalLM.from_pretrained(
        fused_model_path,
        quantization_config = bnb_config,
        device_map = "auto"  # Allows CPU offloading for out-of-memory cases.
    )

    return fused_model, tokenizer


if __name__ == "__main__":

    creative_model_path = "../data/models/Runku-ho_model"
    chat_model_path = "meta-llama/Llama-2-7b-chat-hf"
    chroma_db_path = "../data/tokenized_data/chroma_db_for_RAG"

    while True:
        print("Select the Runku-ho mode :")
        print("1 - Writer mode.")
        print("2 - Archivist mode.")
        choice = input("Entrez 1 ou 2 : ").strip()
        if choice == "1" or choice == "2":
            break
        else:
            print("Invalid choice.")

    if choice == "1":
        selected_model_path = creative_model_path
        mode = "writer mode"
    elif choice == "2":
        selected_model_path = chat_model_path
        mode = "archivist mode"

    print(f"Loading LLM and tokenizer...")
    model, tokenizer = load_model(selected_model_path)

    if choice == "2":
        print(f"Loading nlp model for filtering...")
        nlp_model = spacy.load("fr_core_news_lg")

    print("Model(s) loaded successfully !")

    print("\nEnter a prompt to generate text (type 'exit' to quit) :")
    while True:
        prompt = input("Prompt : ")
        if prompt.lower() == "exit":
            break

        if choice == "2":
            print(f"Initializing RAG pipeline for {mode}...")
            rag_chain = initialize_rag_pipeline_for_archivist_mode(model, tokenizer, chroma_db_path, nlp_model, prompt)
            print("RAG pipeline initialized !")

        print("\nGenerating...")

        if choice == "1":
            result = generate_text_without_RAG(model, tokenizer, prompt, 500, 0.7)
        elif choice == "2":
            result = rag_chain.invoke({"query": prompt})

        generated_text = result["result"]
        print(f"\nGenerated Text :\n{generated_text}\n")
