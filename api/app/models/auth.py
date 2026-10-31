from pydantic import BaseModel, EmailStr, Field

from app.models.users import UserMe


class RegisterIn(BaseModel):
    f_name: str = Field(min_length=1, max_length=50, title="First name")
    m_name: str | None = Field(default=None, max_length=50, title="Middle name")
    l_name: str = Field(min_length=1, max_length=50, title="Last name")
    email: EmailStr = Field(title="Email")
    password: str = Field(min_length=8, max_length=128, title="Password",
                          json_schema_extra={"format": "password"})


class LoginIn(BaseModel):
    email: EmailStr = Field(title="Email")
    password: str = Field(min_length=1, max_length=128, title="Password",
                          json_schema_extra={"format": "password"})


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserMe
