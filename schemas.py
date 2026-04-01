from pydantic import BaseModel,Field

class PostsBase(BaseModel):
    title:str = Field(max_length=50)
    content:str = Field(max_length=250)
    author:str = Field(max_length=25, default='Temur')

class PostCreate(PostsBase):
     pass

class PostOut(PostsBase):
    id:int = Field(ge = 1)

class PostUpdate(PostsBase):
    id:int  = Field(ge=1)   

    


    