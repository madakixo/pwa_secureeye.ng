from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str

class PaymentVerify(BaseModel):
    reference: str

class CameraCreate(BaseModel):
    camera_url: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    active: bool

    class Config:
        from_attributes = True
