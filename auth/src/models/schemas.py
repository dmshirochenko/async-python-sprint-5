from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    username: str
    token: str
    is_active: bool

    class Config:
        orm_mode = True
