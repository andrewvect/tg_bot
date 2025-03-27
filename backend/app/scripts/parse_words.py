import requests
from bs4 import BeautifulSoup


def parse_serbian_words(url, output_file):
    """
    Parses Serbian words from a Wiktionary frequency list and saves them to a file.

    Args:
        url (str): The URL of the Wiktionary page.
        output_file (str): The path to the output file.`
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table", {"class": "wikitable"})

        words_data = []
        tbody = table.find("tbody")
        for row in tbody.find_all("tr"):
            if len(row.find_all("td")) >= 1:
                word_element = row.find("th").find("a")
                if word_element:
                    word = word_element.get("title").strip()
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
