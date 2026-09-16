from typing import Optional
from pydantic import BaseModel


class AlertItem(BaseModel):
    id: int
    type: str = "INFO"  # SUCCESS, INFO, WARNING, CRITICAL
    title: str
    message: str
    timestamp: str
    read: bool = False
