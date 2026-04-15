from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import String, Integer, ForeignKey


from database import Base


class Author(Base):
    __tablename__ = 'author'
    id :Mapped[int] = mapped_column(Integer,primary_key=True)
    username:Mapped[str] = mapped_column(String(length=100))
    first_name:Mapped[str] = mapped_column(String(length=100),nullable=False)
    last_name:Mapped[str] = mapped_column(String(length=100),nullable=False)
    post:Mapped['Posts'] = relationship(back_populates='auth',cascade='all, delete-orphan')
    hashed_password: Mapped[str] = mapped_column(String(length=200))

  
class Posts(Base):
    __tablename__ = 'posts'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String(length=50))
    content:Mapped[str] = mapped_column(String)
    author_id:Mapped[int] = mapped_column(ForeignKey('author.id'))
    auth:Mapped[Author] = relationship(back_populates='post')
