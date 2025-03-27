"""Script for upload words from git to database"""
import requests
import yaml
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.common.db.models import Word
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
                    ):
                        existing_word.native_word = item["translation"]
                        existing_word.cyrillic_word = item["serbian_word"]["Cyrillic"]
                        session.commit()
                        count += 1
                except SQLAlchemyError as e:
                    logger.error(f"Database error when updating word: {e}")
                    break
        logger.info(f"Updated {count} words.")


if __name__ == "__main__":
    # No need for logging.basicConfig as we're using the custom logger
    parser = GitWordParser(config=settings)
    parser.update_word_in_db()
