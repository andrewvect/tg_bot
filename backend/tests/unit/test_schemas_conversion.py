"""Unit tests for Pydantic schema conversion methods."""

from app.common.db.models.sentence import Sentence
from app.common.db.models.word import Word
from app.common.shemas.words import SentenceResponce, WordResponse


class TestSentenceResponceConversion:
    """Tests for SentenceResponce.from_db_model() conversion method."""

    def test_from_db_model_all_fields(self):
        """Test conversion with all fields populated."""
        # Arrange
        db_sentence = Sentence(
            id=1,
            native_text="Hello world",
            cyrilic_text="Хелло ворлд",
            latin_text="Hello world",
            word_id=10,
        )

        # Act
        response = SentenceResponce.from_db_model(db_sentence)

        # Assert
        assert response.id == 1
        assert response.native_text == "Hello world"
        assert response.cyrilic_text == "Хелло ворлд"
        assert response.latin_text == "Hello world"

    def test_from_db_model_preserves_types(self):
        """Test that conversion preserves correct types."""
        # Arrange
        db_sentence = Sentence(
            id=42,
            native_text="Test",
            cyrilic_text="Тест",
            latin_text="Test",
            word_id=1,
        )

        # Act
        response = SentenceResponce.from_db_model(db_sentence)

        # Assert
        assert isinstance(response, SentenceResponce)
        assert isinstance(response.id, int)
        assert isinstance(response.native_text, str)
        assert isinstance(response.cyrilic_text, str)
        assert isinstance(response.latin_text, str)


class TestWordResponseConversion:
    """Tests for WordResponse.from_db_model() conversion method."""

    def test_from_db_model_without_sentences(self):
        """Test conversion of Word without sentences (sentences attribute not set)."""
        # Arrange
        db_word = Word(
            id=1,
            latin_word="hello",
            cyrillic_word="хелло",
            native_word="привет",
            legend="A greeting",
        )
        # Don't set sentences attribute - it will be None by default

        # Act
        response = WordResponse.from_db_model(db_word)

        # Assert
        assert response.word_id == 1
        assert response.latin_word == "hello"
        assert response.cyrillic_word == "хелло"
        assert response.native_word == "привет"
        assert response.legend == "A greeting"
        assert response.sentences == []

    def test_from_db_model_with_empty_sentences_list(self):
        """Test conversion of Word with empty sentences list."""
        # Arrange
        db_word = Word(
            id=2,
            latin_word="world",
            cyrillic_word="ворлд",
            native_word="мир",
            legend=None,
        )
        db_word.sentences = []

        # Act
        response = WordResponse.from_db_model(db_word)

        # Assert
        assert response.word_id == 2
        assert response.latin_word == "world"
        assert response.cyrillic_word == "ворлд"
        assert response.native_word == "мир"
        assert response.legend is None
        assert response.sentences == []

    def test_from_db_model_with_sentences(self):
        """Test conversion of Word with sentences."""
        # Arrange
        db_word = Word(
            id=3,
            latin_word="book",
            cyrillic_word="бук",
            native_word="книга",
            legend="Reading material",
        )
        db_word.sentences = [
            Sentence(
                id=1,
                native_text="I read a book",
                cyrilic_text="Я читаю книгу",
                latin_text="Ya chitayu knigu",
                word_id=3,
            ),
            Sentence(
                id=2,
                native_text="This is my book",
                cyrilic_text="Это моя книга",
                latin_text="Eto moya kniga",
                word_id=3,
            ),
        ]

        # Act
        response = WordResponse.from_db_model(db_word)

        # Assert
        assert response.word_id == 3
        assert response.latin_word == "book"
        assert response.cyrillic_word == "бук"
        assert response.native_word == "книга"
        assert response.legend == "Reading material"
        assert response.sentences is not None
        assert len(response.sentences) == 2

        # Check first sentence
        assert response.sentences[0].id == 1
        assert response.sentences[0].native_text == "I read a book"
        assert response.sentences[0].cyrilic_text == "Я читаю книгу"
        assert response.sentences[0].latin_text == "Ya chitayu knigu"

        # Check second sentence
        assert response.sentences[1].id == 2
        assert response.sentences[1].native_text == "This is my book"
        assert response.sentences[1].cyrilic_text == "Это моя книга"
        assert response.sentences[1].latin_text == "Eto moya kniga"

    def test_from_db_model_preserves_types(self):
        """Test that conversion preserves correct types."""
        # Arrange
        db_word = Word(
            id=99,
            latin_word="test",
            cyrillic_word="тест",
            native_word="тест",
            legend="Test word",
        )
        db_word.sentences = []

        # Act
        response = WordResponse.from_db_model(db_word)

        # Assert
        assert isinstance(response, WordResponse)
        assert isinstance(response.word_id, int)
        assert isinstance(response.latin_word, str)
        assert isinstance(response.cyrillic_word, str)
        assert isinstance(response.native_word, str)
        assert isinstance(response.legend, str) or response.legend is None
        assert isinstance(response.sentences, list)

    def test_from_db_model_none_legend(self):
        """Test conversion with None legend field."""
        # Arrange
        db_word = Word(
            id=5,
            latin_word="example",
            cyrillic_word="ексампл",
            native_word="пример",
            legend=None,
        )
        db_word.sentences = []

        # Act
        response = WordResponse.from_db_model(db_word)

        # Assert
        assert response.legend is None
