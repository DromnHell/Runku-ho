import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def generate_text_without_RAG(model, tokenizer, prompt):
    """
    Generate a text from a model.
    """
    input_ids = tokenizer(prompt, return_tensors = "pt").input_ids.to(model.device)

    # Generate an attention mask to indicate valid tokens (avoid unexpected behavior)
    attention_mask = torch.ones_like(input_ids)

    # No need to compute and stock the gradients in inference.
    with torch.no_grad():
        output = model.generate(
            input_ids,
            attention_mask = attention_mask,  # Ensures the model correctly processes padded sequences.
            max_length = 512, # Total text size (prompt + generated response).
            temperature = 0.7, # Low (~0.3) → + consistent answers, High (~1.0) → + creative and varied.
            top_p = 0.9, # Selects first tokens whose cumulative probability exceeds top_p. So favors probable tokens.
            pad_token_id = tokenizer.eos_token_id # Prevents errors due to missing tokens [PAD].
        )

    return tokenizer.decode(output[0], skip_special_tokens = True)

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

    print("Model loaded successfully !")
    return fused_model, tokenizer

def initialize_rag_pipeline(model, tokenizer, chroma_db_path):
    """
    Build the LangChain pipeline for the RAG la pipeline LangChain pour la RAG.
    """
    # 1) Create a HuggingFace “text-generation” inference pipeline.
    generation_HF_pipeline = pipeline(
        "text-generation",
        model = model,
        tokenizer = tokenizer,
        #max_length = 2048, # Total text size (initial prompt + RAG product + generated response).
        max_new_tokens = 300, # The generated response will be limited to 200 tokens.
        temperature = 0.7, # Low (~0.3) → + consistent answers, High (~1.0) → + creative and varied.
        top_p = 0.9, # Selects first tokens whose cumulative probability exceeds top_p. So favors probable tokens.
        pad_token_id = tokenizer.eos_token_id, # Prevents errors due to missing tokens [PAD].
        truncation = True  # Ensures that input is truncated if it exceeds max_length.
    )

    # 2) Create a LangChain LLM from this pipeline.
    langChain_llm = HuggingFacePipeline(pipeline = generation_HF_pipeline)

    # 3) Create the embedding using the one used for Chroma.
    embedding_function = HuggingFaceEmbeddings(
        model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    # 4) Load existing Chroma database (persist_directory = DB path).
    vectorstore = Chroma(
        collection_name = "french_ryzom_wiki",
        persist_directory = chroma_db_path,
        embedding_function = embedding_function
    )

    # 5) Converts the VectorStore into a retriever.
    retriever = vectorstore.as_retriever(
        search_kwargs = {"k": 3} # k = 3 means that 3 nearest chunks will be returned for each query.
    )

    # 6) Define a system prompt.
    CUSTOM_PROMPT_TEMPLATE = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say you don't know. 
    Please do NOT repeat the context verbatim in your answer, just use it to craft a concise response.
    You have to write only the reponse.

    Context:
    {context}

    Question: {question}

    Answer in a concise manner:
    """
    system_prompt = PromptTemplate(
        input_variables = ["context", "question"],
        template = CUSTOM_PROMPT_TEMPLATE,
    )

    # 7) Builds the “stuff” or “refine” chain, etc.
    rag_chain = RetrievalQA.from_chain_type(
        llm = langChain_llm,
        chain_type = "stuff",
        # “stuff” means injecting the k most relevant documents at once.
        # “refine” means gradually refines the response by building on each successive chunk. Slower but more precise.
        # "map_reduce" means first generate summaries, then synthesize the answer.
        chain_type_kwargs={"prompt": system_prompt},
        return_source_documents = True, # Allow to return the query answer.
        retriever = retriever
    )

    return rag_chain

if __name__ == "__main__":

    fused_model_path = "../data/models/Runku-ho_model"
    chroma_db_path = "../data/tokenized_data/chroma_db_for_RAG"

    print("Loading model and tokenizer...")
    fused_model, tokenizer = load_model(fused_model_path)

    print("Initializing RAG pipeline...")
    rag_chain = initialize_rag_pipeline(fused_model, tokenizer, chroma_db_path)

    print("\nEnter a prompt to generate text (type 'exit' to quit) :")
    while True:
        prompt = input("Prompt : ")
        if prompt.lower() == "exit":
            break

        print("\nGenerating...")
        result = rag_chain.invoke({"query": prompt})
        generated_text = result["result"]
        print(f"\nGenerated Text :\n{generated_text}\n")
