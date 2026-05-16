import security
import shutil

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from fastapi import Depends, HTTPException, status, APIRouter, BackgroundTasks,UploadFile,File
from fastapi.security import  OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
from email_servis import send_welcome_email, send_telegram_message


from schemas.users import AuthorCreate, AuthorOut, Token
from database import get_db
from dependencies import get_current_user
from models import Author


user_router = APIRouter(prefix='/api/users')

oauth2_schema = OAuth2PasswordBearer(tokenUrl="api/users/token")


@user_router.post('/upload_avatar/')
async def upload_avatar(file: UploadFile = File(...),
                        current_user: AuthorOut = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    from config import UPLOAD_FOLDER
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

@user_router.post('/register/',response_model=AuthorOut)
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


@user_router.post('/send_telegram_message/')
async def send_telegram_message_endpoint(chat_id: str, message: str, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(send_telegram_message, chat_id, message)
    return {"status": "Message sent"}

@user_router.post('/token/', response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await db.scalar(select(Author).where(Author.username == form.username))
    if not user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi mavjud emas")

    if not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Username yoki parol noto'g'ri")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
 

@user_router.post('/me/', response_model=AuthorOut)
async def get_current_user_profile(current_user: AuthorOut = Depends(get_current_user)):
    return current_user


@user_router.get('/authors/')
async def get_authors(db: Session = Depends(get_db)):
    stmt = select(Author)
    result = await db.scalars(stmt)
    authors = result.all()
    return authors

@user_router.delete('/delete_author/{author_id}')
async def delete_author(author_id:int, db:Session = Depends(get_db)):
    stmt = select(Author).where(Author.id == author_id)
    author = await db.scalar(stmt)
    if not author:
        raise HTTPException(status_code=404, detail=f"{author_id} id li author mavjud emas")
    
    await db.delete(author)
    await db.commit()
    return "Muvaffaqiyatli o'chirildi"
