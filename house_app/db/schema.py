from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserProfileSchema(BaseModel):
    id: int
    first_name: str
    username: str
    password: str
    phone_number: Optional[str]
    age: Optional[int]
    date_registered: datetime


class PredictSchema(BaseModel):
    total_live_area: int
    built_year: int
    garage_cars: int
    basement_area: int
    full_bath: int
    quality_level: int
    region: str
    price: int