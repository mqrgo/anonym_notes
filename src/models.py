from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Note(Base):
    __tablename__ = 'note'

    id = Column(Integer, primary_key=True)
    note = Column(String(), nullable=False)


metadata = Base.metadata

