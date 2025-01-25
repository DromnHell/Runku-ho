import requests
import re
import regex
from bs4 import BeautifulSoup, NavigableString
from typing import Dict, Optional, List

AMBRE_TABLE_KEYS_STYLE = [
    "float: right",
    "width:25%",
    "max-width:30%",
    "margin: 0.1em",
    "overflow: auto",
    "border: thick outset #C90",
    "border-radius:1em",
    "padding: 0.1em"
]


def matches_ambre_style(style: str) -> bool:
    """
    Check if the table style match with "Ambre table" style.

    :param style: The style of the table.
    :return: True is the style match, False otherwise.
    """
    if not style:
        return False
    return all(key in style for key in AMBRE_TABLE_KEYS_STYLE)


def clean_text(description: str) -> str:
    """
    Cleans up the `description` string by removing :
    - [x] characters (e.g. [1], [2]...).
    - Consecutive special characters (non-alphanumeric).
    - Consecutive spaces.
    - Extra symbols.

    :param description: The text to be cleaned up.
    :return: The cleaned string.
    """
    text = re.sub(r'\[\d+]', '', description)

    text = re.sub(r'([^\w\s])\1+', r'\1', text)

    text = re.sub(r'\s{2,}', ' ', text)

    text = regex.sub(r'[\p{So}ᐉ]', '', text)

    text = text.strip()

    return text


def get_custom_text(element, separator=" ", inline_tags={"b", "i", "strong", "em", "u"}) -> str:
    """
    Extracts text from an element with custom separator logic:
    - Adds separators (e.g., spaces) between elements, except for inline tags like <b>, <i>, etc.
    - Separates links and other inline content correctly.

    :param element: A BeautifulSoup element to process.
    :param separator: The default separator to use between non-inline elements.
    :param inline_tags: A set of tags considered as inline formatting tags (no separator applied).
    :return: Cleaned and formatted text.
    """
    text_parts = []

    for child in element.children:
        # Add the text content directly, stripping unnecessary spaces.
        if isinstance(child, NavigableString):
            text_parts.append(child.strip())
        # Inline tags: add their content, ensuring spaces around if needed
        elif child.name in inline_tags:
            inline_text = get_custom_text(child, separator, inline_tags)
            if text_parts and not text_parts[-1].endswith(" "):
                text_parts.append(" ")
            text_parts.append(inline_text)
            text_parts.append(" ")
        # Non-inline tags should add separators.
        else:
            if text_parts and text_parts[-1] != separator:
                text_parts.append(separator)
            text_parts.append(get_custom_text(child, separator, inline_tags))
            text_parts.append(separator)

    result = "".join(text_parts).strip(separator)

    # Handle cases where links are followed by punctuation (remove spaces before punctuation)
    result = re.sub(r'\s([.,!?;:])', r'\1', result)

    return result


def filter_newlines_and_whitespace_children(element):
    """
    Filters out children of an HTML element that are either newlines or whitespace.

    :param element: A BeautifulSoup element whose children will be filtered.
    :return: A list of children with non-whitespace content.
    """
    return [
        child for child in element.children
        if not (isinstance(child, NavigableString) and not child.strip())
    ]


def element_contains_too_many_links(element, ratio_threshold: float = 0.5) -> bool:
    """
    Check if an HTML element (list or table) is predominantly composed of links.

    :param element: A BeautifulSoup element (<ul>, <ol>, <dl>, or <table>) to analyze.
    :param ratio_threshold: A float (0 < ratio_threshold <= 1) indicating the minimum percentage of text within <a>.
    :return: True if the element is composed mainly of links, False otherwise.
    """
    if element.name not in ["ul", "ol", "dl", "table"]:
        return False

    elements_to_check = []

    # For <ul> and <ol>, check each <li>.
    if element.name in ["ul", "ol"]:
        elements_to_check = element.find_all("li", recursive=False)

    # For <dl>, check each <dt> and <dd>.
    elif element.name == "dl":
        elements_to_check = element.find_all(["dt", "dd"], recursive=False)

    # For <table>, check each <th> and <td>.
    elif element.name == "table":
        rows = element.find_all("tr", recursive=False)
        for row in rows:
            cells = row.find_all(["th", "td"], recursive=False)
            elements_to_check.extend(cells)

    if not elements_to_check:
        return False

    # Calculate the total text and link lengths across all elements

    total_text_length = 0
    total_link_length = 0

    for sub_element in elements_to_check:
        full_text = get_custom_text(sub_element)
        if not full_text:
            continue

        total_text_length += len(full_text)

        anchors = sub_element.find_all("a")
        for a_tag in anchors:
            a_txt = get_custom_text(a_tag)
            if a_txt:
                total_link_length += len(a_txt)

    if total_text_length == 0:
        return False

    overall_ratio = total_link_length / total_text_length

    return overall_ratio >= ratio_threshold

def is_ignored_element(element, rules):
    """
    Checks if an element matches any of the ignore rules.

    :param element: A BeautifulSoup element representing the element.
    :param rules: A dictionary containing the rules for ignored classes, ids, and styles.
    :return: True if the element matches an ignore rule, False otherwise.
    """

    if element_contains_too_many_links(element):
        return True

    element_classes = element.get("class", [])
    if any(cls in rules["classes"] for cls in element_classes):
        return True

    element_id = element.get("id", "")
    if element_id in rules["ids"]:
        return True

    element_style = element.get("style", "")

    if not element_style:
        return False

    # Check for exact match with styles in rules.
    if element_style in rules["styles"]:
        return True

    # Check for partial match (all key styles from lists must be present).
    for style_list in rules["styles"]:
        if isinstance(style_list, list):
            if all(key_style in element_style for key_style in style_list):
                return True

    return False