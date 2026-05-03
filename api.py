import jwt
import asyncio
import security
import shutil

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession as Session
from fastapi import Depends, HTTPException, status, APIRouter, BackgroundTasks,UploadFile,File
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordRequestForm,OAuth2PasswordBearer
from typing import List
from email_servis import send_welcome_email, send_telegram_message


from schemas import PostOut, PostCreate, PostUpdate, AuthorCreate, AuthorOut, Token, LikeCreate, LikeOut, CommentCreate, CommentOut
from database import get_db
from models import Posts,Author,Like,Comment


api_router = APIRouter(prefix='/api/posts')


oauth2_schema = OAuth2PasswordBearer(tokenUrl="api/posts/token")

async def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token yaroqsiz yoki muddati t   ugagan"
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        author_id: str = payload.get("sub")
        if author_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    author = await db.scalar(select(Author).where(Author.id == int(author_id)))
    if author is None:
        raise credentials_exception

    return author


@api_router.post('/users/upload_avatar/')
async def upload_avatar(file: UploadFile = File(...),
                        current_user: AuthorOut = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    from main import UPLOAD_FOLDER
    file_extension = file.filename.split(".")[-1]
    file_location = f"{UPLOAD_FOLDER}/{current_user.id}_avatar.{file_extension}"
    static_location = f"/static/{current_user.id}_avatar.{file_extension}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    current_user.user_avatar = static_location
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@api_router.post('/register',response_model=AuthorOut)
async def author_creat(bg_tasks: BackgroundTasks, author_in:AuthorCreate, db:Session = Depends(get_db)):
    author = await db.scalar(select(Author).where(Author.username == author_in.username))
    if author:
        raise HTTPException(status_code=404, detail='Bunday foydalanuvchi mavjud')
    
    author = Author(
    username=author_in.username,
    first_name=author_in.first_name,
    last_name=author_in.last_name,
    hashed_password = security.get_password_hash(author_in.password))
    db.add(author)
    await db.commit()
    await db.refresh(author)
    bg_tasks.add_task(send_welcome_email, f"{author.username}@gmail.com")
    return author


@api_router.post('/users/send_telegram_message')
async def send_telegram_message_endpoint(chat_id: str, message: str, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(send_telegram_message, chat_id, message)
    return {"status": "Message sent"}

@api_router.post('/token', response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await db.scalar(select(Author).where(Author.username == form.username))
    if not user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi mavjud emas")

    if not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Username yoki parol noto'g'ri")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
 

@api_router.post('/users/me', response_model=AuthorOut)
async def get_current_user_profile(current_user: AuthorOut = Depends(get_current_user)):
    return current_user


@api_router.get('/users', response_model=List[AuthorOut])
async def get_authors(db: Session = Depends(get_db)):
    stmt = select(Author)
    result = db.scalars(stmt)
    authors = result.all()
    return authors

@api_router.delete('/users{author_id}')
async def delete_author(author_id:int, db:Session = Depends(get_db)):
    stmt = select(Author).where(Author.id == author_id)
    author = db.scalar(stmt)
    if not author:
        raise HTTPException(status_code=404, detail=f"{author_id} id li author mavjud emas")
    
    await db.delete(author)
    await db.commit()
    return "Muvaffaqiyatli o'chirildi"



@api_router.post('/',response_model=PostOut)
async def post_creat(post_in:PostCreate, db = Depends(get_db)):
    stmt  = select(Author).where(Author.id == post_in.author_id)
    author = await db.scalar(stmt)
    if not author:
        raise HTTPException(status_code=400,  detail=f"{post_in.author_id} li author mavud  emas")
    
    post  = Posts(**post_in.model_dump())

    db.add(post)
    await db.commit()
    await db.refresh(post)

    return post


@api_router.get('/', response_model=List[PostOut])
async def post_out(db = Depends(get_db)):
    stmt = select(Posts)
    result = await db.scalars(stmt)
    posts = result.all()
    return posts


@api_router.get('/{post_id}', response_model=PostOut)
async def get_post(post_id: int, db = Depends(get_db)):
    stmt = select(Posts).where(Posts.id == post_id)
    post = await db.scalar(stmt)

    if not post:
        raise HTTPException(status_code=404, detail=f"{post_id}-raqamli post mavjud emas")

    return post

@api_router.put('/{post_id}', response_model=PostOut)
async def update_post(post_id:int, post_in: PostUpdate, db = Depends(get_db),):
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


@api_router.delete('/{post_id}')
async def delete_post(post_id:int, db = Depends(get_db)):
    stmt = select(Posts).where(Posts.id == post_id)
    post = await db.scalar(stmt)
    if not post:
        raise HTTPException(status_code=404, detail=f'{post_id}-post mavjud emas')
    await db.delete(post)
    await db.commit()
    return {'status':404}

@api_router.post('/like/{post_id}', response_model=LikeOut)
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


@api_router.post('/comment/{post_id}', response_model=CommentOut)
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

@api_router.get('/comments/{post_id}', response_model=List[str])
async def get_comments(post_id:int, db = Depends(get_db)):
    stmt = select(Comment).where(Comment.post_id == post_id)
    comments = await db.scalars(stmt).all()
    return [comment.content for comment in comments]


@api_router.get('/likes/{post_id}', response_model=int)
async def get_likes(post_id:int, db = Depends(get_db)):
    stmt = select(Like).where(Like.post_id == post_id)
    likes = await db.scalars(stmt)
    return len(likes.all())