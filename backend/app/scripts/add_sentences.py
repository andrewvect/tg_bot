import copy
import os
from typing import Any

import yaml
from openai import OpenAI


def add_empty_sentences() -> str:
    file_name = "words.yaml"
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    if not os.path.exists(file_path):
        open(file_path, "w").close()

    sentences_template = [
        {"Cyrillic": "", "Latin": "", "Russian": ""},
        {"Cyrillic": "", "Latin": "", "Russian": ""},
        {"Cyrillic": "", "Latin": "", "Russian": ""},
    ]

    with open(file_path, encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
        except Exception:
            data = {}

    changed = False
    for value in data.values():
        if "sentences" not in value:
            value["sentences"] = copy.deepcopy(sentences_template)
            changed = True

    if changed:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data, f, allow_unicode=True, sort_keys=False, default_flow_style=False
            )

    return file_path


def find_words_with_empty_sentences(data: dict[str, dict[str, Any]]) -> list[str]:
    """Return keys of words with empty sentences."""
    keys = []
    for key, value in data.items():
        if "sentences" in value:
            if all(
                not s["Cyrillic"] and not s["Latin"] and not s["Russian"]
                for s in value["sentences"]
            ):
                keys.append(key)
    return keys


def build_prompt_for_words(data: dict[str, dict[str, Any]], keys: list[str]) -> str:
    """Builds a prompt for a batch of words."""
    prompt_header = """"это сербские слова по распространенности,
    проверь правильность перевода если неправильный исправь,
    заполни пробелы укажи в bio тип слова падеж или сколнение или время ,
    ответь в формате yml,
    не добавляй в yml комментарии где исправил,
    так же создай для слова три предложения с ним экранируй слово **слово** в предложениях,
Вот пример как это будет выглядеть:
------
1299:
  bio: 'глагол, повелительное наклонение, 2-е лицо единственного числа'
  serbian_word:
    Cyrillic: 'моли'
    Latin: 'moli'
  translation: 'моли'
  sentences:
    - Cyrillic: '**Моли**, дођи на время.'
      Latin: '**Moli**, dođi na vreme.'
      Russian: '**Пожалуйста**, приходи вовремя.'
    - Cyrillic: '**Моли**, помози ми са овим задатком.'
      Latin: '**Moli**, pomozi mi sa овим задатком.'
      Russian: '**Пожалуйста**, помоги мне с этим заданием.'
    - Cyrillic: '**Моли**, немој заборавити кључ.'
      Latin: '**Moli**, nemoj zaboraviti ključ.'
      Russian: '**Пожалуйста**, не забудь ключ.'
------
Сделай для слова ниже:
"""
    prompt_body = ""
    for key in keys:
        entry = data[key]
        prompt_body += f"{key}:\n"
        prompt_body += f"  bio: {entry.get('bio', '')}\n"
        prompt_body += "  serbian_word:\n"
        prompt_body += f"    Cyrillic: {entry['serbian_word'].get('Cyrillic', '')}\n"
        prompt_body += f"    Latin: {entry['serbian_word'].get('Latin', '')}\n"
        prompt_body += f"  translation: {entry.get('translation', '')}\n"
        prompt_body += "  sentences:\n"
        for s in entry.get("sentences", []):
            prompt_body += f"    - Cyrillic: '{s.get('Cyrillic', '')}'\n"
            prompt_body += f"      Latin: '{s.get('Latin', '')}'\n"
            prompt_body += f"      Russian: '{s.get('Russian', '')}'\n"
    return prompt_header + prompt_body


def update_data_with_response(
    data: dict[str, dict[str, Any]], response_yaml: str
) -> None:
    """Update the main data dict with sentences from the response."""
    try:
        # Remove code block formatting if present
        if response_yaml.strip().startswith("```"):
            lines = response_yaml.strip().splitlines()
            # Remove the first line (``` or ```yaml)
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remove the last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_yaml = "\n".join(lines)
        response_data = yaml.safe_load(response_yaml)
        for key, value in response_data.items():
            if key in data:
                data[key]["sentences"] = value.get(
                    "sentences", data[key].get("sentences", [])
                )
                # Optionally update bio/translation if changed
                data[key]["bio"] = value.get("bio", data[key].get("bio", ""))
                data[key]["translation"] = value.get(
                    "translation", data[key].get("translation", "")
                )
    except Exception as e:
        print(f"Failed to parse response: {e}")


def save_to_file(data: dict[str, dict[str, Any]]) -> None:
    file_name = "words.yaml"
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    if not os.path.exists(file_path):
        open(file_path, "w").close()

    with open(file_path, encoding="utf-8") as f:
        try:
            existing_data = yaml.safe_load(f) or {}
        except Exception:
            existing_data = {}

    existing_data.update(data)

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(
            existing_data,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )


def load_from_file(file_path: str) -> dict[str, Any]:
    with open(file_path, encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
        except Exception:
            data = {}
    return data


def main() -> None:
    file_name = "words.yaml"
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    if not os.path.exists(file_path):
        print("words.yaml not found.")
        return

    with open(file_path, encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
        except Exception:
            print("Failed to load YAML.")
            return

    keys_to_process = find_words_with_empty_sentences(data)
    if not keys_to_process:
        print("No words with empty sentences found.")
        return

    XAI_API_KEY = os.getenv("XAI_API_KEY")
    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )

    # Process in batches of 3
    for i in range(0, len(keys_to_process), 3):
        batch_keys = keys_to_process[i : i + 3]
        prompt = build_prompt_for_words(data, batch_keys)
        completion = client.chat.completions.create(
            model="grok-3-beta",
            messages=[
                {"role": "system", "content": prompt},
            ],
        )
        response_content = completion.choices[0].message.content
        if response_content is not None:
            update_data_with_response(data, response_content)
            # Save after each batch
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    data,
                    f,
                    allow_unicode=True,
                    sort_keys=False,
                    default_flow_style=False,
                )
            print(f"Processed keys: {batch_keys}")


if __name__ == "__main__":
    main()
