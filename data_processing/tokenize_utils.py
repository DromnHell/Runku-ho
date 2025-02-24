import os
import glob
import random
import json
import csv
import gc
import spacy
import chromadb
from chromadb.config import Settings
from langchain.docstore.document import Document
from transformers import AutoTokenizer
from datasets import Dataset, DatasetDict
from sentence_transformers import SentenceTransformer
import re

MINIMUM_TEXT_SIZE = 200

def extract_keywords(text, nlp_model):
    """
    Extract the keywords of a text using spaCy.

    :param text: The text from which we want to extract the keywords.
    :param nlp_model : The nlp model used to extract the keywords.

    :return: List of keyword.
    """
    doc = nlp_model(text)
    keywords = [ent.text for ent in doc.ents]
    # Handle manually the date sase.
    date_pattern = re.compile(r'\b(1[0-9]{3}|2[0-9]{3})\b')
    dates = date_pattern.findall(text)
    for d in dates:
        if d not in keywords:
            keywords.append(d)
    return keywords

def segment_text_into_sentences(text, nlp_model):
    """
    Segment text into sentences using spaCy (except for small texts, to avoid crashes).

    :param text: The text to segment.
    :param nlp_model : The nlp model used to segment the text.

    :return: List of tokenized chunks, where each chunk is a list of token IDs.
    """
    if len(text.strip()) < MINIMUM_TEXT_SIZE:
        return [text]
    try:
        doc = nlp_model(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        return sentences
    except Exception as e:
        return [text]

def chunk_by_sentences(sentences, tokenizer, max_length, overlap_ratio):
    """
    Splits a list of sentences into tokenized chunks, ensuring that each chunk
    does not exceed max_length tokens. The function applies an overlap between
    consecutive chunks to maintain contextual coherence.

    :param sentences: List of sentences to be tokenized and chunked.
    :param tokenizer: Hugging Face tokenizer used for tokenization.
    :param max_length: Maximum number of tokens per chunk. Defaults to 512.
    :param overlap_ratio: Proportion of tokens from the end of each chunk
    to be included at the beginning of the next chunk. Defaults to 0.1.

    :return: List of tokenized chunks, where each chunk is a list of token IDs.
    """
    overlap_tokens = int(max_length * overlap_ratio)
    chunks = []
    current_chunk = []
    current_length = 0

    tokenized_sentences = []
    for sentence in sentences:
        tokenized_sentence = tokenizer.encode(sentence, add_special_tokens = False)
        tokenized_sentences.append(tokenized_sentence)

    i = 0
    while i < len(tokenized_sentences):
        tokenized_sentence = tokenized_sentences[i]
        sentence_len = len(tokenized_sentence)

        if current_length + sentence_len > max_length:
            if current_chunk:
                chunks.append(current_chunk)
                # Handle the overlap
                if overlap_tokens > 0:
                    leftover_tokens = []
                    collected_tokens = 0
                    for tokens in reversed(current_chunk):
                        leftover_tokens = tokens + leftover_tokens
                        collected_tokens += len(tokens)
                        if collected_tokens >= overlap_tokens:
                            break
                    current_chunk = [leftover_tokens]
                    current_length = len(leftover_tokens)
                else:
                    current_chunk = []
                    current_length = 0
            else:
                # If the sentence alone exceeds max_length, it is stored as an individual chunk
                chunks.append([tokenized_sentence])
            i += 1
        else:
            current_chunk.append(tokenized_sentence)
            current_length += sentence_len
            i += 1

    # Last chunk
    if current_chunk:
        chunks.append(current_chunk)

    # Merge each chunk (list of token lists) into a single token list
    final_chunks = []
    for chunk in chunks:
        merged_chunks = []
        for tokens in chunk:
            merged_chunks.extend(tokens)
        final_chunks.append(merged_chunks)

    return final_chunks

def chunk_text_with_overlap(text, nlp_model , tokenizer, max_length, overlap_ratio):
    """
    Splits a given text into overlapping chunks based on sentence segmentation.

    :param text: The input text to be chunked.
    :param nlp_model: The NLP model used for sentence segmentation.
    :param tokenizer: The tokenizer used to measure chunk length.
    :param max_length: The maximum length of each chunk.
    :param overlap_ratio: The proportion of overlap between consecutive chunks.

    :return: A list of text chunks with overlapping sentences.
    """
    sentences = segment_text_into_sentences(text, nlp_model )
    chunks = chunk_by_sentences(sentences, tokenizer, max_length, overlap_ratio)
    return chunks

def build_corpus(data_dir, nlp_model, tokenizer, max_length, overlap_ratio, rag_corpus):
    """
    Builds a text corpus by processing and chunking all .txt and .json files in a given directory.
    The output format can be either tokenized chunks (list of token IDs) or text chunks.

    :param data_dir: Path to the directory containing text files and JSON datasets.
    :param nlp_model: The NLP model used for sentence segmentation.
    :param tokenizer: The tokenizer used to encode text (for length checks).
    :param max_length: The maximum length of each chunk (in tokens).
    :param overlap_ratio: The proportion of overlap between consecutive chunks.
    :param rag_corpus: If True, returns chunks as plain text with the corresponding titles.
    :return: A list of chunked texts (strings) or tokenized chunks (lists of token IDs).
    """
    all_chunks = []
    files_to_process = glob.glob(os.path.join(data_dir, "*"))
    files_nb = len(files_to_process)

    for idx, file_path in enumerate(files_to_process):
        file_name = os.path.basename(file_path)
        print(f"[{idx+1}/{files_nb}] Processing {file_name}...")

        if file_path.endswith(".txt"):
            with open(file_path, "r", encoding = "utf-8") as f:
                text = f.read().strip()
                file_chunks = chunk_text_with_overlap(text, nlp_model, tokenizer, max_length, overlap_ratio)

        elif file_path.endswith(".json"):
            with open(file_path, "r", encoding = "utf-8") as f:
                data = json.load(f)
                file_chunks = []

                if len(data) > 0:
                    if "Question" in data[0]:
                        for entry in data:
                            text = f"Question : {entry['Question']}\nRéponse : {entry['Réponse']}"
                            file_chunks.extend(chunk_text_with_overlap(text, nlp_model, tokenizer, max_length, overlap_ratio))

                    elif "Instruction" in data[0]:
                        for entry in data:
                            text = f"Instruction : {entry['Instruction']}\n{entry.get('Prompt', '')}\n{entry.get('Texte', '')}"
                            file_chunks.extend(chunk_text_with_overlap(text, nlp_model, tokenizer, max_length, overlap_ratio))

        elif file_path.endswith(".csv"):
            with open(file_path, "r", encoding = "utf-8") as f:
                reader = csv.DictReader(f, delimiter = ";")
                lines = []
                for row in reader:
                    field = row["Field"].strip()
                    value = row["Value"].strip()
                    if value and value != "-":
                        lines.append(f"{field} : {value}")

                if lines:
                    document_title = file_name.replace("_", " ").replace(".csv", "")
                    text = f"Fiche descriptive de {document_title} :\n" + "\n".join(lines)
                    file_chunks = chunk_text_with_overlap(
                        text, nlp_model, tokenizer, max_length, overlap_ratio
                    )

        else:
            print(f"Skipping unsupported file type: {file_name}")
            continue

        if rag_corpus:
            # We convert token IDs to text, then create the pair (text, file_name).
            decoded_chunks = [
                tokenizer.decode(chunk, skip_special_tokens = True)
                for chunk in file_chunks
            ]
            for chunk_text in decoded_chunks:
                all_chunks.append((chunk_text, file_name))
        else:
            all_chunks.extend(file_chunks)

    return all_chunks