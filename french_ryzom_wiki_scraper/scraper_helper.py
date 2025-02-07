from files_utiles import *
from scraper_rules import AMBRE_TABLE_KEYS_STYLE

def get_custom_text(element, ambre_table = False)  -> str:
    """
    Extracts text from an element with custom separator logic:
    - Adds separators (e.g., spaces) between elements, except for inline tags like <b>, <i>, etc.
    - Adds a label "[→]" before link text, only if 50% or more of the line/cell is composed of links.
    - Excludes content inside specific tags (e.g., <small>).

    :param element: A BeautifulSoup element to process.
    :param ambre_table: A boolean to change the function behavior on Ambre Table.

    :return: Cleaned and formatted text.
    """
    separator = " "
    inline_tags = {"b", "i", "strong", "em", "u"}
    excluded_tags = {"small"}

    # Skip excluded tags
    if element.name in excluded_tags:
        return ""

    text_parts = []

    element_text = element.get_text(strip=True)
    total_text_len = len(element_text)

    if(total_text_len == 0):
        return ""

    # Collect all links in the current element
    link_texts = []

    if(isinstance(element, NavigableString)):
        text_parts.append(element.strip())

    else:
        for child in element.find_all("a", recursive=True):
            link_text = child.get_text(strip=True)
            if link_text:
                link_texts.append(link_text)

        total_link_text_len = sum(len(link) for link in link_texts)

        # Determine if the line/cell is mostly composed of links (>= 50%)
        add_link_label = (element.name in {"li", "dd", "th", "td"}
                          and total_link_text_len / total_text_len >= 0.5)

        # Process the children of the element
        for child in element.children:

            # Skip excluded tags
            if child.name in excluded_tags:
                continue

            # Skip excluded tags
            if child.name == "br":
                text_parts.append("\n")
                continue

            # Add the text content directly, stripping unnecessary spaces.
            if isinstance(child, NavigableString):
                text_parts.append(child.strip())

            # Inline tags: add their content, ensuring spaces before and after.
            elif child.name in inline_tags:
                inline_text = get_custom_text(child)
                if text_parts and not text_parts[-1].endswith(" "):
                    text_parts.append(" ")
                text_parts.append(inline_text)
                text_parts.append(" ")

            # Non-inline tags should add separators.
            else:
                if text_parts and text_parts[-1] != separator:
                    text_parts.append(separator)

                # If the child is a link (<a>) and the parent line/cell is mostly links, prepend the label
                if child.name == "a" and add_link_label:
                    link_text = get_custom_text(child)
                    if link_text:
                        labeled_link = link_text if ambre_table else  f"[→ {link_text}]"
                        text_parts.append(labeled_link)
                else:
                    text_parts.append(get_custom_text(child))

                text_parts.append(separator)

    # Removing consecutive spaces.
    result = "".join(text_parts).strip(separator)

    result = re.sub(r'[^\S\r\n]+', ' ', result)

    return result


def matches_ambre_style(style: str) -> bool:
    """
    Check if the table style match with "Ambre table" style.

    :param style: The style of the table.
    :return: True is the style match, False otherwise.
    """
    if not style:
        return False
    return all(key in style for key in AMBRE_TABLE_KEYS_STYLE)


def is_ignored_element(element, rules):
    """
    Checks if an element matches any of the ignore rules.

    :param element: A BeautifulSoup element representing the element.
    :param rules: A dictionary containing the rules for ignored classes, ids, and styles.
    :return: True if the element matches an ignore rule, False otherwise.
    """

    element_classes = element.get("class", [])
    if any(cls in rules["classes"] for cls in element_classes):
        return True

    element_id = element.get("id", "")
    if element_id in rules["ids"]:
        return True

    element_summary = element.get("summary", "")
    if element_summary in rules["summaries"]:
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


def is_header_row(row):
    """
    Determine if a row is a header row.
    """
    if row.find("th"):
        return True
    if "font-weight:bold" in row.get("style", "").lower():
        return True
    return False



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