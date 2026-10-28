from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class TunnelInfo(BaseModel):
    """Information about an established tunnel."""

    provider: str
    public_url: str
    local_url: str
    tunnel_id: Optional[str] = None


class ServerStatus(BaseModel):
    """Runtime status of DeskLink."""

    running: bool = False
    local_url: Optional[str] = None
    public_url: Optional[str] = None
    tools_count: int = 0
    auth_enabled: bool = True
    allowed_directories: list[Path] = []
