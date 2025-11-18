import uvicorn
from app.core.setup import create_app
from app.core.config import settings

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=settings.API_HOST, 
        port=settings.API_PORT
    )