"""Runnable API server entrypoint."""

from __future__ import annotations

import argparse

import uvicorn


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser for the backend API server."""

    parser = argparse.ArgumentParser(description="Run the pyDFT FastAPI backend server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", default=8000, type=int, help="Bind port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    return parser


def run() -> None:
    """CLI entrypoint used by the `pydft-api` script."""

    parser = build_parser()
    args = parser.parse_args()

    uvicorn.run(
        "pydft.core.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    run()
