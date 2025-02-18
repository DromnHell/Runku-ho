import requests
import re
import regex
from bs4 import BeautifulSoup, NavigableString, Comment
from typing import Dict, Optional, List
import time
import os
import copy
import pandas as pd
from io import StringIO
import urllib.parse
from typing import Optional, Dict
from scraper_helper import *
from scraper_rules import URL_TO_NOT_SCRAP, EXTRA_URL_TO_SCRAP

def convert_markdown_title(line: str) -> str:
    """
    Replaces a Markdown title of type #, ##, ###... with "Titre", "Sous-titre", "Sous-sous-titre", etc.
    If the line doesn't begin with '#', we return it as is.

    :param line: A line of text.

    :return: The cleaned text.
    """
    stripped_line = line.lstrip()

    count_hash = 0
    while count_hash < len(stripped_line) and stripped_line[count_hash] == '#':
        count_hash += 1

    if count_hash == 0:
        return line

    remainder = stripped_line[count_hash:].lstrip()

    if count_hash == 1:
        label = "Titre : "
    else:
        label = "Sous-" * (count_hash - 1) + "titre : "

    return label + remainder

def finalize_markdown_titles (text: str) -> str:
    """
    1. Deletes the last line if it is a title (beginning with '#') after removing the empty lines at the end.
    2. For all other lines, replace Markdown titles with more explicit wording.

    :param text: The text to process.

    :return: The cleaned text.
    """
    lines = text.split("\n")

    while lines and not lines[-1].strip():
        lines.pop()

    if lines and lines[-1].strip().startswith("#"):
        lines.pop()

    converted_lines = [convert_markdown_title(line) for line in lines]

    return "\n".join(converted_lines)

def replace_urls_with_placeholder(text: str, placeholder: str = "[URL IGNORÉE]") -> str:
    """
    Replaces all URLs in the text with a placeholder.

    :param text: The original text.
    :param placeholder: The placeholder to replace URLs with.
    :return: The text with URLs replaced by the placeholder.
    """
    url_pattern = r"https?://[^\s]+"
    return re.sub(url_pattern, placeholder, text)

def clean_text_before_extraction(description: str) -> str:
    """
    Cleans up the `description`.

    :param description: The text to be cleaned up.
    :return: The cleaned string.
    """

    # Replace URLs with a placeholder
    description = replace_urls_with_placeholder(description)

    # Removing [x] characters (e.g. [1], [2]...).
    text = re.sub(r'\[\d+]', '', description)

    # Removing consecutive special characters (non-alphanumeric) except the point and the #.
    text = re.sub(r'([^\w\s.#])\1+', r'\1', text)

    # Adding spaces before certain punctuations (French style).
    text = re.sub(r'([!?;:])', r' \1', text)

    # Removing spaces before certain punctuations (French style).
    text = re.sub(r'\s+([.,…»)])', r'\1', text)

    # Removing spaces after apostrophe.
    text = re.sub(r"'\s+", "'", text)

    # Removing extra symbols.
    text = regex.sub(r'[\p{So}ᐉ⓵⓶⓷←ᐖᐄᐛ]', '', text)

    # Replacing excessive newlines, keeping at most two consecutive ones
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Removing the pattern "-–—o§O§o—–-"
    text = re.sub(r'-–—o§O§o—–-', '', text)

    # Removing the pattern "一 ⧼⧽ 一"
    text = re.sub(r'一 ⧼⧽ 一', '', text)

    text = text.strip()

    cleaned_text = finalize_markdown_titles(text)

    return cleaned_text

def save_data_to_file(data: Optional[Dict[str, object]], folder_name, file_name):
    """
    Saves data to a text file in a specific folder.

    :param data: The data to be saved.
    :param folder_name: The folder in which to save the files.
    :param file_name: The file name.

    :return: None
    """
    if data is None:
        return

    title = data.get('title', "")
    text_main_content = data.get('text_main_content', "")
    ambre_table = data.get('ambre_table', {})

    if not text_main_content.strip() and not ambre_table:
        return

    os.makedirs(folder_name, exist_ok = True)

    file_path = os.path.join(folder_name, file_name)

    with open(file_path, "w", encoding = "utf-8") as file:

        if isinstance(text_main_content, str) and text_main_content.strip():
            cleaned_text = clean_text_before_extraction(text_main_content)
            file.write(cleaned_text)

        if isinstance(ambre_table, dict) and ambre_table:
            file.write("\n\n[Tableau résumé]\n")
            for key, value in ambre_table.items():
                if(value == ""):
                    file.write(f"{clean_text_before_extraction(key)}\n")
                else:
                    file.write(f"{clean_text_before_extraction(key)}: {clean_text_before_extraction(value)}\n")


def get_all_links_from_pagination(base_url, all_pages_url):
    """
    Crawl all pages from the start URL and follow the pagination to retrieve all links.

    :param all_pages_url: The URL of the page that references all the wiki pages.
    :param base_url: The base URL of the wiki site.

    :return: A list of all wiki page links.
    """
    all_links = set()
    current_url = all_pages_url

    # Loop on all "All Pages" pages of the wiki.
    i = 1
    while current_url:

        print(f"Processing links from 'All pages' {i}: {current_url}")
        response = requests.get(current_url)
        if response.status_code != 200:
            print(f"Failed to fetch: {current_url}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract links from the "All Pages" page.
        for link in soup.select("div.mw-allpages-body a"):
            href = link.get("href")
            if href and href.startswith("/wiki/"):
                if ("mw-redirect" in link.get("class", [])
                        or is_ignored_url(base_url + href, URL_TO_NOT_SCRAP)):
                    continue
                all_links.add(base_url + href)

        # Find the "next page" link of the "All Pages" page.
        next_page = soup.find("a", string=lambda t: t and t.startswith("Page suivante"))
        if next_page:
            next_url = next_page.get("href")
            current_url = base_url + next_url
            time.sleep(0.1)
        else:
            current_url = None

        i += 1

    # Extract links from pages that are not referenced in the “All pages” pages. EXTRA_URL_TO_SCRAP
    print(f"Processing extra wiki pages link.")
    for extra_wiki_link in EXTRA_URL_TO_SCRAP:
        all_links.add(extra_wiki_link)

    return list(all_links)


def sanitize_filename(filename):
    """
    Clean the files names to remove not-valid character.
    :param filename: The raw title.
    :return: A valid file name.
    """
    invalid_chars = '<>:"/\\|?*'
    decoded_filename = urllib.parse.unquote(filename)
    for char in invalid_chars:
        decoded_filename = decoded_filename.replace(char, "_")
    return decoded_filename


def log_error(message, error_log_file="errors.log"):
    """
    Sage error messages.
    """
    with open(error_log_file, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")


def is_ignored_url(url, ignored_urls):
    """
    Check if a URL is in  the list of URL to ignore, or start with one of these URL.
    """
    return any(url.startswith(ignored) for ignored in ignored_urls)