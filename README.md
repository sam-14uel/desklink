# DeskLink

Turn your local computer into a remotely accessible **MCP endpoint** for cloud AI agents.

DeskLink runs a secure local filesystem MCP server (Streamable HTTP) and exposes it through a temporary public tunnel (ngrok by default) so tools like Grok, Claude, or Cursor can access permitted directories on your machine.

## Quick start

```bash
pip install desklink
# Optional: export NGROK_AUTHTOKEN=your_token   # required for free ngrok
desklink start
```

Example output:

```
DeskLink v0.1.0

✓ Filesystem MCP started
✓ Local MCP: http://127.0.0.1:8765/mcp
✓ Tunnel connected

Remote MCP endpoint:
https://abc123.ngrok-free.app/mcp

Auth token: sk-desklink-...
Include as Authorization: Bearer <token> when connecting.

Status: ● Connected
Tools: 5
Allowed dirs: 1

Press Ctrl+C to stop.
```

Connect the remote URL + bearer token from your AI client.

## Installation

```bash
pip install desklink
# or for development
uv pip install -e ".[dev]"
```

Requires Python 3.10+.

## Configuration

DeskLink uses sensible defaults and can be overridden via environment variables (`DESKLINK_*`) or CLI flags.

Default allowed directory: `~/Documents`.

```bash
desklink start --allow ~/projects --allow /tmp/workspace --read-only
desklink start --port 9000 --tunnel none   # local only
```

Persistent token is stored at `~/.desklink/token` (mode 0600).

## Security

- Bearer token authentication is **enabled by default**.
- Filesystem access is restricted to explicitly allowed directories.
- Relative paths are resolved against the first allowed directory.
- Path traversal outside allowed roots is rejected.
- The public tunnel URL alone does **not** grant access; the token is required.

Future versions will support JWT, machine approval, organization tokens, and a cloud relay.

## Architecture

Modular by design:

- `cli` – Typer CLI
- `server` – HTTP + lifecycle
- `filesystem` – restricted filesystem tools
- `tunnel` – pluggable providers (ngrok, none, future Cloudflare / DeskLink relay)
- `auth` – token verification (extensible)
- `config` / `models` – typed configuration

Additional MCP servers (terminal, browser, git, docker, etc.) can be added later and composed behind the same endpoint.

## Development

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
```

## License

MIT
