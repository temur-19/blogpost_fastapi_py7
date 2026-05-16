from pydantic import BaseModel,Field


class AuthorBase(BaseModel):
    first_name:str = Field(max_length=100)
    last_name:str = Field(max_length=100)
    role: str | None = Field(default='user', max_length=50)
    
class AuthorCreate(AuthorBase):
    username:str = Field(min_length = 3, max_length=100)
    password:str = Field(min_length= 6, max_length=100)

class AuthorOut(AuthorBase):
    id:int = Field(ge = 1)
    user_avatar:str = Field(default=None, max_length=200)

class Token(BaseModel):
    access_token: str
    token_type: str
