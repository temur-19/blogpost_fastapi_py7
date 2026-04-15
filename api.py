import  security
import jwt

from fastapi import APIRouter, Depends, HTTPException,  status
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from schemas import PostOut,PostCreate, PostUpdate, AuthorCreate,AuthorOut,Token
from database import Base, engine,get_db
from models import Posts,Author


Base.metadata.create_all(bind=engine)
api_router = APIRouter(prefix='/api/posts')


oauth2_schema = OAuth2PasswordBearer(tokenUrl='login')

def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
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

    author = db.scalar(select(Author).where(Author.id == int(author_id)))
    if author is None:
        raise credentials_exception

    return author


@api_router.post('/users',response_model=AuthorOut)
def author_creat(author_in:AuthorCreate, db:Session = Depends(get_db)):
    author = db.scalar(select(Author).where(Author.first_name == author_in.first_name, Author.last_name == author_in.last_name))
    if author:
        raise HTTPException(status_code=404, detail='Bunday foydalanubchi mavjud')
    
    author = Author(
    username=author_in.username,
    first_name=author_in.first_name,
    last_name=author_in.last_name,
    hashed_password=security.get_password_hash(author_in.password))

    db.add(author)
    db.commit()
    db.refresh(author)
    return author

@api_router.post('/au/login', response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(Author).where(Author.username == form.username))
    if not user:
        raise HTTPException(status_code=400, detail="Bunday foydalanuvchi mavjud emas")

    if not security.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Username yoki parol noto'g'ri")

    access_token = security.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@api_router.post('/users/me', response_model=AuthorOut)
def get_current_user_profile(current_user: AuthorOut = Depends(get_current_user)):
    return current_user


@api_router.get('/users', response_model=List[AuthorOut])
def get_authors(db: Session = Depends(get_db)):
    stmt = select(Author)
    authors = db.scalars(stmt).all()
    return authors

@api_router.delete('/users{author_id}')
def delete_author(author_id:int, db:Session = Depends(get_db)):
    stmt = select(Author).where(Author.id == author_id)
    author = db.scalar(stmt)
    if not author:
        raise HTTPException(status_code=404, detail=f"{author_id} id li author mavjud emas")
    
    db.delete(author)
    db.commit()
    return "Muvaffaqiyatli o'chirildi"



@api_router.post('/',response_model=PostOut)
def post_creat(post_in:PostCreate, db = Depends(get_db)):
    stmt  = select(Author).where(Author.id == post_in.author_id)
    author = db.scalar(stmt)
    if not author:
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