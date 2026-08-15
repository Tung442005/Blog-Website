from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr


#pydantic use those datatype ot validate data at runtime
#BaseModel
class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    #pydantic EamilStr automatically validate the proper email format for us  
    email: EmailStr = Field(max_length=120)

#Create Model
class UserCreate(UserBase):
    pass 

#Reposne Model
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id : int
    image_file: str | None
    image_path: str

class UserUpdate(BaseModel):
    username: str | None = Field(default= None, min_length=1, max_length=50)
    #pydantic EamilStr automatically validate the proper email format for us  
    email: EmailStr | None = Field(default=None, max_length=120)

    #Only lets user change which filename is referenced as their profile picture
    #No need full path because the image_path property within model.py has already build the full path
    image_file: str | None = Field(default=None, min_length=1, max_length=200)


class PostBase(BaseModel):
    title: str  = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


#when we create a post, we want this class for what we accept when they are created 
class PostCreate(PostBase):
    user_id: int #Temporary --> will get the user directly from session  


#For PATCH method
class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default= None, min_length=1)

class PostResponse(PostBase):
    """this tell the Config can read data from objects with attribute not just dictionary by default
    --> used for pydantic to read object from database
    """
    model_config = ConfigDict(from_attributes=True)
    #Create field that generate by the server not by the client
    id: int
    user_id: int #foreign key
    date_posted: datetime
    #The frontend gets everything it needs to render "post + author card" from a single GET /api/posts call.
    author: UserResponse #embeds the entire related user object's attribtes all in one response