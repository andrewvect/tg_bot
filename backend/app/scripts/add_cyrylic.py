import os
import re
from pathlib import Path

import yaml

# Path to the words.yaml file
SCRIPT_DIR = Path(__file__).resolve().parent
WORDS_YAML_PATH = os.path.join(SCRIPT_DIR, "words.yaml")


def extract_word_from_sentences(sentences: list[dict[str, str]]) -> str | None:
    """Extract words between ** symbols from Cyrillic sentences."""
    for sentence in sentences:
        if "Cyrillic" in sentence:
            cyrillic_text = sentence["Cyrillic"]
            # Find text between ** symbols
            match = re.search(r"\*\*(.*?)\*\*", cyrillic_text)
            if match:
                return match.group(1)
    return None


def fill_empty_cyrillic_fields() -> None:
    # Load the YAML file
    with open(WORDS_YAML_PATH, encoding="utf-8") as file:
        words_data = yaml.safe_load(file)

    changes_count = 0

    # Process each word entry
    for word_id, word_data in words_data.items():
        # Check if the word has serbian_word field with empty Cyrillic
        if (
            "serbian_word" in word_data
            and isinstance(word_data["serbian_word"], dict)
            and "Cyrillic" in word_data["serbian_word"]
            and not word_data["serbian_word"]["Cyrillic"]
        ):
            # Check if sentences are available
            if "sentences" in word_data and word_data["sentences"]:
                # Extract the Cyrillic word from sentences
                cyrillic_word = extract_word_from_sentences(word_data["sentences"])

                if cyrillic_word:
                    # Update the Cyrillic field
                    word_data["serbian_word"]["Cyrillic"] = cyrillic_word
                    changes_count += 1
                    print(f"Updated word {word_id}: {cyrillic_word}")

    # Save the updated YAML file
    with open(WORDS_YAML_PATH, "w", encoding="utf-8") as file:
        yaml.dump(words_data, file, allow_unicode=True, sort_keys=False)

    print(f"Completed. Updated {changes_count} words with missing Cyrillic.")


if __name__ == "__main__":
    fill_empty_cyrillic_fields()
