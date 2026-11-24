import socket
import sys
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from retailer.app import create_app  # noqa: E402

KEY = "test-key-123"
TODAY = "2026-11-24"
SYSTEMS = ["stores", "foodsafety", "care", "purchasing", "property", "performance", "tills", "orders",
           "catalogue", "stock", "pricing", "loyalty", "people", "franchise"]
ALL_SYSTEMS = SYSTEMS
H = {"X-API-Key": KEY}


def make_env(**extra):
    env = {"RETAILER_API_KEY": KEY, "RETAILER_TODAY": TODAY}
    env.update(extra)
    return env


@pytest.fixture()
def app():
    return create_app(make_env())


@pytest.fixture()
def client(app):
    return TestClient(app)


@pytest.fixture()
def store(app):
    return app.state.ctx.store


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    """A real server on a free port, for the MCP client tests."""
    app = create_app(make_env())
    port = free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(5)
