"""Entry point: uvicorn main:app"""

from insurer.app import create_app

app = create_app()
