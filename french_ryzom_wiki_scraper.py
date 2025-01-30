from operator import truediv
import argparse
from scraper_helper import *
from files_utiles import *
from scraper_rules import *


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

        if(get_custom_text(cells[0], True).startswith("S'il vous plaît, préférez plutôt le modèle")):
            continue

        # If exactly 2 cells => key-value
        if len(cells) == 2:
            key = get_custom_text(cells[0], True)
            value = get_custom_text(cells[1], True)
            if key:
                table_data[key] = value

        # If exactly 1 cell => key with empty value
        elif len(cells) == 1:
            key = get_custom_text(cells[0], True)
            if key:
                table_data[key] = ""

    return table_data


def process_images(child, lines) -> bool:
    """
    Add a tag [IMG] instead of an image.

    :param child: The HTML element to process.
    :param lines: The str element to write.

    :return: True if the function is process. False otherwise.
    """
    text = "[IMG]"
    if(child.get("alt", "") == "Rubber-Stamp-Lore-Amber.png"):
        return True
    if text:
        lines.append(text)
    return True

def process_description_list(child, lines) -> bool:
    """
    Add the text / table contained in <dl> lists.

    :param child: The HTML element to process.
    :param lines: The str element to write.

    :return: True if the function is process. False otherwise.
    """
    # Check if the <dl> contains a table
    table = child.find("table", recursive=True)
    if table:
        process_table(table, lines)
        return True

    # Process <dt> elements
    for dt in child.find_all("dt", recursive=False):
        dt_text = get_custom_text(dt)
        if dt_text:
            lines.append(f"- {dt_text})")

    # Process the <dd> child within the <dl>
    for dd in child.find_all("dd", recursive=False):
        dd_text = get_custom_text(dd)
        if dd_text:
            lines.append(f"- {dd_text}")

    return True

def process_list(child, lines) -> bool:
    """
    Add the text contained in <ul> or <ol> lists.

    :param child: The HTML element to process.
    :param lines: The str element to write.

    :return: True.
    """
    for li in child.find_all("li", recursive=False):
        li_id = li.get("id", "")
        # Ignore footnotes
        if li_id.startswith("cite_note-"):
            continue
        li_text = get_custom_text(li)
        if li_text:
            lines.append(f"- {li_text}")
    return True

def process_headers(child, lines, children, current_index):
    """
    Processes header elements (<h1>, <h2>, <h3>, etc.).
    Skips headers that are immediately followed by another header of the same level or higher without meaningful content.
    Skips headers that are immediately followed by a "genealogy table".

    :param child: The current header element being processed.
    :param lines: The list to store processed text.
    :param children: The list of all children elements.
    :param current_index: The index of the current header in the children list.

    :return: True.
    """
    header_level = int(child.name[1])
    header_text = get_custom_text(child)

    # Look ahead to check if there's meaningful content before the next header
    for next_child in children[current_index + 1:]:

        next_line_is_header = False

        # Skip whitespace or empty strings
        if (isinstance(next_child, NavigableString)
                or (isinstance(next_child, NavigableString) and not next_child.strip())):
            continue

        # If the next element is another header of the same level or higher, skip this header
        if hasattr(next_child, 'name') and next_child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            next_level = int(next_child.name[1])
            if next_level <= header_level:
                return True
            else:
                next_line_is_header = True

        # Check if the next element is a table with a specific summary
        if next_child.name == "table" and next_child.has_attr("summary"):
            table_summary = next_child.get("summary", "")
            if table_summary in GENEALOGY_SUMMARIES:
                return

        # If meaningful content is found, add the header and return
        if get_custom_text(next_child).strip():
            if(header_level == 2 and not next_line_is_header):
                lines.append(f"\n{header_text}\n")
            else:
                lines.append(f"\n{header_text}")
            return True

def process_paragraph(child, lines) -> bool:
    """
    Add the text contained in a <p>.

    :param child: The HTML element to process.
    :param lines: The str element to write.

    :return: True.
    """
    text = get_custom_text(child)
    if text:
        lines.append(text)
    return True

def process_span(child, lines) -> bool:
    """
    Add the text contained in a <span>, ignoring certain styles.

    :param child: The HTML element to process.
    :param lines: The str element to write.

    :return: True if the function is process. False otherwise.
    """
    if child.has_attr("style") and "white-space: nowrap;" not in child["style"]:
        text = get_custom_text(child)
        if text:
            lines.append(text)
        return True
    return False

def process_table(child, lines) -> bool:
    """
    Process an HTML <table> using Pandas to parse and display it as a DataFrame.

    :param child: The HTML element (table) to process.
    :param lines: The list to store processed data.

    :return: True if the table was processed successfully, False otherwise.
    """

    if not any(td.get_text(strip=True) for td in child.find_all("td")):
        return True

    # Convert the table element to a string and wrap it in StringIO
    table_html = StringIO(str(child))

    # Use pandas to parse the table into a DataFrame
    df = pd.read_html(table_html)[0]

    # Clean column names for better readability
    df.columns = [str(col).strip().replace('\n', ' ') for col in df.columns]

    # Optimize the table display for LLM readability
    table_as_string = df.to_string(
        #max_colwidth=30,    # Limit the width of each column
        line_width=80,      # Set the total width of the table
        index=False,        # Hide the index if not necessary
        justify="left"     # Align columns to the left for consistency
    )

    # Add processed table to the lines
    lines.append(f"\n{table_as_string}\n")

    return True

def process_div_without_nested_div(child, lines) -> bool:
    """
    Add the text of a <div> only if the <div> doesn't contain another <div>.
    This is to manage the rare cases where relevant text is located in raw <div> without <p> tag for example.

    :param child: The HTML element to process.
    :param lines: The str element to write.

    :return: True if the function is process. False otherwise.
    """
    if not child.find("div", recursive=True):
        text = get_custom_text(child)
        if text:
            lines.append(text)
            return True
    return False

def extract_ordered_content(element):
    """
    Extracts content from an element and its children in a structured way.

    :param element: The BeautifulSoup element to process.
    :return: A list of extracted text lines.
    """
    lines = []

    # Delete HTML comment.
    for comment in element.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Ignore specific element.
    if((element.name == "div" and is_ignored_element(element, IGNORED_DIV_RULES))
            or (element.name == "table" and is_ignored_element(element, IGNORED_TABLE_RULES))
            or (element.name == "ul" and is_ignored_element(element, IGNORED_LIST_RULES))):
        return lines

    filtered_children = [
        child for child in element.children
        if not (isinstance(child, NavigableString) and not child.strip())
    ]

    i = 0

    # Sequentially process the children of the element.
    while i < len(filtered_children):
        child = filtered_children[i]

        # 1) If the child is plain text (NavigableString), skip it.
        if isinstance(child, NavigableString):
            i += 1
            continue

        # 2) If the child is an HTML tag:
        if child and hasattr(child, "name"):

            # a) Dot not add text of elements to ignore.
            if ((child.name == "div" and is_ignored_element(child, IGNORED_DIV_RULES))
                    or (child.name == "table" and is_ignored_element(child, IGNORED_TABLE_RULES))
                    or (child.name == "ul" and is_ignored_element(child, IGNORED_LIST_RULES))):
                i += 1
                continue

            # b) Process <div> elements.
            if child.name == "div":
                if process_div_without_nested_div(child, lines):
                    i += 1
                    continue

            # c) Process <table> elements.
            if child.name == "table":
                if process_table(child, lines):
                    i += 1
                    continue

            # d) Process <span> elements.
            if child.name == "span":
                if process_span(child, lines):
                    i += 1
                    continue

            # e) Process <p> elements.
            if child.name == "p":
                if process_paragraph(child, lines):
                    i += 1
                    continue

            # f) Process headers elements (<hx>).
            if child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                if process_headers(child, lines, filtered_children, i):
                    i += 1
                    continue

            # g) Process <ul> and <ol> lists.
            if child.name in ["ul", "ol"]:
                if process_list(child, lines):
                    i += 1
                    continue

            # h) Process <dl> lists.
            if child.name == "dl":
                if process_description_list(child, lines):
                    i += 1
                    continue

            # h) Process <img>.
            if child.name == "img":
                if process_images(child, lines):
                    i += 1
                    continue

            # j) If the child is not specifically handled, recursively explore its content.
            child_lines = extract_ordered_content(child)
            lines.extend(child_lines)

        i += 1

    return lines

def scrape_text_main_content(soup: BeautifulSoup) -> str:
    """
    Targets only the 'core' of the Wiki page, i.e. <div id="mw-content-text">,
    and returns its textual content contents (paragraphs, headings, list items, etc.) in HTML reading order.

    :param soup: A BeautifulSoup object representing the parsed HTML content.
    :return: A string of extracted data. Returns an empty string if no matching table or rows are found.
    """
    core_div = soup.find("div", id="mw-content-text")
    if not core_div:
        return ""

    lines = extract_ordered_content(core_div)

    return "\n".join(lines)


def scrape_useful_page_content(url: str) -> Optional[Dict[str, object]]:
    """
    Extracts useful content from a given wiki page URL.

    :param url: The URL of the wiki page to scrape.
    :return: A dictionary with 'text_main_content' (str) and 'ambre_table' (dict),
             or None if the request failed.
    """
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    page_title = soup.title.string
    clean_title = page_title.split("—")[0].strip()

    text_main_content: str = scrape_text_main_content(soup)
    ambre_table: Dict[str, str] = scrape_ambre_table(soup)

    return {
        'title': clean_title,
        'text_main_content': text_main_content,
        'ambre_table': ambre_table
    }

if __name__ == "__main__":
    '''   base_url = "https://fr.wiki.ryzom.com/wiki/Wuaoi_Yai-Zhio/%C3%80_propos_d%27Oflovak_Rydon"

    if is_ignored_url(base_url, URL_TO_NOT_SCRAP):
        print(f"URL ignored : {base_url}")
    else:
        folder_name = "french_ryzom_wiki_pages"
        data = scrape_useful_page_content(base_url)
        save_data_to_file(data, folder_name,"test.txt")
        '''

    base_url = "https://fr.wiki.ryzom.com"
    all_pages_url = f"{base_url}/wiki/Sp%C3%A9cial:Toutes_les_pages"
    folder_name = "french_ryzom_wiki_pages"
    error_log_file = "errors.log"

    print("Retrieve links..")
    all_links = get_all_links_from_pagination(base_url, all_pages_url)
    print(f"{len(all_links)} pages found.")

    '''for idx, url in enumerate(all_links):
        if idx > 3:
            break
        print(f"[{idx + 1}/{len(all_links)}] Extraction of {url}...")
        try:
            title = url.split("/wiki/")[-1]
            file_name = sanitize_filename(title) + ".txt"
            content = scrape_useful_page_content(url)
            save_data_to_file(content, folder_name, file_name)
            time.sleep(1)
        except Exception as e:
            error_message = f"Error on {url}: {e}"
            print(error_message)
            log_error(error_message, error_log_file)'''