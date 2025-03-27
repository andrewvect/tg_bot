import asyncio

import yaml
from googletrans import Translator


async def translate_words(yaml_file_path):
    """
    Translates words from a YAML file to a specified target language using Google Translate.

    Args:
        yaml_file_path (str): The path to the YAML file containing the words to translate.
        target_language (str): The target language code (e.g., 'en' for English, 'es' for Spanish).
    """

    try:
        with open(yaml_file_path) as file:
            words = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: File not found at {yaml_file_path}")
        return
    except yaml.YAMLError as e:
        print(f"Error: Could not parse YAML: {e}")
        return

    translator = Translator()
    translated_words = {}

    for entry in words.values():
        latin_word = entry["serbian_word"].get("Latin", "")
        if latin_word:
            try:
                translation = await translator.translate(latin_word, dest="ru")
                if isinstance(translation.text, bytes):
                    entry["translation"] = translation.text.decode("utf-8")
                else:
                    entry["translation"] = translation.text
                print(f"Original: {latin_word}, Translated: {translation.text}")
            except Exception as e:
                print(f"Error translating '{latin_word}': {e}")
                entry["translation"] = None  # or some other placeholder

    with open(yaml_file_path, "w", encoding="utf-8") as file:
        yaml.safe_dump(words, file, allow_unicode=True)

    return translated_words


async def main():
    yaml_file = "words.yaml"  # Replace with your YAML file path
    translated = await translate_words(yaml_file)

    if translated:
        print("\nTranslated Words:")
        for key, value in translated.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
