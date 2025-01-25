from scraper_helper import *
from scraper_ignored_rules import IGNORED_DIV_RULES, IGNORED_TABLE_RULES

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
            file.write(clean_text(description) + "\n\n")

        if isinstance(ambre_table, dict) and ambre_table:
            file.write("Tableau résumé:\n")
            for key, value in ambre_table.items():
                file.write(f"{clean_text(key)}: {clean_text(value)}\n")

    print(f"The data was saved in '{file_name}'.")

def scrape_ambre_table(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Finds and extracts key-value pairs from the "Ambre table".

    :param soup: A BeautifulSoup object representing the parsed HTML content.
    :return: A dictionary of extracted data (key -> value). Returns an empty dict if no matching table or rows are found.
    """

    tables = soup.find_all('table', style=lambda s: matches_ambre_style(s))
    if not tables:
        return {}

    target_table = tables[0]

    rows = target_table.find_all('tr')
    if len(rows) < 2:
        return {}

    table_data: Dict[str, str] = {}

    # Start from the second row because we don't want the title of this table.
    for row in rows[1:]:
        cells = row.find_all(['th', 'td'])

        # If exactly 2 cells => key-value
        if len(cells) == 2:
            key = get_custom_text(cells[0])
            value = get_custom_text(cells[1])
            if key:
                table_data[key] = value

        # If exactly 1 cell => key with empty value
        elif len(cells) == 1:
            key = get_custom_text(cells[0])
            if key:
                table_data[key] = ""

    return table_data


def extract_ordered_content(element) -> List[str]:
    """
    Recursively traverses HTML elements in reading order to add relevant text.
    Relevance criteria are in the functions comments.

    :element: An object representing an HTML element to explore.
    :return: list of string of extracted data. Returns an empty list if no matching HTML elements are found.
    """

    lines = list()

    # Ignore specific <div> and <table>.
    if ((element.name == "div" and is_ignored_element(element, IGNORED_DIV_RULES))
            or (element.name == "table" and is_ignored_element(element, IGNORED_TABLE_RULES))):
        return lines

    filtered_children: List[str] = [
        child for child in element.children
        if not (isinstance(child, NavigableString) and not child.strip())]

    i = 0

    # Sequential exploration of the children of the element.
    while i < len(filtered_children):
        child = filtered_children[i]

        # 1) If it's plain text (NavigableString), we ignore it.
        if isinstance(child, NavigableString):
            i += 1
            continue

        # 2) If it's an HTML tag :
        if child and hasattr(child, 'name'):

            # a) Dot not add text of <div> and <table> to ignore
            if ((child.name == "div" and is_ignored_element(child, IGNORED_DIV_RULES))
                    or (child.name == "table" and is_ignored_element(child, IGNORED_TABLE_RULES))):
                i += 1
                continue

            # b) Add the text of a <div> only if the <div> doesn't contain another <div>.
            # This is to manage the rare cases where relevant text is located in raw <div> without <p> tag for example.
            if child.name == "div":
                if not child.find("div", recursive=True):
                    text = get_custom_text(child)
                    if text:
                        lines.append(text)
                    i += 1
                    continue

            # c) Add the text contains in basic informative <table> ("text-align:center;" style).
            if child.name == "table" and child.has_attr('style') and "text-align:center;" in child["style"]:
                for row in child.find_all("tr", recursive=False):
                    cells = row.find_all(["th", "td"], recursive=False)
                    cell_texts = []
                    for cell in cells:
                        txt = get_custom_text(cell)
                        if txt:
                            cell_texts.append(txt)
                    if cell_texts:
                        line = " : ".join(cell_texts)
                        lines.append(line)
                i += 1
                continue

            # d) Add the text contains in <span>.
            if (child.name == "span" and child.has_attr('style')
                    and "white-space: nowrap;" not in child["style"]):
                text = get_custom_text(child)
                if text:
                    lines.append(text)
                i += 1
                continue

            # e) Add the text contains in <p>.
            if child.name == "p":
                text = get_custom_text(child)
                if text:
                    lines.append(text)
                i += 1
                continue

            # f) Add the text contains in <h2> / <h3>.
            if child.name in ["h2", "h3"]:
                title_text = get_custom_text(child)

                # Check if the header is followed by too much links. Skip if true.
                if (i + 1) < len(filtered_children):
                    sibling = filtered_children[i + 1]
                    if (sibling
                            and hasattr(sibling, 'name')
                            and sibling.name in ["ul", "ol"]
                            and element_contains_too_many_links(sibling)):
                        i += 2
                        continue
                if title_text:
                    lines.append(title_text)
                i += 1
                continue

            # g) Add the text contains in <ul> / <ol> lists.
            if child.name in ["ul", "ol"]:
                for li in child.find_all("li", recursive=False):
                    # Ignore footnote
                    li_id = li.get("id", "")
                    if li_id.startswith("cite_note-"):
                        continue
                    li_text = get_custom_text(li)
                    if li_text:
                        lines.append(li_text)
                i += 1
                continue

            # h) Add the text contains in <dl> lists.
            if child.name == "dl":
                for dd in child.find_all("dd", recursive=False):
                    dd_text = get_custom_text(dd)
                    if dd_text:
                        lines.append(dd_text)
                i += 1
                continue

            child_lines = extract_ordered_content(child)
            lines.extend(child_lines)

        i += 1

    return lines


def scrape_page_description(soup: BeautifulSoup) -> str:
    """
    Targets only the 'core' of the Wiki page, i.e. <div id="mw-content-text">,
    and returns its contents (paragraphs, headings, list items) in HTML reading order.

    :param soup: A BeautifulSoup object representing the parsed HTML content.
    :return: A string of extracted data. Returns an empty string if no matching table or rows are found.
    """
    core_div = soup.find("div", id="mw-content-text")
    if not core_div:
        return ""

    lines = extract_ordered_content(core_div)

    return "\n".join(lines)


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


if __name__ == "__main__":
    url = "https://fr.wiki.ryzom.com/wiki/Zachini"
    data = scrape_page_content(url)
    save_data_to_file(data, "text_data.txt")
