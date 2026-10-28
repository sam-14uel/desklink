"""Authentication for DeskLink MCP endpoints.

Provides a simple Bearer token verifier that can be extended to JWT, OAuth, etc.
"""

import secrets
from pathlib import Path
from typing import Optional

from mcp.server.auth.provider import AccessToken, TokenVerifier


class DeskLinkTokenVerifier(TokenVerifier):
    """Simple static Bearer token verifier for MVP.

    Designed so stronger authentication (JWT, machine approval, org tokens)
    can be plugged in later by subclassing or replacing this verifier.
    """

    def __init__(self, expected_token: str):
        self.expected_token = expected_token

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        if not token or token != self.expected_token:
            return None
        # Minimal AccessToken for MVP. Scopes can be expanded later.
        return AccessToken(
            token=token,
            client_id="desklink-local",
            scopes=["filesystem:read", "filesystem:write"],
            expires_at=None,
        )


def generate_token() -> str:
    """Generate a cryptographically strong random token."""
    return secrets.token_urlsafe(32)


def load_or_create_token(token_file: Optional[Path] = None, existing: Optional[str] = None) -> str:
    """Load token from file/env or generate a new one and optionally persist it."""
    if existing:
        return existing
    if token_file and token_file.exists():
        return token_file.read_text().strip()
    token = generate_token()
    if token_file:
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(token)
        token_file.chmod(0o600)
    return token
