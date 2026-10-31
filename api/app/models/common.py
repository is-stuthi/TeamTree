from typing import Literal

from pydantic import BaseModel

Level = Literal["Beginner", "Intermediate", "Advanced", "Expert"]
Availability = Literal["Full-time", "Part-time", "Weekends", "Unavailable"]
AppRole = Literal["admin", "member"]


class Message(BaseModel):
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
