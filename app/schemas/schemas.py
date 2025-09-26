# In your schemas.py file
from pydantic import BaseModel

class UserLogin(BaseModel):
    email: str
    password: str