
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


#expectation (control)from users what to send: for example,  title, content str
class PostBase (BaseModel):
    title : str
    content: str
    published: bool = True
   

class PostCreate (PostBase):
    pass

class PostUpdate (PostBase):
    pass


#controlling the response

class Post (PostBase): # inherite from PostBase
    id : int
    created_at: datetime
 
  
   