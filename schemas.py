import pydantic as pyd
import datetime as dt

class UserBase(pyd.BaseModel):
    email: str
    name: str
    phone: str

class UserRequest(UserBase):
    password_hash: str

    class Config:
        orm_mode = True

class UserResponse(UserBase):
    id: int
    created_at: dt.datetime

    class Config:
        orm_mode = True

class PostBase(pyd.BaseModel):
    post_title: str
    post_description: str
    post_image: str

class PostRequest(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    user_id: int
    created_at: dt.datetime

    class Config:
        orm_mode = True