from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer


from database import Base

class Posts(Base):
    __tablename__ = 'posts'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    author:Mapped[str] = 'Temur'    
    title:Mapped[str] = mapped_column(String(length=50))
    content:Mapped[str] = mapped_column(String)
    image_path:Mapped[str] = mapped_column(String(250), nullable=True)







