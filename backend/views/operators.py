from pydantic import BaseModel


class CreateOperatorView(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    address: str


class LoginView(BaseModel):
    email: str
    password: str


class ReadOperatorView(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        orm_mode = True