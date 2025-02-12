import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

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

def generate_text(model, tokenizer, prompt, max_length = 300, temperature = 0.7, top_p = 0.9):
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
            max_length = max_length, # Controls the maximum length of generated text.
            temperature = temperature, # Low (~0.3) → + consistent answers, High (~1.0) → + creative and varied.
            top_p = top_p, # Selects first tokens whose cumulative probability exceeds top_p. So favors probable tokens.
            pad_token_id = tokenizer.eos_token_id # Prevents errors due to missing tokens [PAD].
        )

    return tokenizer.decode(output[0], skip_special_tokens = True)

if __name__ == "__main__":

    fused_model_path = "../data/models/Runku-ho_model"

    print("Loading model and tokenizer...")
    fused_model, tokenizer = load_model(fused_model_path)

    print("\nEnter a prompt to generate text (type 'exit' to quit) :")
    while True:
        prompt = input("Prompt : ")
        if prompt.lower() == "exit":
            break

        print("\nGenerating...")
        generated_text = generate_text(fused_model, tokenizer, prompt)
        print(f"\nGenerated Text :\n{generated_text}\n")
