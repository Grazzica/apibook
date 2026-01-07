from sqlalchemy import Column, Integer, String, Float, DateTime
from api.database import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key= True, index=True)
    user_name = Column(String, unique=True, index=True)
    password_hash = Column(String)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key = True, index=True)
    book_title = Column(String)
    target = Column(String)
    prediction = Column(Float)
    user = Column(String)
    created_at = Column(DateTime)


