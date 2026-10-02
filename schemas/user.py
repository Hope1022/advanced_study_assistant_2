import enum
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import datetime

class UserRegisterSchema(BaseModel):
    email:     EmailStr
    password:  str
    full_name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number.")
        return value

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        if len(value) > 100:
            raise ValueError("Full name must be under 100 characters.")
        return value


class UserLoginSchema(BaseModel):
    email:    EmailStr
    password: str


class UserUpdateSchema(BaseModel):
    full_name:              str | None = None
    avatar_url:             str | None = None
    preferred_translation:  str | None = None
    bio:                    str | None = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        if len(value) > 100:
            raise ValueError("Full name must be under 100 characters.")
        return value

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UserUpdateSchema":
        fields = [self.full_name, self.avatar_url,
                  self.preferred_translation, self.bio]
        if all(f is None for f in fields):
            raise ValueError("At least one field must be provided to update.")
        return self


class ProfileResponseSchema(BaseModel):
    full_name:              str
    avatar_url:             str | None
    preferred_translation:  str
    bio:                    str | None
    updated_at:             datetime

    model_config = {"from_attributes": True}


class UserResponseSchema(BaseModel):
    id:          int
    email:       str
    #role:        UserRole
    is_active:   bool
    is_verified: bool
    created_at:  datetime
    last_login:  datetime | None
    #profile:     ProfileResponseSchema | None

    model_config = {"from_attributes": True}