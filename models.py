from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import String, Integer, ForeignKey
from typing import List


from database import Base


class Author(Base):
    __tablename__ = 'author'
    id :Mapped[int] = mapped_column(Integer,primary_key=True)
    username:Mapped[str] = mapped_column(String(length=100))
    first_name:Mapped[str] = mapped_column(String(length=100),nullable=False)
    last_name:Mapped[str] = mapped_column(String(length=100),nullable=False)
    post:Mapped[List['Posts']] = relationship(back_populates='auth',cascade='all, delete-orphan')
    hashed_password: Mapped[str] = mapped_column(String(length=200))
    phone_number: Mapped[str] = mapped_column(String(length=20), nullable=True)
    gender: Mapped[str] = mapped_column(String(length=10), nullable=True)
    comment:Mapped[List['Comment']] = relationship(back_populates='auth', cascade='all, delete-orphan')
    like:Mapped[List[   'Like']] = relationship(back_populates='auth', cascade='all, delete-orphan')

class Posts(Base):
    __tablename__ = 'posts'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String(length=50))
    content:Mapped[str] = mapped_column(String)
    author_id:Mapped[int] = mapped_column(ForeignKey('author.id'))
    auth:Mapped[Author] = relationship(back_populates='post')
    like:Mapped[List['Like']] = relationship(back_populates='post', cascade='all, delete-orphan')
    comment:Mapped[List['Comment']] = relationship(back_populates='post', cascade='all, delete-orphan')



class Comment(Base):
    __tablename__ = 'comments'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    content:Mapped[str] = mapped_column(String)
    post_id:Mapped[int] = mapped_column(ForeignKey('posts.id'))
    author_id:Mapped[int] = mapped_column(ForeignKey('author.id'))
    auth:Mapped[Author] = relationship(back_populates='comment')
    post:Mapped[Posts] = relationship(back_populates='comment')



class Like(Base):
    __tablename__ = 'likes'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id:Mapped[int] = mapped_column(ForeignKey('posts.id'))
    author_id:Mapped[int] = mapped_column(ForeignKey('author.id'))
    auth:Mapped[Author] = relationship(back_populates='like')
    post:Mapped[Posts] = relationship(back_populates='like')
