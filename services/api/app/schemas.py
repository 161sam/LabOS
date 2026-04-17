from datetime import date
from typing import Optional

from pydantic import BaseModel


class ChargeCreate(BaseModel):
    name: str
    species: str
    status: str = 'planned'
    volume_l: float = 1.0
    reactor_id: Optional[int] = None
    start_date: Optional[date] = None
    notes: Optional[str] = None


class ReactorCreate(BaseModel):
    name: str
    reactor_type: str
    status: str = 'online'
    volume_l: float = 1.0
    location: Optional[str] = None
