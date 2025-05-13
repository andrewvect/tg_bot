import yaml


def create_yaml_from_words(input_file: str, output_file: str) -> None:
    words = {}
    with open(input_file, encoding="utf-8") as f:
        for i, line in enumerate(f):
            # Take the first word from each line
            word_latin = line.strip().split(" ")[0]
            words[i + 1] = {
                "serbian_word": {"Latin": word_latin, "Cyrillic": ""},
                "translation": "",
                "bio": "",
            }

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(words, f, allow_unicode=True)


if __name__ == "__main__":
    input_file = "serbian_words_with_counts.txt"
    output_file = "words.yaml"
    create_yaml_from_words(input_file, output_file)
    print(f"Successfully created {output_file} from {input_file}")
