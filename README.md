# Runku-ho

Runku-ho (means “scribe” in Taki Zoraï, the language of a race in the universe of Ryzom) is a tool designed to answer
questions about the lore of Ryzom and to facilitate creative writing within this universe. A LLM has been fine-tuned
using LoRA on my novel "[La Guerre Sacrée](https://la-guerre-sacree.fr/)".

## Table of Contents

- [Installation](#installation)
- [Features](#features)
- [Usage](#usage)
- [Contribution](#contribution)
- [Contact](#contact)

## Installation

To use Runku-ho, download the repository and install the conda environment using the following bash command:

```conda env create -f runku_ho.yml```

## Features

- Scrape lore documents from the French Ryzom wiki.
- Parse data and create a database for the RAG.
- Tokenize data for training a model.
- Train a LoRA model with quantization.
- Generate text using different modes for creative writing and lore questioning.

## USAGE

Usage Instructions (in this order):

* Run ```scrape_ryzom_wiki.py```: Allows scraping lore documents from the french Ryzom wiki.
* Run ```collect_raw_data_for_RAG.py```: Allows collect raw data from the scraped data, necessary for creating the vector database used by the RAG.
* Run ```tokenize_rag_data.py```: Allows creating a Chroma vector database for the RAG.
* Run ```tokenize_training_data.py```: Allows tokenizing the data needed for training the model. The training data (the novel divided into chapters + a .json document providing examples of creative writing from prompts) were created manually.
* Run ```train_with_lora_and_quantization.py```: Allows training a LoRA model with quantization, based on the ```meta-llama/Llama-2-7b-hf``` model.
* Run ```generate_text.py```: Allow to generate text. Mode 1 (Writer) uses the fine-tuned LoRA model for creative writing. Mode 2 (Archivist) uses the ```meta-llama/Llama-2-7b-chat-hf``` model with a RAG to answer questions about Ryzom lore.

## CONTRIBUTION

Contributions are welcome ! The RAG currently needs improvement as it does not perform well.

## CONTACT

For any questions, please contact me at remi.dromnelle@gmail.com.
