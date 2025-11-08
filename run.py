from fastapi import FastAPI
from dotenv import load_dotenv
import logging
from app.routes.env_routes import router as env_router
from app.routes.clients_route import router as clients_router
from app.routes.category_topic_route import router as category_topic_router

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Social Media AI Backend MVP")


# Register routes
app.include_router(env_router, prefix="/env", tags=["Environment Config"])
app.include_router(clients_router, prefix="/clients", tags=["Client Management"])
app.include_router(category_topic_router, tags=["Categories and Topics"])

@app.get("/")
def home():
    return {"message": "Social media AI system Backend is running 🚀"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)
