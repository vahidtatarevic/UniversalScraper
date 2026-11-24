from pydantic import EmailStr
from sqlmodel import Field, SQLModel, UniqueConstraint


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str | None = Field(default=None, unique=True)
    hashed_password: str | None = None
    is_verified: bool = False


class UserIdentity(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("provider", "provider_id"),)

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    provider: str
    provider_id: str


class UserCreate(SQLModel):
    username: str = Field(
        min_length=3,
        max_length=30,
        schema_extra={"pattern": r"^[a-zA-Z0-9_]+$"},
    )
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class GoogleLogin(SQLModel):
    token: str


class ResendVerification(SQLModel):
    email: EmailStr
