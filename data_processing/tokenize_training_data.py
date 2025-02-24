from tokenize_utils import *

if __name__ == "__main__":

    data_to_be_tokenized = "../data/raw_data/raw_data_for_training"

    hf_tokenizer_model_name = "meta-llama/Llama-2-7b-hf"
    spacy_model_name = "fr_core_news_lg"

    chunk_max_length = 512
    chunk_overlap_ratio = 0.1
    train_ratio = 0.95

    print(f"Loading the {spacy_model_name} spaCy model...")
    nlp_model  = spacy.load(spacy_model_name)

    print(f"Loading the {hf_tokenizer_model_name} HF tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(hf_tokenizer_model_name)

    print("Building the corpus chunks...")
    corpus_chunks = build_corpus(data_to_be_tokenized, nlp_model , tokenizer, chunk_max_length, chunk_overlap_ratio, False)

    print("Shuffling the corpus chunks...")
    random.shuffle(corpus_chunks)

    print("Building the training and the validation sets...")
    n_total = len(corpus_chunks)
    n_train = int(n_total * train_ratio)
    train_data = corpus_chunks[:n_train]
    val_data = corpus_chunks[n_train:]

    print("Saving into a hugging face dataset...")
    train_dataset = Dataset.from_dict({"input_ids": train_data})
    val_dataset = Dataset.from_dict({"input_ids": val_data})

    dataset = DatasetDict({
        "train": train_dataset,
        "validation": val_dataset
    })

    dataset.save_to_disk("../data/tokenized_data/tokenized_training_data")

    print(f"Done ! You can now train a model and your tonekized data.")


