from datasets import load_from_disk
from transformers import (
    AutoTokenizer, DataCollatorForLanguageModeling, AutoModelForCausalLM,
    BitsAndBytesConfig, TrainingArguments, Trainer
)
from peft import LoraConfig, get_peft_model, TaskType
import os


def add_attention_mask(sample):
    """
    Adds an attention mask to indicate which tokens should be attended to.
    """
    return {"attention_mask": [1] * len(sample["input_ids"])}

def load_tokenized_data(data_path):
    """
    Loads tokenized dataset and applies attention masks.
    """
    tokenized_data = load_from_disk(data_path)
    train_dataset = tokenized_data["train"].map(add_attention_mask)
    val_dataset = tokenized_data["validation"].map(add_attention_mask)
    return train_dataset, val_dataset


def load_model(base_model_path):
    """
    Loads the base LLaMA-2 model with 8-bit quantization and LoRA configuration.
    """
    tokenizer = AutoTokenizer.from_pretrained(base_model_path)

    # Set a padding token (since LLaMA-2 does not have one by default)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token  # Use <eos> as padding token

    # Enables 8-bit quantization which is optimized for an 8GB VRAM GPU and allow CPU offloading.
    bnb_config = BitsAndBytesConfig(load_in_8bit_fp32_cpu_offload = True)

    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        quantization_config = bnb_config,
        device_map = "auto"  # Allows CPU offloading for out-of-memory cases.
    )

    lora_config = LoraConfig(
        r = 16,  # LoRA rank (small enough to fit in 8GB VRAM, while maintaining efficiency).
        lora_alpha = 32,  # Scaling factor (alpha/r ≈ 2 is a good tradeoff).
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"],  # Focus on attention layers and not FFL.
        lora_dropout = 0.05,  # Prevents overfitting.
        bias = "none",  # No additional bias to save memory.
        task_type = TaskType.CAUSAL_LM  # Auto-regressive task.
    )

    base_model_with_lora = get_peft_model(base_model, lora_config)
    return tokenizer, base_model_with_lora


def get_training_args():
    """
    Defines training hyperparameters optimized for LoRA fine-tuning on an 8GB VRAM GPU.
    """
    return TrainingArguments(
        output_dir = "../data/lora_output",  # Directory for saving checkpoints.
        overwrite_output_dir = True,  # Overwrite existing files if they exist.
        num_train_epochs = 3,  # 3 epochs are enough for LoRA fine-tuning.
        per_device_train_batch_size = 1,  # Small batch size (to avoid OOM errors).
        gradient_accumulation_steps = 4,  # Simulates a larger batch (1 x 4 = 4).
        evaluation_strategy = "epoch",  # Evaluate after each epoch.
        save_strategy = "epoch",  # Save a checkpoint at each epoch.
        logging_steps = 100,  # Log training progress every 100 steps.
        learning_rate = 2e-4,  # Optimized LR for LoRA tuning.
        fp16 = True,  # Use float16 precision to save memory and accelerate training.
        save_total_limit = 2  # Keep only the last 2 checkpoints.
    )


def train_lora(base_model_with_lora, tokenizer, train_dataset, val_dataset):
    """
    Runs the fine-tuning process using LoRA.
    """
    # Use DataCollatorForLanguageModeling(mlm = False) for causal model. “mlm” means "masked language modeling",
    # which is used for bidirectional models like BERT, but not for causal models like ours. We don't want the collator
    # applies random masking to certain tokens in the input text, because we want the model to predict the next token.
    data_collator = DataCollatorForLanguageModeling(tokenizer = tokenizer, mlm = False)

    training_args = get_training_args()

    trainer = Trainer(
        model = base_model_with_lora,
        args = training_args,
        train_dataset = train_dataset,
        eval_dataset = val_dataset,
        data_collator = data_collator
    )

    trainer.train()
    trainer.save_model("../data/lora_output")
    print("LoRA training complete. Model saved in Runku-ho/data/lora_output")


if __name__ == "__main__":

    os.environ["WANDB_DISABLED"] = "true"

    base_model_path = "meta-llama/Llama-2-7b-hf"

    print("Loading tokenized dataset...")
    train_dataset, val_dataset = load_tokenized_data("../data/tokenized_data")

    print("Loading model and tokenizer...")
    tokenizer, base_model_with_lora = load_model(base_model_path)

    print("Starting LoRA fine-tuning...")
    train_lora(base_model_with_lora, tokenizer, train_dataset, val_dataset)
