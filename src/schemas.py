from fastapi import Query
from pydantic import BaseModel, EmailStr
from typing import Annotated


class NoteData(BaseModel):
    note: Annotated[str, Query(max_length=100)]
    email: EmailStr
    
