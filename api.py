from fastapi import APIRouter, Depends, HTTPException
from schemas import PostOut,PostCreate, PostUpdate,AuthorCreate, AuthorOut
from database import get_db
from database import Base, engine
from models import Posts, Author
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List

Base.metadata.create_all(bind=engine)
api_router = APIRouter(prefix='/api/posts')




@api_router.post('/users',response_model=AuthorOut)
def author_creat(author_in:AuthorCreate, db:Session = Depends(get_db)):
    author  = Author(**author_in.model_dump())
    db.add(author)
    db.commit()
    db.refresh(author)
    return author




@api_router.post('/',response_model=PostOut)
def post_creat(post_in:PostCreate, db = Depends(get_db)):
    stmt  = select(Author).where(Author.id == post_in.author_id)
    autor = db.scalar(stmt)
    if not autor:
        raise HTTPException(status_code=400,  detail=f"{post_in.author_id} li author mavud  emas")
    
    post  = Posts(**post_in.model_dump())

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


@api_router.get('/', response_model=List[PostOut])
def post_out(db = Depends(get_db)):
    stmt = select(Posts)
    posts = db.scalars(stmt).all()
    return posts


@api_router.get('/{post_id}', response_model=PostOut)
def get_post(post_id: int, db = Depends(get_db)):
    stmt = select(Posts).where(Posts.id == post_id)
    post = db.scalar(stmt)

    if not post:
        raise HTTPException(status_code=404, detail=f"{post_id}-raqamli post mavjud emas")

    return post

@api_router.put('/{post_id}', response_model=PostOut)
def update_post(post_id:int, post_in: PostUpdate, db = Depends(get_db),):
    stmt = select(Posts).where(Posts.id == post_id)
    post:Posts = db.scalar(stmt)

    if not post:
        raise HTTPException(status_code=404, detail=f"{post_id}-raqamli post mavjud emas")
    
    post.title = post_in.title
    post.content = post_in.content
    post.image_path = post_in.image_path

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@api_router.delete('/{post_id}')
def  delete_post(post_id:int, db = Depends(get_db)):
    stmt = select(Posts).where(Posts.id == post_id)
    post = db.scalar(stmt)
    if not post:
        raise HTTPException(status_code=404, detail=f'{post_id}-post mavjud emas')
    db.delete(post)
    db.commit()
    return {'status':404}