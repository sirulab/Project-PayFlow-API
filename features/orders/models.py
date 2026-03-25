from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int
    status: str = "pending"
    amount: int
    created_at: datetime = Field(default_factory=datetime.utcnow)