from pydantic import BaseModel


class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: str = ""
    username: str
    language_code: str
    added_to_attachment_menu: bool
    allows_write_to_pm: bool
    photo_url: str


class TelegramAuthData(BaseModel):
    user: TelegramUser
    auth_date: str
    signature: str
    hash: str


class TelegramAuthResponse(BaseModel):
    status: str
    user_id: int
    username: str
    access_token: str


class TelegramInitData(BaseModel):
    string: str


class RequestInitData(BaseModel):
    init_data: str


class ResponceToken(BaseModel):
    access_token: str
    expires_in: int
    user_id: int
