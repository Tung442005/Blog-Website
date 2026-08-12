from pydantic import BaseModel, ConfigDict, Field

#pydantic use those datatype ot validate data at runtime

class PostBase(BaseModel):
    title: str  = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)

#when we create a post, we also want the title, the content and the author
class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    #this tell the Config can read data from objects with attribute not just dictionary --> used to read object from database
    model_config = ConfigDict(from_attributes=True)
    #Create field that generate by the system not by the client
    id: int
    date_posted: str