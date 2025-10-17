from typing import Optional, Literal
from pydantic import BaseModel, EmailStr
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass



class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class PostResponse(PostBase):
    id: int
    owner_id: int
    owner: UserResponse
    created_at: datetime

    class Config:
        from_attributes = True


class PostWithVote(BaseModel):
    post: PostResponse
    vote_count: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: Literal["0", "1"]