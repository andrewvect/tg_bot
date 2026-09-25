"""Repositories module."""

from .abstract import Repository
from .card import CardRepo, CardRetriever
from .interfaces import (
    CardRepoProtocol,
    RepositoryProtocol,
    SettingsRepoProtocol,
    UserRepoProtocol,
    WordRepoProtocol,
)
from .invoice import InvoiceRepo
from .sentence import SentenceRepo
from .settings import SettingsRepo
from .statistics import StatisticsRepo
from .texts import TextsRepo
from .user import UserRepo
from .user_text import UserTextRepo
from .word import WordRepo

__all__ = (
    "UserRepo",
    "UserRepoProtocol",
    "Repository",
    "RepositoryProtocol",
    "CardRepo",
    "CardRepoProtocol",
    "WordRepo",
    "WordRepoProtocol",
    "SentenceRepo",
    "TextsRepo",
    "CardRetriever",
    "InvoiceRepo",
    "SettingsRepo",
    "SettingsRepoProtocol",
    "StatisticsRepo",
    "UserTextRepo",
)
