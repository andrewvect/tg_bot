import requests  # type: ignore
from bs4 import BeautifulSoup, Tag


def parse_serbian_words(url: str, output_file: str) -> None:
    """
    Parses Serbian words from a Wiktionary frequency list and saves them to a file.

    Args:
        url (str): The URL of the Wiktionary page.
        output_file (str): The path to the output file.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table", {"class": "wikitable"})
        if not table or not isinstance(table, Tag):
            print("Table not found in the HTML content")
            return

        words_data: list[str] = []
        tbody = table.find("tbody")
        if not tbody or not isinstance(tbody, Tag):
            print("Tbody not found in the table")
            return

        for row in tbody.find_all("tr"):
            if isinstance(row, Tag):
                cells = row.find_all("td")
                if len(cells) >= 1:
                    th_element = row.find("th")
                    if th_element and isinstance(th_element, Tag):
                        word_element = th_element.find("a")
                        if word_element and isinstance(word_element, Tag):
                            title = word_element.get("title")
                            if title and isinstance(title, str):
                                word = title.strip()
                                words_data.append(word)

        with open(output_file, "w", encoding="utf-8") as f:
            for word in words_data:
                f.write(f"{word}\n")

        print(
            f"Successfully parsed {len(words_data)} words and saved them to {output_file}"
        )

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    url = "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Serbian_wordlist"
    output_file = "serbian_words_with_counts.txt"
    parse_serbian_words(url, output_file)
