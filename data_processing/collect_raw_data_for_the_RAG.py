import os
import csv
import re

def extract_data(scraped_file_path, raw_data_rag_path):
    """
    Extracts data from a text file:
    - Summary table stored in a CSV file for RAG
    - Cleaned text (without the summary table) for RAG
    """
    file_name = os.path.basename(scraped_file_path)
    file_name, _ = os.path.splitext(file_name)

    # Define output file paths
    rag_csv_file = os.path.join(raw_data_rag_path, f"{file_name}_summary_table.csv")
    rag_txt_file = os.path.join(raw_data_rag_path, f"{file_name}_text.txt")

    # Read the source file
    with open(scraped_file_path, "r", encoding="utf-8") as file:
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
        # Save the full text for RAG
        with open(rag_txt_file, "w", encoding = "utf-8") as file:
            file.write(file_content)

if __name__ == "__main__":

    scraped_data_path = "../data/raw_data/raw_data_from_scraping/scraping_result"
    raw_data_rag_path = "../data/raw_data/raw_data_for_the_RAG"

    os.makedirs(raw_data_rag_path, exist_ok = True)

    files_nb = len([f for f in os.listdir(scraped_data_path) if os.path.isfile(os.path.join(scraped_data_path, f))])
    i = 0

    # Process all files in the source folder
    for file in os.listdir(scraped_data_path):

        print(f"[{i + 1}/{files_nb}] Building training and rag data of {file}...")

        scraped_file_path = os.path.join(scraped_data_path, file)

        # Ensure only files are processed (skip directories)
        if os.path.isfile(scraped_file_path):
            extract_data(scraped_file_path, raw_data_rag_path)

        i += 1