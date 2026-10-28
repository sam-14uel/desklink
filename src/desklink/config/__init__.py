from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class FilesystemConfig(BaseModel):
    """Configuration for filesystem access restrictions."""

    allowed_directories: List[Path] = Field(
        default_factory=lambda: [Path.home() / "Documents"],
        description="Directories the filesystem MCP server is allowed to access.",
    )
    read_only: bool = Field(default=False, description="If true, disable write operations.")

    @field_validator("allowed_directories", mode="before")
    @classmethod
    def expand_paths(cls, v):
        if isinstance(v, list):
            return [Path(p).expanduser().resolve() for p in v]
        return v


class TunnelConfig(BaseModel):
    """Tunnel provider configuration."""

    provider: str = Field(default="ngrok", description="Tunnel provider: ngrok, cloudflare, or none.")
    authtoken: Optional[str] = Field(default=None, description="ngrok authtoken (or NGROK_AUTHTOKEN env).")
    region: Optional[str] = Field(default=None, description="Preferred region for the tunnel.")


class AuthConfig(BaseModel):
    """Authentication configuration."""

    enabled: bool = Field(default=True, description="Require authentication on the remote endpoint.")
    token: Optional[str] = Field(default=None, description="Bearer token. Auto-generated if not set.")
    token_file: Optional[Path] = Field(default=None, description="File to persist the generated token.")


class ServerConfig(BaseModel):
    """Local MCP server configuration."""

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8765)
    mcp_path: str = Field(default="/mcp")


class DeskLinkConfig(BaseSettings):
    """Root DeskLink configuration loaded from file, env, and defaults."""

    model_config = SettingsConfigDict(
        env_prefix="DESKLINK_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    filesystem: FilesystemConfig = Field(default_factory=FilesystemConfig)
    tunnel: TunnelConfig = Field(default_factory=TunnelConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)

    config_file: Optional[Path] = Field(default=None, description="Path to YAML/TOML config file.")


def load_config(config_path: Optional[Path] = None) -> DeskLinkConfig:
    """Load configuration with sensible defaults and optional file override."""
    if config_path and config_path.exists():
        # For MVP we support env + programmatic; full YAML loading can be added later.
        # Placeholder for future file-based config.
        pass
    return DeskLinkConfig()
