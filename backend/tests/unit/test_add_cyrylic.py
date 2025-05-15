from pytest_mock import MockerFixture

from app.scripts.add_cyrylic import (
    extract_word_from_sentences,
    fill_empty_cyrillic_fields,
)


def test_extract_word_from_sentences_with_match():
    """Test extracting Cyrillic word from sentences with a match."""
    sentences = [
        {"English": "This is a test sentence."},
        {"Cyrillic": "Ово је **тест** реченица."},
    ]
    result = extract_word_from_sentences(sentences)
    assert result == "тест"


def test_extract_word_from_sentences_with_no_match():
    """Test extracting Cyrillic word from sentences with no match."""
    sentences = [
        {"English": "This is a test sentence."},
        {"Cyrillic": "Ово је тест реченица."},  # No ** symbols
    ]
    result = extract_word_from_sentences(sentences)
    assert result is None


def test_extract_word_from_sentences_with_no_cyrillic():
    """Test extracting Cyrillic word from sentences with no Cyrillic entry."""
    sentences = [
        {"English": "This is a test sentence."},
        {"Serbian": "Ovo je test rečenica."},
    ]
    result = extract_word_from_sentences(sentences)
    assert result is None


def test_extract_word_from_empty_sentences():
    """Test extracting Cyrillic word from empty sentences list."""
    sentences = []
    result = extract_word_from_sentences(sentences)
    assert result is None


def test_fill_empty_cyrillic_fields(mocker: MockerFixture):
    """Test filling empty Cyrillic fields in the words data."""
    # Mock the YAML file operations
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch(
        "yaml.safe_load",
        return_value={
            "word1": {
                "serbian_word": {"Latin": "test", "Cyrillic": ""},
                "sentences": [
                    {"English": "This is a test."},
                    {"Cyrillic": "Ово је **тест**."},
                ],
            },
            "word2": {
                "serbian_word": {"Latin": "another", "Cyrillic": "постојећи"},
                "sentences": [
                    {"English": "This is another test."},
                    {"Cyrillic": "Ово је **други** тест."},
                ],
            },
            "word3": {
                "serbian_word": {"Latin": "no_match", "Cyrillic": ""},
                "sentences": [
                    {"English": "No match here."},
                    {"Cyrillic": "Овде нема поклапања."},
                ],
            },
            "word4": {
                "serbian_word": {"Latin": "no_sentences", "Cyrillic": ""}
                # No sentences field
            },
        },
    )
    mock_yaml_dump = mocker.patch("yaml.dump")
    mocker.patch("app.scripts.add_cyrylic.WORDS_YAML_PATH", "mock/path/words.yaml")

    # Mock print to capture output
    mock_print = mocker.patch("builtins.print")

    # Call the function
    fill_empty_cyrillic_fields()

    # Get the data that would have been written via yaml.dump's call arguments
    mock_data = mock_yaml_dump.call_args[0][0]

    # Check if the function updated the Cyrillic field correctly
    assert mock_data["word1"]["serbian_word"]["Cyrillic"] == "тест"
    # Should remain unchanged
    assert mock_data["word2"]["serbian_word"]["Cyrillic"] == "постојећи"
    # No match, should remain empty
    assert mock_data["word3"]["serbian_word"]["Cyrillic"] == ""
    # No sentences, should remain empty
    assert mock_data["word4"]["serbian_word"]["Cyrillic"] == ""

    # Verify that yaml.dump was called once
    mock_yaml_dump.assert_called_once()

    # Verify the printed output
    mock_print.assert_any_call("Updated word word1: тест")
    mock_print.assert_any_call("Completed. Updated 1 words with missing Cyrillic.")
