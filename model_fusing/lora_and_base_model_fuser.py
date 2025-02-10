import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def merge_lora_and_save(base_model_path, lora_adapters_path, fused_model_path):
    """
    Loads the base model, applies the LoRA adapters, merges them into the model,
    and saves the fully fused model without deleting the original adapters.
    """
    print("🔄 Loading base model...")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype = torch.float16 # Loads the base model directly in float16 to avoid memory overload.
    )

    print("Loading LoRA adapters...")
    base_model_with_lora = PeftModel.from_pretrained(base_model, lora_adapters_path)

    print("Merging LoRA adapters into the base model...")
    fused_model = base_model_with_lora.merge_and_unload()

    print(f"Saving fused model to : {fused_model_path}")
    fused_model.save_pretrained(fused_model_path)

    print(f"Saving tokenizer to : {fused_model_path}")
    tokenizer = AutoTokenizer.from_pretrained(base_model_path)
    tokenizer.save_pretrained(fused_model_path)

    print("LoRA model successfully fused and saved !")

if __name__ == "__main__":

    base_model_path = "meta-llama/Llama-2-7b-hf"
    lora_adapters_path = "../data/lora_output"
    fused_model_path = "../data/lora_fused"

    merge_lora_and_save(base_model_path, lora_adapters_path, fused_model_path)
