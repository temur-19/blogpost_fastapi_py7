from pydantic import BaseModel,Field






class AuthorBase(BaseModel):
    first_name:str = Field(max_length=100)
    last_name:str = Field(max_length=100)

class AuthorCreate(AuthorBase):
    pass 

class AuthorOut(AuthorBase):
    id:int = Field(ge = 1)



class PostsBase(BaseModel):
    title:str = Field(max_length=50)
    content:str = Field(max_length=250)
    author:str = Field(max_length=25, default='Temur')

class PostCreate(PostsBase):
     pass
     author_id:int
     

class PostOut(PostsBase):
    id:int = Field(ge = 1)

class PostUpdate(PostsBase):
    id:int  = Field(ge=1)   

    


    