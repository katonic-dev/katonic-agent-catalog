"""Entry point: uvicorn main:app"""

from bank.app import create_app

app = create_app()
