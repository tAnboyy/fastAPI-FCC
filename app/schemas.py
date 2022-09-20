from pydantic import BaseModel

class Post(BaseModel):
    title: str
    content: str
    published: bool = True  # defaults to true ie optional field for user
    # rating: Optional[int] = None

# class CreatePost(BaseModel):
#     title: str
#     content: str
#     published: bool = True

# class UpdatePost(BaseModel):
#     title: str
#     content: str
#     published: bool

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass