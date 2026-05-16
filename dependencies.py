from database import get_db
from models import Author
import security
import jwt

from fastapi.params import Depends
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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


def role_check(*allowed_roles):
    def role_checker(current_user: Author = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Ruxsat etilmagan")
        return current_user
    return role_checker