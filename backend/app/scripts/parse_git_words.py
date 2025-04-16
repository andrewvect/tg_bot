"""Script for upload words from git to database"""
import requests
import yaml
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.common.db.models import Word
from app.common.db.models.sentence import Sentence
from app.core.config import Settings, settings
from app.utils.logger import setup_logger

# Set up logger using the custom logger utility
logger = setup_logger(__name__)


class GitWordParser:
    def __init__(self, config: Settings):
        self.url_to_git_file = config.URL_TO_GIT_FILE

    def get_words_from_git(self):
        words = requests.get(self.url_to_git_file).text
        return words

    def create_db_connection(self) -> sessionmaker:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True, future=True)
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return Session

    def save_words_to_db(self):
        words_text = self.get_words_from_git()
        parsed_data = yaml.safe_load(words_text)
        Session = self.create_db_connection()
        with Session() as session:
            for id, item in parsed_data.items():
                word_data = Word(
                    id=id,
                    native_word=item["translation"],
                    foreign_word=item["serbian_word"]["Latin"],
                    cyrillic_word=item["serbian_word"]["Cyrillic"],
                )
                try:
                    session.add(word_data)
                    session.commit()
                except SQLAlchemyError as e:
                    logger.error(f"Database error: {e}")
                    break

    def update_word_in_db(self):
        words_text = self.get_words_from_git()
        parsed_data = yaml.safe_load(words_text)

        count = 0
        sentences_count = 0
        Session = self.create_db_connection()
        with Session() as session:
            for id, item in parsed_data.items():
                try:
                    # Update word based on the Serbian Latin value as unique identifier.
                    existing_word = session.get(Word, id)

                    if (
                        existing_word.native_word != item["translation"]
                        or existing_word.cyrillic_word
                        != item["serbian_word"]["Cyrillic"]
                        or existing_word.legend != item["bio"]
                    ):
                        existing_word.native_word = item["translation"]
                        existing_word.cyrillic_word = item["serbian_word"]["Cyrillic"]
                        existing_word.legend = item["bio"]
                        session.commit()
                        count += 1

                    # Handle sentences if they exist in the parsed data
                    if "sentences" in item and item["sentences"]:
                        # Check current sentences
                        existing_sentences = (
                            {s.latin_text: s for s in existing_word.sentences}
                            if existing_word.sentences
                            else {}
                        )

                        # Process each sentence from git data
                        for sentence_data in item["sentences"]:
                            latin_text = sentence_data["Latin"]
                            cyrillic_text = sentence_data["Cyrillic"]
                            native_text = sentence_data["Russian"]

                            if latin_text in existing_sentences:
                                # Update existing sentence if needed
                                sentence = existing_sentences[latin_text]
                                if (
                                    sentence.native_text != native_text
                                    or sentence.cyrilic_text != cyrillic_text
                                ):
                                    sentence.native_text = native_text
                                    sentence.cyrilic_text = cyrillic_text
                                    sentences_count += 1
                            else:
                                # Create new sentence
                                new_sentence = Sentence(
                                    native_text=native_text,
                                    cyrilic_text=cyrillic_text,
                                    latin_text=latin_text,
                                    word_id=existing_word.id,
                                )
                                session.add(new_sentence)
                                sentences_count += 1

                        # Commit sentence changes
                        if sentences_count > 0:
                            session.commit()

                except SQLAlchemyError as e:
                    logger.error(f"Database error when updating word: {e}")
                    break
        logger.info(f"Updated {count} words and {sentences_count} sentences.")


if __name__ == "__main__":
    # No need for logging.basicConfig as we're using the custom logger
    parser = GitWordParser(config=settings)
    try:
        parser.save_words_to_db()
    except Exception:
        pass
    parser.update_word_in_db()
