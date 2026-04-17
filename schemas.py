from pydantic import BaseModel,Field






class AuthorBase(BaseModel):
    first_name:str = Field(max_length=100)
    last_name:str = Field(max_length=100)

class AuthorCreate(AuthorBase):
    username:str = Field(min_length = 3, max_length=100)
    password:str = Field(min_length= 6, max_length=100)

class AuthorOut(AuthorBase):
    id:int = Field(ge = 1)

class Token(BaseModel):
    access_token: str
    token_type: str



class PostsBase(BaseModel):
    title:str = Field(max_length=50)
    content:str = Field(max_length=250)
    author_id:int

class PostCreate(PostsBase):
    pass 


class PostOut(PostsBase):
    id:int = Field(ge = 1)


class PostUpdate(PostsBase):
    id:int  = Field(ge=1)   

    
class LikeBase(BaseModel):
    post_id:int
    author_id:int

class LikeCreate(LikeBase):
    pass    

class LikeOut(LikeBase):
    id:int = Field(ge=1)    

class CommentBase(BaseModel):
    content:str = Field(max_length=250)
    post_id:int
    author_id:int

class CommentCreate(CommentBase):
    pass    

class CommentOut(CommentBase):
    id:int = Field(ge=1)
    