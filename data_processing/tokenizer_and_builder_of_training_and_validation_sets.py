import os
import glob
import random
import spacy
from transformers import AutoTokenizer
from datasets import Dataset, DatasetDict


def segment_text_into_sentences(text, nlp_model ):
    """
    Segment text into sentences using spaCy.

    :param text: The text to segment.
    :param nlp_model : The nlp model used to segment the text.

    :return: List of tokenized chunks, where each chunk is a list of token IDs.
    """
    doc = nlp_model (text)
    sentences = [sent.text.strip() for sent in doc.sents]
    return sentences

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

def build_corpus(data_dir, nlp_model , tokenizer, max_length, overlap_ratio):
    """
    Builds a text corpus by processing and chunking all .txt files in a given directory.

    :param data_dir: Path to the directory containing text files.
    :param nlp_model: The NLP model used for sentence segmentation.
    :param tokenizer: The tokenizer used to encode and decode text chunks.
    :param max_length: The maximum length of each chunk.
    :param overlap_ratio: The proportion of overlap between consecutive chunks.

    :return: A list of processed text chunks.
    """
    all_chunks = []
    txt_files = glob.glob(os.path.join(data_dir, "*.txt"))

    for fpath in txt_files:
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read().strip()

            file_chunks = chunk_text_with_overlap(text, nlp_model , tokenizer, max_length, overlap_ratio)

            all_chunks.extend(file_chunks)

    return all_chunks


if __name__ == "__main__":

    data_to_be_tokenized = "../data/data_to_be_tokenized"
    model_name = "meta-llama/Llama-2-7b-hf"
    chunk_max_length = 512
    chunk_overlap_ratio = 0.1
    train_ratio = 0.95

    nlp_model  = spacy.load("fr_core_news_sm")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Transform the text corpus in tokens chunks
    corpus_chunks = build_corpus(data_to_be_tokenized, nlp_model , tokenizer, chunk_max_length, chunk_overlap_ratio)

    random.shuffle(corpus_chunks)

    # Build the training and the validation sets
    n_total = len(corpus_chunks)
    n_train = int(n_total * train_ratio)
    train_data = corpus_chunks[:n_train]
    val_data = corpus_chunks[n_train:]

    # Save the data into a hugging face dataset
    train_dataset = Dataset.from_dict({"input_ids": train_data})
    val_dataset = Dataset.from_dict({"input_ids": val_data})

    dataset = DatasetDict({
        "train": train_dataset,
        "validation": val_dataset
    })

    dataset.save_to_disk("../data/tokenized_data")


