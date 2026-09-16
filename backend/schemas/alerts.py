from typing import Optional
from pydantic import BaseModel


class AlertItem(BaseModel):
    id: int
    type: str = "INFO"  # SUCCESS, INFO, WARNING, CRITICAL
    title: str
    message: str
    description: Optional[str] = None
    timestamp: str
    time: Optional[str] = None
    read: bool = False
    action: Optional[str] = None
    category: Optional[str] = "current"  # "current" or "upcoming"
    status: Optional[str] = "active"  # "active" or "resolved"
    color: Optional[str] = None
    bg: Optional[str] = None
    border: Optional[str] = None
    icon_name: Optional[str] = None

