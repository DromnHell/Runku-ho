import requests
from bs4 import BeautifulSoup, NavigableString
from typing import Dict, Optional, List


def is_exclusively_links(ul_element) -> bool:
    """
    Check if the <ul> (or <ol>) is only composed of links.
    Recursively traverses HTML elements in reading order.
    - Ignores the <div id="toc"> to not retrieve the summary.
    - If the element is a <p>, <h2>, <h3>, we take its text.
    - If it is a <ul> or <ol>, we retrieve each <li> in order.
    - If it is a <dl>, we retrieve each <dd> in order.
    - Otherwise, we descend recursively to continue the traversal.

    :ul_element: An <ul>  to explore.
    :return: True is the <ul> is composed only of links, False otherwise
    """

    if ul_element.name not in ["ul", "ol"]:
        return False

    for li in ul_element.find_all("li", recursive=False):
        li_text = li.get_text(strip=True)
        a = li.find("a", recursive=False)
        if not a:
            return False

        a_text = a.get_text(strip=True)
        if a_text != li_text:
            return False

    return True

def extract_ordered_content(element) -> List[str]:
    """
    Recursively traverses HTML elements in reading order.
    - Ignores the <div id="toc"> to not retrieve the summary.
    - If the element is a <p>, <h2>, <h3>, we take its text.
    - If it is a <ul> or <ol>, we retrieve each <li> in order.
    - If it is a <dl>, we retrieve each <dd> in order.
    - Otherwise, we descend recursively to continue the traversal.

    Also, we skip the entire block if we detect a "reference-only" section:
    <h2>Title</h2>
    <ul>
     <li><a> ... </a></li>
     ...
    </ul>

    :element: An object representing an HTML element to explore.
    :return: A list of string of extracted data. Returns an empty list if no matching HTML elements are found.
    """
    lines = []

    children = list(element.children)
    i = 0

    # Sequential exploration of the direct children of the element
    while i < len(children):
        child = children[i]

        # 1) If it's plain text (NavigableString), we ignore it, or we could take it if need be
        if isinstance(child, NavigableString):
            i += 1
            continue

        # 2) If it's an HTML tag :
        if child and hasattr(child, 'name'):

            # a) Ignore the summary.
            if child.name == "div" and child.get("id") == "toc":
                i += 1
                continue

            # b) <h2> / <h3> : check if the <ul> (or <ol>) is only composed of links.
            if child.name in ["h2", "h3"]:
                title_text = child.get_text(separator=' ', strip=True)

                if (i + 1) < len(children):
                    sibling = children[i + 1]
                    if (sibling
                            and hasattr(sibling, 'name')
                            and sibling.name in ["ul", "ol"]
                            and is_exclusively_links(sibling)):
                        i += 2
                        continue
                if title_text:
                    lines.append(title_text)
                i += 1
                continue

            # c) <p>.
            if child.name == "p":
                text = child.get_text(separator=' ', strip=True)
                if text:
                    lines.append(text)
                i += 1
                continue

            # d) Lists <ul> ou <ol>.
            if child.name in ["ul", "ol"]:
                for li in child.find_all("li", recursive=False):
                    li_text = li.get_text(separator=' ', strip=True)
                    if li_text:
                        lines.append(li_text)
                i += 1
                continue

            # e) Lists <dl>.
            if child.name == "dl":
                for dd in child.find_all("dd", recursive=False):
                    dd_text = dd.get_text(separator=' ', strip=True)
                    if dd_text:
                        lines.append(dd_text)
                i += 1
                continue

            # f) Other tags.
            lines.extend(extract_ordered_content(child))
            i += 1
            continue

        i += 1

    return lines


def scrape_page_description(soup: BeautifulSoup) -> str:
    """
    Targets only the 'core' of the Wiki page, i.e. <div id="mw-content-text">,
    and returns its contents (paragraphs, headings, list items)
    in HTML reading order.

    :param soup: A BeautifulSoup object representing the parsed HTML content.
    :return: A string of extracted data. Returns an empty string if no matching table or rows are found.
    """
    core_div = soup.find("div", id="mw-content-text")
    if not core_div:
        return ""

    lines = extract_ordered_content(core_div)

    return "\n".join(lines)

def scrape_ambre_table(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Finds and extracts key-value pairs from the first table that contains the word 'Ambre' in its first row.

    :param soup: A BeautifulSoup object representing the parsed HTML content.
    :return: A dictionary of extracted data (key -> value). Returns an empty dict if no matching table or rows are found.
    """
    tables = soup.find_all('table')
    target_table = None

    for tbl in tables:
        rows = tbl.find_all('tr')
        if not rows:
            continue
        first_row_cells = rows[0].find_all(['th', 'td'])
        found_ambre_in_first_row = any(
            "ambre" in cell.get_text(strip = True).lower()
            for cell in first_row_cells
        )

        if found_ambre_in_first_row:
            target_table = tbl
            break

    if not target_table:
        return {}

    table_data: Dict[str, str] = {}
    for row in target_table.find_all('tr'):
        cells = row.find_all(['th', 'td'])
        if len(cells) == 2:
            key = cells[0].get_text(strip = True)
            value = cells[1].get_text(strip = True)
            if key:
                table_data[key] = value

    return table_data


def scrape_page_content(url: str) -> Optional[Dict[str, object]]:
    """
    Extracts useful content from a given wiki page URL.

    :param url: The URL of the wiki page to scrape.
    :return: A dictionary with 'description' (str) and 'ambre_table' (dict),
             or None if the request failed.
    """
    try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving URL ({url}): {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    description: str = scrape_page_description(soup)
    ambre_table: Dict[str, str] = scrape_ambre_table(soup)

    return {
        'description': description,
        'ambre_table': ambre_table
    }

def save_data_to_file(data: Optional[Dict[str, object]], file_name: str = "text_data.txt") -> None:
    """
    Saves the extracted description, lists and ambre table into a text file.

    :param data: A dictionary containing 'description', 'list' and 'ambre_table', or None.
    :param file_name: The name of the text file to create or overwrite.
    :return: None
    """
    if data is None:
        print("No data to save.")
        return

    description = data.get('description', "")
    ambre_table = data.get('ambre_table', {})

    with open(file_name, "w", encoding="utf-8") as file:

        if isinstance(description, str) and description.strip():
            file.write("Description:\n")
            file.write(description + "\n\n")

        if isinstance(ambre_table, dict) and ambre_table:
            file.write("Tableau:\n")
            for key, value in ambre_table.items():
                file.write(f"{key}: {value}\n")

    print(f"The data was saved in '{file_name}'.")


if __name__ == "__main__":
    url = "https://fr.wiki.ryzom.com/wiki/Zora%C3%AFs"
    data = scrape_page_content(url)
    save_data_to_file(data, "text_data.txt")
