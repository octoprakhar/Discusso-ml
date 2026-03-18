from pydantic import BaseModel
from typing import Optional,List,Dict

class PostInput(BaseModel):
    title: str
    description: Optional[str] = None

class TagResponse(BaseModel):
    tags: List[str]
    error: Optional[str] = None

class TagRequest(BaseModel):
    post_id: str
    title: str
    description: Optional[str] = None

class PostRequest(BaseModel):
    postId:str
    title: str
    body: str
    karma: int