from pydantic import BaseModel,ConfigDict,Field

class LoginRequest(BaseModel):
    email:str
    password:str

class UserResponse(BaseModel):
    id:int
    name:str
    email:str
    bio:str | None
    role:str

class UserCreate(BaseModel):
    name:str = Field(max_length=100)
    email:str = Field(max_length=255)
    bio: str | None = Field(default=None, max_length=500)
    password:str = Field(max_length=255)

class PostResponse(BaseModel):
    id:int
    title:str
    content:str
    user_id:int

class PostAndUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id:int
    title:str
    content:str
    user_id:int
    user: UserResponse

class PostCreate(BaseModel):
    title:str = Field(max_length=100)
    content:str = Field(max_length=300)

class Token(BaseModel):
    access_token: str
    token_type: str