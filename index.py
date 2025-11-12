from fastapi import FastAPI
from dotenv import load_dotenv
import logging
from app.routes.env_routes import router as env_router
from app.routes.clients_route import router as clients_router
from app.routes.category_topic_route import router as category_topic_router
from app.routes.image_route import router as image_router
from app.routes.post_route import router as post_router
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum



load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Social Media AI Backend MVP")

# Allow all origins (or you can restrict to Loveable’s URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <- "*" allows any origin
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, DELETE, etc.
    allow_headers=["*"],   # Allows all headers
)


# Register routes
app.include_router(env_router, prefix="/env", tags=["Environment Config"])
app.include_router(clients_router, prefix="/clients", tags=["Client Management"])
app.include_router(category_topic_router, tags=["Categories and Topics"])
app.include_router(image_router, prefix="/images", tags=["Image Management"])
app.include_router(post_router, prefix="/posts", tags=["Post Creation"])


@app.get("/")
def home():
    return {"message": "Social media AI system Backend is running 🚀"}


handler = Mangum(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)