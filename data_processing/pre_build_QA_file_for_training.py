import os
import json
import spacy
import random

'''
This script is only used to pre-build the file containing the questions/answers needed to train the model. However, 
you'll need to go back to the built file manually to correct certain questions that SpacCy doesn't recognize correctly.

Note that this file is not the only one in the model training corpus, and that others, including the novel 
“La Guerre Sacrée”, have been manually added to the /raw_data_for_training folder.
'''

def extract_first_paragraph(path):
    """
    Extracts the first paragraph (separated by double newlines) from a file.
    Ignores lines that start with '#' (titles).
    """
    with open(path, "r", encoding = "utf-8") as f:
        text = f.read().strip()

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    for para in paragraphs:
        if not para.startswith("#"):
            return para

    return ""

def detect_question(title, nlp_model):
    """
    Generates a question based on the 'title' using spaCy to detect
    whether it refers to a date, a person, a place, etc.
    """
    if title.isdigit():
        return f"Que s'est-il passé en {title} ?"

    doc = nlp_model(title)

    if doc.ents:
        ent = doc.ents[0]
        label = ent.label_

        if label == "PER":
            return f"Qui est {title} ?"
        elif label in ["LOC", "GPE"]:
            return f"Où se situe {title} ?"
        elif label == "ORG":
            return f"Qu'est-ce que {title} ?"
        elif label == "MISC":
            return f"Qu'est-ce que {title} ?"
        # Generic answer.
        return f"Qu'est-ce que {title} ?"

    # Generic answer.
    return f"Qu'est-ce que {title} ?"

def generate_qa_dataset(nlp_model, scraped_data_path, narrative_corpus_len, output_file, max_ratio = 0.1):
    """
    Generates a Q/A dataset from wiki pages but ensures the total word count does not exceed
    `max_ratio` (default 5%) of the narrative corpus.
    """
    max_words = int(narrative_corpus_len * max_ratio)
    current_word_count = 0
    qa_data = []

    file_list = [f for f in os.listdir(scraped_data_path) if f.endswith(".txt") and f != "La_Guerre_Sacrée_roman.txt"]

    random.shuffle(file_list)

    for filename in file_list:
        title = filename[:-4].replace("_", " ")
        path = os.path.join(scraped_data_path, filename)
        question = detect_question(title, nlp_model)
        answer = extract_first_paragraph(path)

        if answer == "":
            continue

        qa_data.append({"Question": question, "Réponse": answer})
        current_word_count += len(answer.split())

        if current_word_count >= max_words:
            break

    with open(output_file, "w", encoding = "utf-8") as jsonf:
        json.dump(qa_data, jsonf, indent = 4, ensure_ascii=False)

    print(f"Q/A file generated : {output_file} (Size : {current_word_count} words / {max_words} max)")


def get_text_size(file_path):
    """
    Returns the number of words in a text file.
    """
    with open(file_path, "r", encoding = "utf-8") as f:
        text = f.read()
    return len(text.split())

if __name__ == "__main__":
    nlp_model = spacy.load("fr_core_news_lg")

    scraped_data_path = "../data/raw_data/raw_data_from_scraping/scraping_result"
    narrative_corpus_path = os.path.join(scraped_data_path, "La_Guerre_Sacrée_roman.txt")

    narrative_corpus_len = get_text_size(narrative_corpus_path)

    output_file = "../data/raw_data/raw_data_for_training/wiki_QA_example.json"

    generate_qa_dataset(nlp_model, scraped_data_path, narrative_corpus_len, output_file)
