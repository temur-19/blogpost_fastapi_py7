from sqlalchemy import select
from fastapi import Depends, HTTPException, APIRouter
from typing import List

from database import get_db
from models import Posts,Author,Like,Comment
from schemas.posts import PostOut, PostCreate, PostUpdate, LikeOut, CommentOut
from schemas.users import AuthorOut
from dependencies import get_current_user,role_check



post_router = APIRouter(prefix='/api/posts')

@post_router.post('/',response_model=PostOut)
async def post_creat(post_in:PostCreate, db = Depends(get_db), _: AuthorOut = Depends(role_check('admin'))):
    stmt  = select(Author).where(Author.id == post_in.author_id)
    author = await db.scalar(stmt)
    if not author:
        raise HTTPException(status_code=400,  detail=f"{post_in.author_id} li author mavud  emas")
    
    post  = Posts(**post_in.model_dump())

    db.add(post)
    await db.commit()
    await db.refresh(post)

    return post


@post_router.get('/', response_model=List[PostOut])
async def post_out(db = Depends(get_db)):
    stmt = select(Posts)
    result = await db.scalars(stmt)
    posts = result.all()
    return posts


@post_router.get('/{post_id}', response_model=PostOut)
async def get_post(post_id: int, db = Depends(get_db)):
    stmt = select(Posts).where(Posts.id == post_id)
    post = await db.scalar(stmt)

    if not post:
        raise HTTPException(status_code=404, detail=f"{post_id}-raqamli post mavjud emas")

    return post

@post_router.put('/{post_id}', response_model=PostOut)
async def update_post(post_id:int, post_in: PostUpdate, db = Depends(get_db), current_user: AuthorOut = Depends(role_check('admin'))):
    stmt = select(Posts).where(Posts.id == post_id)
    post:Posts = await db.scalar(stmt)

    if not post:
        raise HTTPException(status_code=404, detail=f"{post_id}-raqamli post mavjud emas")
    
    post.title = post_in.title
    post.content = post_in.content
    post.image_path = post_in.image_path

    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@post_router.delete('/{post_id}')
async def delete_post(post_id:int, db = Depends(get_db)):
    stmt = select(Posts).where(Posts.id == post_id)
    post = await db.scalar(stmt)
    if not post:
        raise HTTPException(status_code=404, detail=f'{post_id}-post mavjud emas')
    await db.delete(post)
    await db.commit()
    return {'status':404}

@post_router.post('/like/{post_id}', response_model=LikeOut)
async def like_post(post_id:int, db = Depends(get_db), current_user: AuthorOut = Depends(get_current_user)):
    stmt = select(Posts).where(Posts.id == post_id)
    post = await db.scalar(stmt)
    if not post:
        raise HTTPException(status_code=404, detail=f'{post_id}-post mavjud emas')
    like = select(Like).where(Like.post_id == post_id,Like.author_id == current_user.id)
    if await db.scalar(like):
        raise HTTPException(status_code=400, detail=f'{post_id}-postga allaqachon like bosilgan')
    like = Like(post_id=post_id, author_id=current_user.id)
    db.add(like)
    await db.commit()
    await db.refresh(like)
    return like


@post_router.post('/comment/{post_id}', response_model=CommentOut)
async def comment_post(post_id:int, comment:str, db = Depends(get_db), current_user: AuthorOut = Depends(get_current_user)):
    stmt = select(Posts).where(Posts.id == post_id)
    post = await db.scalar(stmt)
    if not post:
        raise HTTPException(status_code=404, detail=f'{post_id}-post mavjud emas')
    
    comment = Comment(content=comment, post_id=post_id, author_id=current_user.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment

@post_router.get('/comments/{post_id}', response_model=List[str])
async def get_comments(post_id:int, db = Depends(get_db)):
    stmt = select(Comment).where(Comment.post_id == post_id)
    comments = await db.scalars(stmt).all()
    return [comment.content for comment in comments]


@post_router.get('/likes/{post_id}', response_model=int)
async def get_likes(post_id:int, db = Depends(get_db)):
    stmt = select(Like).where(Like.post_id == post_id)
    likes = await db.scalars(stmt)
    return len(likes.all())