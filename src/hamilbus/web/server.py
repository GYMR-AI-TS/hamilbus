from __future__ import annotations

import uvicorn

from .app import app


def run_server(host: str = "127.0.0.1", port: int = 3000) -> None:
    print(f"Starting Hamilbus local server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
