from sqlalchemy import Integer, MetaData
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from sqlalchemy.orm.decl_api import DeclarativeBase

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class Base(DeclarativeBase):
    # Remove the classmethod as it's not needed with declared_attr
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    __allow_unmapped__ = False

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)


Base.metadata = metadata
