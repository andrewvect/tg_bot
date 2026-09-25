from sqlalchemy.ext.asyncio import AsyncSession

from app.common.db.models import Invoice, Sentence, Statistic, Texts, UserText

from .repositories import (
    CardRepo,
    CardRepoProtocol,
    InvoiceRepo,
    RepositoryProtocol,
    SentenceRepo,
    SettingsRepo,
    SettingsRepoProtocol,
    StatisticsRepo,
    TextsRepo,
    UserRepo,
    UserRepoProtocol,
    UserTextRepo,
    WordRepo,
    WordRepoProtocol,
)


class Database:
    """Aggregates all repositories behind their interfaces.

    Attributes and constructor parameters are typed against the repository
    Protocols, not the concrete classes - so anything that receives a
    Database (WordCardHandler, ...) only ever sees the interface, and a
    fake repository can be substituted here (e.g. in a test) without this
    class or its consumers changing. Constructing the real, concrete repos
    is this class's own job as the composition root; that's the one place
    that is allowed - and expected - to know about them.
    """

    user: UserRepoProtocol
    card: CardRepoProtocol
    word: WordRepoProtocol
    sentence: RepositoryProtocol[Sentence]
    settings: SettingsRepoProtocol
    statistic: RepositoryProtocol[Statistic]
    invoice: RepositoryProtocol[Invoice]
    texts: RepositoryProtocol[Texts]
    user_text: RepositoryProtocol[UserText]

    session: AsyncSession

    def __init__(
        self,
        session: AsyncSession,
        user: UserRepoProtocol | None = None,
        card: CardRepoProtocol | None = None,
        word: WordRepoProtocol | None = None,
        sentence: RepositoryProtocol[Sentence] | None = None,
        settings: SettingsRepoProtocol | None = None,
        statistic: RepositoryProtocol[Statistic] | None = None,
        invoice: RepositoryProtocol[Invoice] | None = None,
        texts: RepositoryProtocol[Texts] | None = None,
        user_text: RepositoryProtocol[UserText] | None = None,
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
