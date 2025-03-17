from sqlalchemy.ext.asyncio import AsyncSession

from .repositories import (
    CardRepo,
    InvoiceRepo,
    SentenceRepo,
    SettingsRepo,
    StatisticsRepo,
    TextsRepo,
    UserRepo,
    UserTextRepo,
    WordRepo,
)


class Database:
    user: UserRepo
    card: CardRepo
    word: WordRepo
    sentence: SentenceRepo
    settings: SettingsRepo

    session: AsyncSession

    def __init__(
        self,
        session: AsyncSession,
        user: UserRepo = None,
        card: CardRepo = None,
        word: WordRepo = None,
        sentence: SentenceRepo = None,
        settings: SettingsRepo = None,
        statistic: StatisticsRepo = None,
        invoice: InvoiceRepo = None,
        texts: TextsRepo = None,
        user_text: UserTextRepo = None,
    ):
        """Init database."""
        self.session = session
        self.user = user or UserRepo(session=session)
        self.card = card or CardRepo(session=session)
        self.word = word or WordRepo(session=session)
        self.sentence = sentence or SentenceRepo(session=session)
        self.settings = settings or SettingsRepo(session=session)
        self.texts = texts or TextsRepo(session=session)
        self.user_text = user_text or UserTextRepo(session=session)
        self.statistic = statistic or StatisticsRepo(session=session)
        self.invoice = invoice or InvoiceRepo(session=session)
