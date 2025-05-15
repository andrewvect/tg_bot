"""Tests for the parse_git_words script."""
from typing import LiteralString
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.common.db.models import Word
from app.common.db.models.sentence import Sentence
from app.core.config import Settings
from app.scripts.parse_git_words import GitWordParser


@pytest.fixture
def mock_settings():
    """Fixture for test settings."""
    settings = Settings()
    settings.URL_TO_GIT_FILES = "https://example.com/"
    return settings


@pytest.fixture
def sample_yaml_data():
    """Fixture providing sample YAML data for testing."""
    yaml_content = """
    1:
      serbian_word:
        Latin: "jedan"
        Cyrillic: "један"
      translation: "one"
      bio: "The number 1"
      sentences:
        - Latin: "Ja imam jedan pas."
          Cyrillic: "Ја имам један пас."
          Russian: "У меня одна собака."
    2:
      serbian_word:
        Latin: "dva"
        Cyrillic: "два"
      translation: "two"
      bio: "The number 2"
      sentences:
        - Latin: "Imam dva psa."
          Cyrillic: "Имам два пса."
          Russian: "У меня две собаки."
    """
    return yaml_content


@pytest.fixture
def parser(mock_settings):
    """Fixture for GitWordParser instance."""
    return GitWordParser(config=mock_settings)


class TestGitWordParser:
    def test_get_words_from_git(self, parser: GitWordParser, sample_yaml_data):
        """Test fetching words from git."""
        with patch("requests.get") as mock_get:
            # Setup mock response for each file
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = sample_yaml_data
            mock_get.return_value = mock_response

            # Call the method
            result = parser.get_words_from_git()

            # Assert the results
            # Each file returns the same data
            assert result == sample_yaml_data * len(parser.files)
            assert mock_get.call_count == len(parser.files)  # Called once per file

    def test_get_words_from_git_failed_request(self, parser: GitWordParser):
        """Test handling failed requests when fetching words."""
        with patch("requests.get") as mock_get:
            # Setup mock response for failed request
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            # Call the method
            with patch("app.scripts.parse_git_words.logger") as mock_logger:
                result = parser.get_words_from_git()

                # Assert the results
                assert result == ""  # Empty string returned for failed requests
                assert mock_get.call_count == len(parser.files)  # Called once per file
                assert mock_logger.error.call_count == len(
                    parser.files
                )  # Error logged for each file

    def test_create_db_connection(self, parser):
        """Test database connection creation."""
        with patch("app.scripts.parse_git_words.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine

            with patch("app.scripts.parse_git_words.sessionmaker") as mock_sessionmaker:
                # Call the method
                result = parser.create_db_connection()

                # Assert results
                mock_create_engine.assert_called_once()
                mock_sessionmaker.assert_called_once_with(
                    autocommit=False, autoflush=False, bind=mock_engine
                )
                assert result == mock_sessionmaker.return_value

    def test_save_words_to_db(
        self, parser: GitWordParser, sample_yaml_data: LiteralString
    ):
        """Test saving words to the database."""
        # Mock get_words_from_git to return sample data
        with patch.object(parser, "get_words_from_git", return_value=sample_yaml_data):
            # Mock yaml.safe_load to return parsed data
            parsed_data = {
                1: {
                    "serbian_word": {"Latin": "jedan", "Cyrillic": "један"},
                    "translation": "one",
                    "bio": "The number 1",
                },
                2: {
                    "serbian_word": {"Latin": "dva", "Cyrillic": "два"},
                    "translation": "two",
                    "bio": "The number 2",
                },
            }
            with patch("yaml.safe_load", return_value=parsed_data):
                # Mock the session
                mock_session = MagicMock()
                mock_session_instance = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_session_instance

                with patch.object(
                    parser, "create_db_connection", return_value=mock_session
                ):
                    # Call the method
                    parser.save_words_to_db()

                    # Assert results
                    assert mock_session_instance.add.call_count == 2  # Two words added
                    assert (
                        mock_session_instance.commit.call_count == 2
                    )  # Committed twice

    def test_save_words_to_db_error(
        self, parser: GitWordParser, sample_yaml_data: LiteralString
    ):
        """Test handling database errors when saving words."""
        # Mock get_words_from_git to return sample data
        with patch.object(parser, "get_words_from_git", return_value=sample_yaml_data):
            # Mock yaml.safe_load to return parsed data
            parsed_data = {
                1: {
                    "serbian_word": {"Latin": "jedan", "Cyrillic": "један"},
                    "translation": "one",
                    "bio": "The number 1",
                }
            }
            with patch("yaml.safe_load", return_value=parsed_data):
                # Mock the session to raise an error
                mock_session = MagicMock()
                mock_session_instance = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_session_instance
                mock_session_instance.commit.side_effect = SQLAlchemyError(
                    "Database error"
                )

                with patch.object(
                    parser, "create_db_connection", return_value=mock_session
                ):
                    with patch("app.scripts.parse_git_words.logger") as mock_logger:
                        # Call the method
                        parser.save_words_to_db()

                        # Assert results
                        mock_logger.error.assert_called_once()  # Error logged

    def test_update_word_in_db(
        self, parser: GitWordParser, sample_yaml_data: LiteralString
    ):
        """Test updating words in the database."""
        # Mock get_words_from_git to return sample data
        with patch.object(parser, "get_words_from_git", return_value=sample_yaml_data):
            # Mock yaml.safe_load to return parsed data
            parsed_data = {
                1: {
                    "serbian_word": {"Latin": "jedan", "Cyrillic": "један"},
                    "translation": "one",
                    "bio": "The number 1",
                    "sentences": [
                        {
                            "Latin": "Ja imam jedan pas.",
                            "Cyrillic": "Ја имам један пас.",
                            "Russian": "У меня одна собака.",
                        }
                    ],
                },
                2: {
                    "serbian_word": {"Latin": "dva", "Cyrillic": "два"},
                    "translation": "two",
                    "bio": "The number 2",
                    "sentences": [
                        {
                            "Latin": "Imam dva psa.",
                            "Cyrillic": "Имам два пса.",
                            "Russian": "У меня две собаки.",
                        }
                    ],
                },
            }
            with patch("yaml.safe_load", return_value=parsed_data):
                # Mock the session
                mock_session = MagicMock()
                mock_session_instance = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_session_instance

                # Create mock words for get method
                word1 = Word(
                    id=1,
                    native_word="old_one",
                    latin_word="jedan",
                    cyrillic_word="old_cyrillic_1",
                    legend="old_bio_1",
                )
                word1.sentences = []

                word2 = Word(
                    id=2,
                    native_word="two",
                    latin_word="dva",
                    cyrillic_word="два",
                    legend="The number 2",
                )
                # Add an existing sentence to word2
                sentence = Sentence(
                    native_text="У меня две собаки.",
                    cyrilic_text="Имам два пса.",
                    latin_text="Imam dva psa.",
                    word_id=2,
                )
                word2.sentences = [sentence]

                # Mock session.get to return appropriate word based on ID
                def mock_get(cls, id):  # noqa
                    if id == 1:
                        return word1
                    elif id == 2:
                        return word2
                    return None

                mock_session_instance.get = mock_get

                with patch.object(
                    parser, "create_db_connection", return_value=mock_session
                ):
                    with patch("app.scripts.parse_git_words.logger") as mock_logger:
                        # Call the method
                        parser.update_word_in_db()

                        # Assert results
                        assert word1.native_word == "one"  # Word 1 updated
                        assert word1.cyrillic_word == "један"
                        assert word1.legend == "The number 1"

                        # Word 2 not updated (values already match)
                        assert word2.native_word == "two"
                        assert word2.cyrillic_word == "два"
                        assert word2.legend == "The number 2"

                        # Check sentences were added correctly
                        # Only one new sentence added (for word 1)
                        assert mock_session_instance.add.call_count == 1

                        # Make sure logs were created
                        mock_logger.info.assert_called_once()

    def test_update_nonexistent_word(self, parser: GitWordParser, sample_yaml_data):
        """Test handling nonexistent words during update."""
        # Mock get_words_from_git to return sample data
        with patch.object(parser, "get_words_from_git", return_value=sample_yaml_data):
            # Mock yaml.safe_load to return parsed data
            parsed_data = {
                999: {  # Non-existent ID
                    "serbian_word": {"Latin": "missing", "Cyrillic": "несуществующий"},
                    "translation": "missing",
                    "bio": "This word does not exist in DB",
                }
            }
            with patch("yaml.safe_load", return_value=parsed_data):
                # Mock the session
                mock_session = MagicMock()
                mock_session_instance = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_session_instance

                # Mock session.get to return None (word not found)
                mock_session_instance.get.return_value = None

                with patch.object(
                    parser, "create_db_connection", return_value=mock_session
                ):
                    with patch("app.scripts.parse_git_words.logger") as mock_logger:
                        # Call the method
                        parser.update_word_in_db()

                        # Assert results
                        mock_logger.warning.assert_called_once()  # Warning logged for missing word

    def test_update_word_with_invalid_sentence(
        self, parser: GitWordParser, sample_yaml_data
    ):
        """Test handling invalid sentence data during update."""
        # Mock get_words_from_git to return sample data
        with patch.object(parser, "get_words_from_git", return_value=sample_yaml_data):
            # Mock yaml.safe_load to return parsed data with invalid sentence
            parsed_data = {
                1: {
                    "serbian_word": {"Latin": "jedan", "Cyrillic": "један"},
                    "translation": "one",
                    "bio": "The number 1",
                    "sentences": [
                        "This is an invalid sentence object"  # Should be dict but is string
                    ],
                }
            }
            with patch("yaml.safe_load", return_value=parsed_data):
                # Mock the session
                mock_session = MagicMock()
                mock_session_instance = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_session_instance

                # Create mock word
                word = Word(
                    id=1,
                    native_word="one",
                    latin_word="jedan",
                    cyrillic_word="један",
                    legend="The number 1",
                )
                word.sentences = []

                mock_session_instance.get.return_value = word

                with patch.object(
                    parser, "create_db_connection", return_value=mock_session
                ):
                    with patch("app.scripts.parse_git_words.logger") as mock_logger:
                        # Call the method
                        parser.update_word_in_db()

                        # Assert results
                        mock_logger.error.assert_called_once()  # Error logged for invalid sentence

    def test_update_word_database_error(self, parser: GitWordParser, sample_yaml_data):
        """Test handling database errors during word update."""
        # Mock get_words_from_git to return sample data
        with patch.object(parser, "get_words_from_git", return_value=sample_yaml_data):
            # Mock yaml.safe_load to return parsed data
            parsed_data = {
                1: {
                    "serbian_word": {"Latin": "jedan", "Cyrillic": "један"},
                    "translation": "one",
                    "bio": "The number 1",
                }
            }
            with patch("yaml.safe_load", return_value=parsed_data):
                # Mock the session to raise an error
                mock_session = MagicMock()
                mock_session_instance = MagicMock()
                mock_session.return_value.__enter__.return_value = mock_session_instance

                # Create mock word
                word = Word(
                    id=1,
                    native_word="old_one",
                    latin_word="jedan",
                    cyrillic_word="old_cyrillic",
                    legend="old_bio",
                )

                mock_session_instance.get.return_value = word
                mock_session_instance.commit.side_effect = SQLAlchemyError(
                    "Database error"
                )

                with patch.object(
                    parser, "create_db_connection", return_value=mock_session
                ):
                    with patch("app.scripts.parse_git_words.logger") as mock_logger:
                        # Call the method
                        parser.update_word_in_db()

                        # Assert results
                        mock_logger.error.assert_called_once()  # Error logged


if __name__ == "__main__":
    pytest.main(["-v", "test_parse_git_words.py"])
