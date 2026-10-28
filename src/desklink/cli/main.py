"""DeskLink CLI.

Primary command: desklink start
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from desklink import __version__
from desklink.auth import load_or_create_token
from desklink.config import DeskLinkConfig, load_config
from desklink.server import DeskLinkServer

app = typer.Typer(
    name="desklink",
    help="Turn your local computer into a remotely accessible MCP endpoint for cloud AI agents.",
    no_args_is_help=True,
)
console = Console()

# Global state for the running server (simple for MVP)
_current_server: DeskLinkServer | None = None


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@app.command()
def start(
    config_file: Path = typer.Option(
        None, "--config", "-c", help="Path to configuration file (YAML)."
    ),
    port: int = typer.Option(None, "--port", "-p", help="Local HTTP port."),
    host: str = typer.Option(None, "--host", help="Local bind host."),
    tunnel: str = typer.Option(None, "--tunnel", help="Tunnel provider: ngrok, none."),
    token: str = typer.Option(None, "--token", help="Bearer token (auto-generated if omitted)."),
    allowed_dir: list[str] = typer.Option(
        None, "--allow", help="Additional allowed directory (repeatable)."
    ),
    read_only: bool = typer.Option(False, "--read-only", help="Disable write tools."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging."),
) -> None:
    """Start DeskLink: local MCP server + secure tunnel."""
    setup_logging(verbose)

    # Load base config
    cfg = load_config(config_file)

    # Apply CLI overrides
    if port is not None:
        cfg.server.port = port
    if host is not None:
        cfg.server.host = host
    if tunnel is not None:
        cfg.tunnel.provider = tunnel
    if read_only:
        cfg.filesystem.read_only = True
    if allowed_dir:
        from pathlib import Path as P

        extra = [P(d).expanduser().resolve() for d in allowed_dir]
        cfg.filesystem.allowed_directories.extend(extra)

    # Auth token
    token_file = Path.home() / ".desklink" / "token"
    cfg.auth.token = load_or_create_token(token_file, existing=token or os.getenv("DESKLINK_TOKEN"))
    cfg.auth.enabled = True

    # ngrok token from env if not set
    if cfg.tunnel.provider == "ngrok" and not cfg.tunnel.authtoken:
        cfg.tunnel.authtoken = os.getenv("NGROK_AUTHTOKEN")

    server = DeskLinkServer(cfg)
    global _current_server
    _current_server = server

    # Print banner
    console.print(Panel.fit(
        f"[bold cyan]DeskLink[/] v{__version__}",
        border_style="cyan",
    ))

    async def _run():
        # Start and display
        local = await server.start_http_server()
        public = server.start_tunnel()

        # Ensure tools count is populated
        if server.filesystem_mcp:
            try:
                tools = server.filesystem_mcp.list_tools()
                server.status.tools_count = len(list(tools))
            except Exception:
                server.status.tools_count = 5

        console.print("[green]✓[/] Filesystem MCP started")
        console.print(f"[green]✓[/] Local MCP: [link={local}]{local}[/]")
        console.print("[green]✓[/] Tunnel connected")
        console.print()
        console.print("[bold]Remote MCP endpoint:[/]")
        console.print(f"[bold green]{public}[/]")
        console.print()
        if cfg.auth.enabled:
            console.print(f"[yellow]Auth token:[/] {cfg.auth.token}")
            console.print("[dim]Include as Authorization: Bearer <token> when connecting.[/]")
        console.print()
        console.print("[bold]Status:[/] ● Connected")
        console.print(f"[bold]Tools:[/] {server.status.tools_count}")
        console.print(f"[bold]Allowed dirs:[/] {len(cfg.filesystem.allowed_directories)}")
        console.print()
        console.print("[dim]Press Ctrl+C to stop.[/]")

        # Handle signals
        loop = asyncio.get_event_loop()

        def _signal_handler():
            console.print("\n[yellow]Stopping DeskLink...[/]")
            server.request_shutdown()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _signal_handler)
            except NotImplementedError:
                # Windows
                signal.signal(sig, lambda *_: _signal_handler())

        await server._shutdown_event.wait()

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/]")
    finally:
        if _current_server:
            asyncio.run(_current_server.shutdown())
        console.print("[green]DeskLink stopped.[/]")


@app.command()
def stop() -> None:
    """Stop a running DeskLink process (best-effort; prefer Ctrl+C)."""
    console.print("[yellow]Use Ctrl+C in the running terminal to stop DeskLink.[/]")
    console.print("[dim]Process management will be improved in a future release.[/]")


@app.command()
def status() -> None:
    """Show status of DeskLink (placeholder for MVP)."""
    console.print("[dim]Status command will report running instances in a future release.[/]")
    console.print("For now, check the terminal where you ran [bold]desklink start[/].")


@app.command()
def config(
    show: bool = typer.Option(True, "--show/--no-show", help="Show current effective config."),
) -> None:
    """Manage DeskLink configuration."""
    cfg = load_config()
    console.print("[bold]DeskLink Configuration[/]")
    console.print(f"Server: {cfg.server.host}:{cfg.server.port}{cfg.server.mcp_path}")
    console.print(f"Tunnel: {cfg.tunnel.provider}")
    console.print(f"Auth enabled: {cfg.auth.enabled}")
    console.print("Allowed directories:")
    for d in cfg.filesystem.allowed_directories:
        console.print(f"  - {d}")
    console.print("\n[dim]Set DESKLINK_* environment variables or use CLI flags to override.[/]")


@app.command()
def version() -> None:
    """Show version."""
    console.print(f"DeskLink {__version__}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
