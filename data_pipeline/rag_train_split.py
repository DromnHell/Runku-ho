import os
import csv
import re

def extract_data(file_path, rag_data_folder, training_data_folder):
    """
    Extracts data from a text file:
    - Cleaned text (without the summary table) for LLM training
    - Summary table stored in a CSV file for RAG
    - Cleaned text (without the summary table) for RAG
    """
    file_name = os.path.basename(file_path)
    file_name, _ = os.path.splitext(file_name)

    # Define output file paths
    training_txt_file = os.path.join(training_data_folder, f"{file_name}.txt")
    rag_csv_file = os.path.join(rag_data_folder, f"{file_name}_summary_table.csv")
    rag_txt_file = os.path.join(rag_data_folder, f"{file_name}_text.txt")

    # Read the source file
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    # Define the regex pattern to extract the summary table
    pattern = re.compile(r"\[Tableau résumé\](.*)", re.DOTALL)
    match = pattern.search(file_content)

    summary_table = []

    # If summary table
    if match:
        table_text = match.group(1).strip()
        lines = table_text.split("\n")

        # Extract key-value pairs from the summary table
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                summary_table.append([key.strip(), value.strip()])

        # Remove the summary table from the text
        text_without_summary_table = pattern.sub("", file_content).strip()

        # Save the cleaned text for training
        with open(training_txt_file, "w", encoding = "utf-8") as file:
            file.write(text_without_summary_table)

        # Save the summary table in a CSV file for RAG
        with open(rag_csv_file, "w", encoding = "utf-8", newline="") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(["Field", "Value"])  # CSV Header. Maybe to remove later.
            writer.writerows(summary_table)

        # Save the full text without the summary table for RAG
        with open(rag_txt_file, "w", encoding = "utf-8") as file:
            file.write(text_without_summary_table)

    # If no summary table
    else:
        # Save the full text for training
        with open(training_txt_file, "w", encoding = "utf-8") as file:
            file.write(file_content)

        # Save the full text for RAG
        with open(rag_txt_file, "w", encoding = "utf-8") as file:
            file.write(file_content)

if __name__ == "__main__":

    '''base_folder_name = os.path.abspath("../data/french_ryzom_wiki_pages")
    rag_data_folder_name = os.path.abspath("../data/rag")
    training_data_folder_name = os.path.abspath("../data/training")

    file = "Culte_Noir_de_Ma-Duk"
    file_path = os.path.join(base_folder_name, file)
    extract_data(file_path, rag_data_folder_name, training_data_folder_name)'''

    base_folder_name = "../data/french_ryzom_wiki_pages"
    rag_data_folder_name = "../data/rag"
    training_data_folder_name = "../data/training"

    # Ensure output directories exist
    os.makedirs(rag_data_folder_name, exist_ok=True)
    os.makedirs(training_data_folder_name, exist_ok=True)

    files_nb = len([f for f in os.listdir(base_folder_name) if os.path.isfile(os.path.join(base_folder_name, f))])
    i = 0

    # Process all files in the source folder
    for file in os.listdir(base_folder_name):

        print(f"[{i + 1}/{files_nb}] Extraction of {file}...")

        file_path = os.path.join(base_folder_name, file)

        # Ensure only files are processed (skip directories)
        if os.path.isfile(file_path):
            extract_data(file_path, rag_data_folder_name, training_data_folder_name)

        i += 1