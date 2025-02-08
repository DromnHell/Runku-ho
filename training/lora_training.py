from datasets import load_from_disk
from transformers import (AutoTokenizer, DataCollatorForLanguageModeling)


if __name__ == "__main__":

    tokenized_data = load_from_disk("../data/tokenized_data")
    model_name = "meta-llama/Llama-2-7b-hf"

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    train_dataset = tokenized_data["train"]
    val_dataset = tokenized_data["val"]

    # Add an attention mask
    def add_attention_mask(example):
        ids = example["input_ids"]
        return {"attention_mask": [1] * len(ids)}

    train_dataset = train_dataset.map(add_attention_mask)
    val_dataset = val_dataset.map(add_attention_mask)

    # Use DataCollatorForLanguageModeling(mlm = False) for causal model.
    # “mlm” means "masked language modeling", which is used for bidirectional models like BERT,
    # but not for causal models like ours. We don't want the collator applies random masking to
    # certain tokens in the input text, because we want the model to predict the next token.
    data_collator = DataCollatorForLanguageModeling(tokenizer = tokenizer, mlm = False)
