import re

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


# Base user model
class PrivateUsersResponse(BaseModel):
    username: str
    email: str
    phone_no: str
    rating: float
    locked: bool
    disabled: bool

    model_config = ConfigDict(from_attributes=True)


class PublicUsersResponse(BaseModel):
    username: str
    rating: float

    model_config = ConfigDict(from_attributes=True)


class ProtectedUserResponse(PublicUsersResponse):
    phone_no: str
    email: str

    model_config = ConfigDict(from_attributes=True)


# user create model
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone_no: str
    password: str

    @field_validator("username")
    @classmethod
    def username_validation(cls, u: str) -> str:
        if " " in u:
            raise ValueError("Username cannot contain spaces")
        if len(u) < 3 or len(u) > 20:
            raise ValueError("Length of username should be between 3 and 20")
        if re.search(r'[!#$%^&*(),.?":{}|<>]', u):
            raise ValueError(
                "Username should not contain any special characters other than @"
            )
        return u

    @field_validator("email")
    @classmethod
    def email_validation(cls, e: str) -> str:
        if not e.endswith("@gectcr.ac.in"):
            raise ValueError("This is not a student email of GECT")
        return e

    @field_validator("phone_no")
    @classmethod
    def phone_no_validation(cls, p: str) -> str:
        try:
            p = str(int(p))

            if len(p) != 10:
                raise ValueError("This is not a valid phone number!")

            return p
        except Exception as e:
            raise ValueError(f"This is not a valid phone number! {e}")

    @field_validator("password")
    @classmethod
    def password_constraints(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 20:
            raise ValueError("Password must be at most 20 characters long")
        if " " in v:
            raise ValueError("Password must not contain a space")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v
