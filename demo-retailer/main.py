"""Entry point: uvicorn main:app"""

from retailer.app import create_app

app = create_app()
