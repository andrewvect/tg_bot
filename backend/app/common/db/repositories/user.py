"""User repository file."""


from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from .abstract import Repository


class NewUser(Exception):
    """Raised when a new user is successfully created."""

    pass


class NoUsersFound(Exception):
    """Raised when no users are found in the repository."""

    pass


class UserRepo(Repository[User]):
    """
    User repository for CRUD and other SQL queries.

    Provides methods for creating, retrieving, and updating user records.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a session and user model.

        Parameters:
            session (AsyncSession): The asynchronous database session.
        """
        super().__init__(type_model=User, session=session)

    async def create(
        self,
        telegram_id: int,
        user_name: str | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        is_premium: bool = False,
    ) -> User:
        """
        Create a new user in the repository.

        Parameters:
            telegram_id (int): The user's Telegram ID.
            user_name (Optional[str]): Optional username.
            first_name (Optional[str]): Optional first name.
            second_name (Optional[str]): Optional second name.
            is_premium (bool): Is the user a premium member? Defaults to False.

        Returns:
            User: The newly created user object.
        """
        new_user = User(
            telegram_id=telegram_id,
            user_name=user_name,
            first_name=first_name,
            second_name=second_name,
            is_premium=is_premium,
        )
        self.session.add(new_user)
        try:
            await self.session.commit()
            raise NewUser

        except IntegrityError:
            await self.session.rollback()

    async def get_all_users(self) -> list[User]:
        """
        Retrieve all users from the repository.

        Returns:
            List[User]: A list of all user objects.

        Raises:
            NoUsersFound: If no users are found in the repository.
        """
        users_list = await self._fetch_all_users()
        if not users_list:
            raise NoUsersFound("No users found in the database.")
        return users_list

    async def _fetch_all_users(self) -> list[User]:
        """
        Helper method to fetch all users from the database.

        Returns:
            List[User]: A list of all users.
        """
        statement = select(self.type_model)
        result = await self.session.execute(statement)
        users = result.scalars().unique().all()
        return users

    async def update_paid_status(self, telegram_id: int):
        """
        Update the premium status of a user to True.

        Parameters:
            telegram_id (int): The Telegram ID of the user to update.

        Raises:
            NoUsersFound: If the user is not found in the database.
        """
        user = await self._get_user_by_telegram_id(telegram_id)
        if not user:
            raise NoUsersFound(f"No user found with telegram_id: {telegram_id}.")
        user.paid = True
        await self.session.commit()

    async def _get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        """
        Helper method to retrieve a user by Telegram ID.

        Parameters:
            telegram_id (int): The user's Telegram ID.

        Returns:
            Optional[User]: The user object or None if not found.
        """
        statement = select(self.type_model).where(
            self.type_model.telegram_id == telegram_id
        )
        result = await self.session.execute(statement)
        return result.scalars().first()
